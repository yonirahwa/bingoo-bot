from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.database import Base, engine, SessionLocal
from backend.models import User  # Make sure you have User model
from backend.routes import auth, games, wallet, profile, websocket
import os
import requests

# ------------------------------
# Bot configuration
# ------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ------------------------------
# FastAPI app
# ------------------------------
app = FastAPI(
    title="Bingo Bot API",
    description="Web-based Bingo Game for Telegram",
    version="1.0.0"
)

# ------------------------------
# Middleware
# ------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Static files
# ------------------------------
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ------------------------------
# Include routers
# ------------------------------
app.include_router(auth.router)
app.include_router(games.router)
app.include_router(wallet.router)
app.include_router(profile.router)
app.include_router(websocket.router)

# ------------------------------
# Database
# ------------------------------
Base.metadata.create_all(bind=engine)

# ------------------------------
# Helper functions
# ------------------------------
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

def register_user(chat_id, first_name, phone_number):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.telegram_id == str(chat_id)).first()
    if not existing_user:
        user = User(telegram_id=str(chat_id), name=first_name, phone=phone_number)
        db.add(user)
        db.commit()
    db.close()

# ------------------------------
# Telegram webhook
# ------------------------------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        first_name = message["from"].get("first_name", "")
        text = message.get("text", "")
        contact = message.get("contact")

        # Handle /start
        if text == "/start":
            keyboard = {
                "keyboard": [[{"text": "Register", "request_contact": True}]],
                "one_time_keyboard": True,
                "resize_keyboard": True
            }
            send_message(chat_id, f"Welcome {first_name}! Please register by sharing your contact.", reply_markup=keyboard)
            return {"ok": True}

        # Handle contact sharing
        if contact:
            phone_number = contact.get("phone_number")
            register_user(chat_id, first_name, phone_number)

            # Reply with Play button (Web App)
            keyboard = {
                "inline_keyboard": [
                    [{"text": "▶️ Play", "web_app": {"url": "https://bingoo-bot.onrender.com"}}]
                ]
            }
            send_message(chat_id, "You are registered! Click Play to open the game.", reply_markup=keyboard)
            return {"ok": True}

    return {"ok": True}

# ------------------------------
# Health check & root
# ------------------------------
@app.get("/")
async def root():
    return {
        "message": "Bingo Bot API",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ------------------------------
# Run server
# ------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
