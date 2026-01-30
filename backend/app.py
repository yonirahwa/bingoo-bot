# app.py
from fastapi import FastAPI, Request
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import os

# ---------------- Database Setup ----------------
DATABASE_URL = "sqlite:///./test.db"  # for testing, change to your database

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    first_name = Column(String)  # <-- fixed name issue
    phone = Column(String)

Base.metadata.create_all(bind=engine)

# ---------------- Bot Setup ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN_HERE"
bot = Bot(token=BOT_TOKEN)

# ---------------- FastAPI Setup ----------------
app = FastAPI()

# ---------------- Helper Functions ----------------
def register_user(telegram_id, first_name, phone=None):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    if existing_user:
        db.close()
        return existing_user

    user = User(telegram_id=str(telegram_id), first_name=first_name, phone=phone)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def is_registered(telegram_id):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    db.close()
    return user is not None

# ---------------- Webhook ----------------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name

    # ---------------- Start command ----------------
    if update.message and update.message.text == "/start":
        keyboard = [
            [InlineKeyboardButton("Register", callback_data="register")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=chat_id, text=f"Welcome {first_name}! Please register first.", reply_markup=reply_markup)
        return {"ok": True}

    # ---------------- Handle button callbacks ----------------
    if update.callback_query:
        query = update.callback_query
        data = query.data

        if data == "register":
            # Ask for contact
            contact_button = KeyboardButton(text="Share Contact", request_contact=True)
            markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)
            bot.send_message(chat_id=chat_id, text="Please share your contact to register:", reply_markup=markup)
            return {"ok": True}

        if data == "play":
            keyboard = [
                [InlineKeyboardButton("Start Game", callback_data="start_game")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id=chat_id, text="Click to start the game!", reply_markup=reply_markup)
            return {"ok": True}

        if data == "start_game":
            bot.send_message(chat_id=chat_id, text="Game started! 🎮")
            return {"ok": True}

    # ---------------- Handle contact registration ----------------
    if update.message and update.message.contact:
        phone_number = update.message.contact.phone_number
        user = register_user(chat_id, first_name, phone_number)

        # After successful registration, show Play button
        keyboard = [
            [InlineKeyboardButton("Play", callback_data="play")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=chat_id, text="Registration successful! Click Play to continue.", reply_markup=reply_markup)
        return {"ok": True}

    return {"ok": True}
