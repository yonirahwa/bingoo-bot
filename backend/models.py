from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
from datetime import datetime
import enum

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    language = Column(String, default="en")
    balance = Column(Float, default=0.0)
    bonus_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    game_participants = relationship("GameParticipant", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    wallets = relationship("Wallet", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class GameRoom(Base):
    __tablename__ = "game_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    stake_amount = Column(Float)
    max_players = Column(Integer, default=100)
    current_players = Column(Integer, default=0)
    status = Column(String, default="waiting")  # waiting, starting, running, finished
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    participants = relationship("GameParticipant", back_populates="room")
    called_numbers = relationship("CalledNumber", back_populates="room")
    
    def __repr__(self):
        return f"<GameRoom {self.name}>"


class GameParticipant(Base):
    __tablename__ = "game_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("game_rooms.id"))
    card_numbers = Column(JSON)  # Store selected card IDs
    status = Column(String, default="playing")  # playing, won, lost
    cards_marked = Column(JSON, default={})  # {card_id: [marked_numbers]}
    joined_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="game_participants")
    room = relationship("GameRoom", back_populates="participants")
    
    def __repr__(self):
        return f"<GameParticipant user_id={self.user_id} room_id={self.room_id}>"


class BingoCard(Base):
    __tablename__ = "bingo_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    numbers = Column(JSON)  # Store 5x5 grid of numbers
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<BingoCard id={self.id}>"


class CalledNumber(Base):
    __tablename__ = "called_numbers"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("game_rooms.id"))
    number = Column(Integer)
    called_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    room = relationship("GameRoom", back_populates="called_numbers")


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"
    GAME_WIN = "game_win"
    GAME_LOSS = "game_loss"


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(TransactionType))
    amount = Column(Float)
    method = Column(String)  # telbirr, cbe, bank, internal
    status = Column(String, default="pending")  # pending, completed, failed
    transaction_id = Column(String, nullable=True, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    method = Column(String)  # telbirr, cbe, bank
    account_info = Column(JSON)  # {phone: xxx, account: xxx}
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wallets")

