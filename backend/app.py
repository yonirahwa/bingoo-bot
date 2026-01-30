from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import requests

from backend.config import settings
from backend.database import Base, engine
from backend.routes import auth, games, wallet, profile, websocket

app = FastAPI(
    title="Bingo Bot API",
    description="Web-based Bingo Game for Telegram",
    version="1.0.0"
)

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": f"You said: {text}"
            }
        )

    return {"ok": True}

# --- DB ---
Base.metadata.create_all(bind=engine)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static files ---
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --- Routers ---
app.include_router(auth.router)
app.include_router(games.router)
app.include_router(wallet.router)
app.include_router(profile.router)
app.include_router(websocket.router)

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
