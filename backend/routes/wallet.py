from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, Transaction, TransactionType, Wallet
from backend.schemas import DepositRequest, WithdrawRequest, TransferRequest, TransactionResponse
from typing import List
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/wallet", tags=["wallet"])

@router.get("/balance")
async def get_balance(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get user balance"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "balance": user.balance,
        "bonus_balance": user.bonus_balance,
        "total": user.balance + user.bonus_balance
    }

@router.post("/deposit")
async def deposit(
    request: DepositRequest,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):

    """Initiate deposit"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transaction = Transaction(
        user_id=user_id,
        type=TransactionType.DEPOSIT,
        amount=request.amount,
        method=request.method,
        status="pending",
        transaction_id=str(uuid.uuid4()),
        description=f"Deposit via {request.method}"
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return {
        "transaction_id": transaction.transaction_id,
        "status": "pending",
        "amount": request.amount,
        "method": request.method,
        "message": f"Deposit initiated. Please send {request.amount} to {request.method}"
    }

@router.post("/withdraw")
async def withdraw(
    request: WithdrawRequest,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Initiate withdrawal"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    transaction = Transaction(
        user_id=user_id,
        type=TransactionType.WITHDRAW,
        amount=request.amount,
        method=request.method,
        status="pending",
        transaction_id=str(uuid.uuid4()),
        description=f"Withdrawal via {request.method}"
    )
    db.add(transaction)
    
    # Store wallet info
    wallet = Wallet(
        user_id=user_id,
        method=request.method,
        account_info=request.account_info
    )
    db.add(wallet)
    
    db.commit()
    db.refresh(transaction)
    
    return {
        "transaction_id": transaction.transaction_id,
        "status": "pending",
        "amount": request.amount,
        "message": "Withdrawal request submitted. Please allow up to 30 minutes for processing."
    }

@router.post("/transfer")
async def transfer(
    request: TransferRequest,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):

    """Transfer funds to another user"""
    sender = db.query(User).filter(User.id == user_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    recipient = db.query(User).filter(User.id == request.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    if sender.balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Deduct from sender
    sender.balance -= request.amount
    
    # Add to recipient
    recipient.balance += request.amount
    
    # Create transaction records
    transaction = Transaction(
        user_id=user_id,
        type=TransactionType.TRANSFER,
        amount=request.amount,
        method="internal",
        status="completed",
        transaction_id=str(uuid.uuid4()),
        description=f"Transfer to {recipient.username or recipient.first_name}"
    )
    db.add(transaction)
    db.commit()
    
    return {
        "status": "completed",
        "amount": request.amount,
        "recipient": recipient.username,
        "message": "Transfer successful"
    }

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    user_id: int = Query(...),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Get user transaction history"""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.created_at.desc()).limit(limit).all()
    
    return transactions


