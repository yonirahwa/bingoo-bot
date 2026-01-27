from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import GameRoom, GameParticipant, User, BingoCard, CalledNumber
from schemas import GameRoomResponse, GameParticipantResponse, JoinGameRequest, BingoCardResponse
from game_logic import BingoCardGenerator, BingoGameLogic
from typing import List
from datetime import datetime, timedelta
import asyncio
from websocket_manager import manager

router = APIRouter(prefix="/api/games", tags=["games"])

# Store active game logic instances
active_games: dict = {}

@router.get("/rooms", response_model=List[GameRoomResponse])
async def get_game_rooms(db: Session = Depends(get_db)):
    """Get all available game rooms"""
    rooms = db.query(GameRoom).filter(GameRoom.status.in_(["waiting", "starting"])).all()
    return rooms

@router.get("/my-cards", response_model=List[BingoCardResponse])
async def get_my_cards(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get user's generated bingo cards"""
    cards = db.query(BingoCard).filter(BingoCard.user_id == user_id).all()
    return cards

@router.post("/generate-cards")
async def generate_cards(
    user_id: int = Query(...),
    count: int = Query(2, le=10),
    db: Session = Depends(get_db)
):
    """Generate new bingo cards for user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cards_data = BingoCardGenerator.generate_multiple_cards(count)
    
    saved_cards = []
    for card_data in cards_data:
        card = BingoCard(user_id=user_id, numbers=card_data)
        db.add(card)
        db.flush()
        saved_cards.append(card)
    
    db.commit()
    return {
        "message": f"Generated {count} cards",
        "cards": [{"id": c.id, "numbers": c.numbers} for c in saved_cards]
    }

@router.post("/join-game")
async def join_game(
    user_id: int = Query(...),
    room_id: int = Query(...),
    card_ids: List[int] = Query(...),
    db: Session = Depends(get_db)
):
    """Join a game room"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    room = db.query(GameRoom).filter(GameRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.current_players >= room.max_players:
        raise HTTPException(status_code=400, detail="Room is full")
    
    # Check if user already in room
    existing = db.query(GameParticipant).filter(
        GameParticipant.user_id == user_id,
        GameParticipant.room_id == room_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already in this game")
    
    # Deduct stake from user balance
    if user.balance < room.stake_amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    user.balance -= room.stake_amount
    
    # Create participant
    participant = GameParticipant(
        user_id=user_id,
        room_id=room_id,
        card_numbers=card_ids,
        cards_marked={}
    )
    db.add(participant)
    room.current_players += 1
    db.commit()
    db.refresh(participant)
    
    # Broadcast to room
    await manager.broadcast_to_room(room_id, {
        "type": "player_joined",
        "player_count": room.current_players,
        "user": {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name
        }
    })
    
    return participant

@router.post("/start-game/{room_id}")
async def start_game(
    room_id: int,
    db: Session = Depends(get_db)
):
    """Start a game (after timer)"""
    room = db.query(GameRoom).filter(GameRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room.status = "starting"
    room.start_time = datetime.utcnow()
    db.commit()
    
    # Initialize game logic
    active_games[room_id] = BingoGameLogic()
    
    # Broadcast game started
    await manager.broadcast_to_room(room_id, {
        "type": "game_started",
        "message": "Game is starting!"
    })
    
    # Schedule first number call in 3 seconds
    asyncio.create_task(call_numbers_loop(room_id, db))
    
    return {"status": "Game started"}

async def call_numbers_loop(room_id: int, db: Session):
    """Call numbers with 3 second delay"""
    from config import settings
    
    game = active_games.get(room_id)
    if not game:
        return
    
    db.query(GameRoom).filter(GameRoom.id == room_id).update({"status": "running"})
    db.commit()
    
    while len(game.called_numbers) < 75:
        await asyncio.sleep(settings.NUMBER_CALL_DELAY)
        
        number, letter = game.call_next_number()
        
        if number == -1:
            break
        
        # Save to database
        called = CalledNumber(room_id=room_id, number=number)
        db.add(called)
        db.commit()
        
        # Broadcast to room
        await manager.broadcast_to_room(room_id, {
            "type": "number_called",
            "number": number,
            "letter": letter,
            "total_called": len(game.called_numbers)
        })

@router.post("/mark-number")
async def mark_number(
    user_id: int = Query(...),
    room_id: int = Query(...),
    number: int = Query(...),
    card_index: int = Query(...),
    db: Session = Depends(get_db)
):
    """Mark a number on player's card"""
    participant = db.query(GameParticipant).filter(
        GameParticipant.user_id == user_id,
        GameParticipant.room_id == room_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    if not participant.cards_marked:
        participant.cards_marked = {}
    
    card_id = participant.card_numbers[card_index]
    if str(card_id) not in participant.cards_marked:
        participant.cards_marked[str(card_id)] = []
    
    if number not in participant.cards_marked[str(card_id)]:
        participant.cards_marked[str(card_id)].append(number)
    
    db.commit()
    
    return {"status": "Number marked"}

@router.post("/check-win")
async def check_win(
    user_id: int = Query(...),
    room_id: int = Query(...),
    card_index: int = Query(...),
    db: Session = Depends(get_db)
):
    """Check if player has won"""
    participant = db.query(GameParticipant).filter(
        GameParticipant.user_id == user_id,
        GameParticipant.room_id == room_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    card = db.query(BingoCard).filter(
        BingoCard.id == participant.card_numbers[card_index]
    ).first()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Build marked positions
    marked_numbers = participant.cards_marked.get(str(card.id), [])
    marked_positions = [
        [card.numbers[i][j] == 0 or card.numbers[i][j] in marked_numbers for j in range(5)]
        for i in range(5)
    ]
    
    game = active_games.get(room_id)
    if not game:
        raise HTTPException(status_code=400, detail="Game not active")
    
    has_won, pattern = game.check_win(card.numbers, marked_positions)
    
    if has_won and participant.status == "playing":
        participant.status = "won"
        room = db.query(GameRoom).filter(GameRoom.id == room_id).first()
        
        # Add winnings to user balance
        user = db.query(User).filter(User.id == user_id).first()
        pot = room.stake_amount * room.current_players
        user.balance += pot
        
        db.commit()
        
        # Broadcast winner
        await manager.broadcast_to_room(room_id, {
            "type": "player_won",
            "user_id": user_id,
            "username": user.username,
            "pattern": pattern,
            "winning_amount": pot
        })
    
    return {
        "has_won": has_won,
        "pattern": pattern,
        "status": participant.status
    }
