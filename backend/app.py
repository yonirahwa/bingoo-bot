# app.py
from fastapi import FastAPI, Request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Set your bot token in Render environment variables
bot = Bot(token=BOT_TOKEN)

app = FastAPI()

# In-memory "database" for demo purposes
registered_users = set()

# Helper function to generate keyboard
def main_menu_keyboard(registered=False):
    if registered:
        buttons = [[InlineKeyboardButton("Play", callback_data="play")]]
    else:
        buttons = [[InlineKeyboardButton("Register", callback_data="register")]]
    return InlineKeyboardMarkup(buttons)

# Webhook endpoint for Telegram
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)

    if update.message:
        chat_id = update.message.chat.id
        first_name = update.message.from_user.first_name
        if chat_id in registered_users:
            reply_markup = main_menu_keyboard(registered=True)
            await bot.send_message(chat_id=chat_id, text="Welcome back! Click Play to continue.", reply_markup=reply_markup)
        else:
            reply_markup = main_menu_keyboard(registered=False)
            await bot.send_message(chat_id=chat_id, text=f"Hello {first_name}! Please register first.", reply_markup=reply_markup)

    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
        data = update.callback_query.data

        if data == "register":
            registered_users.add(chat_id)
            reply_markup = main_menu_keyboard(registered=True)
            await bot.send_message(chat_id=chat_id, text="Registration successful! Click Play to continue.", reply_markup=reply_markup)
        elif data == "play":
            await bot.send_message(chat_id=chat_id, text="🎮 Game started! Enjoy playing!")

        # Answer callback query to remove loading animation
        await update.callback_query.answer()

    return {"ok": True}

# Optional: simple root endpoint to check if FastAPI is running
@app.get("/")
async def root():
    return {"message": "Bot webhook is running!"}


