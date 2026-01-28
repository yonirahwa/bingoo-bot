from fastapi import FastAPI, Request
import requests
import os


app = FastAPI()

# Load your Telegram bot token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.post("/api/bot/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()  # Telegram sends JSON updates
    chat_id = update.get("message", {}).get("chat", {}).get("id")
    text = update.get("message", {}).get("text")

    if chat_id and text:
        # Example: simple echo reply
        requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": f"You said: {text}"}
        )

    return {"ok": True}
