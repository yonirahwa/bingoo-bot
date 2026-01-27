from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: str = "en"

class UserCreate(UserBase):
    telegram_id: str

class UserUpdate(BaseModel):
    photo_url: Optional[str] = None
    language: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    telegram_id: str
    balance: float
    bonus_balance: float
    photo_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class GameRoomResponse(BaseModel):
    id: int
    name: str
    stake_amount: float
    max_players: int
    current_players: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class BingoCardResponse(BaseModel):
    id: int
    numbers: List[List[int]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class GameParticipantResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    status: str
    card_numbers: Optional[List[int]]
    joined_at: datetime
    
    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    method: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DepositRequest(BaseModel):
    method: str  # telbirr, cbe, bank
    amount: float
    phone_or_account: str

class WithdrawRequest(BaseModel):
    amount: float
    method: str
    account_info: dict

class TransferRequest(BaseModel):
    recipient_id: int
    amount: float

class JoinGameRequest(BaseModel):
    room_id: int
    card_ids: List[int]  # Selected 1-2 cards

class MarkNumberRequest(BaseModel):
    participant_id: int
    number: int
    card_index: int
