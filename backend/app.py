import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import asyncpg

# Get environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set!")

# Initialize database connection
async def init_db():
    return await asyncpg.connect(DATABASE_URL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text="Welcome! Please register first."
    )

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name
    conn = await init_db()

    # Example: store user info
    await conn.execute(
        "INSERT INTO users(chat_id, first_name) VALUES($1, $2) ON CONFLICT DO NOTHING",
        chat_id, first_name
    )

    # Send play button (as inline keyboard)
    keyboard = [[InlineKeyboardButton("Play", callback_data="play")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text="Registration successful!", reply_markup=reply_markup)

    await conn.close()

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "play":
        await query.edit_message_text(text="🎮 Game started!")

# Build bot application
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))
    app.add_handler(MessageHandler(filters.TEXT, start))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.Regex("^/.*"), start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))
    app.add_handler(MessageHandler(filters.ALL, start))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))

    # Callback for inline buttons
    app.add_handler(MessageHandler(filters.ALL, start))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
