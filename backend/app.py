import os
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ===== CONFIG =====
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Please set TELEGRAM_BOT_TOKEN environment variable!")

# ===== DATABASE SETUP =====
DATABASE_URL = os.getenv("DATABASE_URL")  # Render provides DATABASE_URL
if not DATABASE_URL:
    raise ValueError("Please set DATABASE_URL environment variable!")

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
cursor = conn.cursor()

# Create users table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id BIGINT PRIMARY KEY,
    first_name TEXT NOT NULL
);
""")
conn.commit()

# ===== HELPERS =====
async def is_registered(chat_id):
    cursor.execute("SELECT 1 FROM users WHERE chat_id = %s", (chat_id,))
    return cursor.fetchone() is not None

async def register_user(chat_id, first_name):
    if not await is_registered(chat_id):
        cursor.execute(
            "INSERT INTO users (chat_id, first_name) VALUES (%s, %s)",
            (chat_id, first_name)
        )
        conn.commit()
        return True
    return False

# ===== COMMAND HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name

    if await is_registered(chat_id):
        keyboard = [[InlineKeyboardButton("Play 🎮", callback_data="play")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text=f"Welcome back {first_name}!", reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("Register ✅", callback_data="register")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text=f"Hi {first_name}! Please register first.", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    first_name = query.from_user.first_name

    if query.data == "register":
        registered = await register_user(chat_id, first_name)
        if registered:
            keyboard = [[InlineKeyboardButton("Play 🎮", callback_data="play")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id, text="Registration successful! Click Play to start the game.", reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=chat_id, text="You are already registered! Click Play to start the game.")
    
    elif query.data == "play":
        if not await is_registered(chat_id):
            keyboard = [[InlineKeyboardButton("Register ✅", callback_data="register")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id, text="You must register first before playing.", reply_markup=reply_markup)
            return
        
        # ===== GAME LOGIC =====
        # Example: simple game message
        await context.bot.send_message(chat_id=chat_id, text="🎮 Game started! Good luck!")

# ===== MAIN FUNCTION =====
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
