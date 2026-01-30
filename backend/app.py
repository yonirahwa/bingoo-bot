import os
import asyncio
import asyncpg
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
)

# Read environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")  # Render Postgres URL

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable not set")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set")

# PostgreSQL connection pool
async def create_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

# Initialize bot application
app = ApplicationBuilder().token(BOT_TOKEN).build()

# ---------- Registration ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name

    pool = context.bot_data["db_pool"]
    async with pool.acquire() as conn:
        # Check if user is already registered
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE chat_id=$1", chat_id
        )
        if user:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Welcome back {first_name}! Click Play to start the game.",
                reply_markup=play_button(),
            )
            return

    # Ask user to share contact
    contact_button = KeyboardButton(
        "Share Contact", request_contact=True
    )
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Please share your phone number to register:",
        reply_markup=reply_markup,
    )


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    chat_id = update.effective_chat.id

    if not contact or not contact.phone_number:
        await context.bot.send_message(chat_id=chat_id, text="Please share your contact properly.")
        return

    pool = context.bot_data["db_pool"]
    async with pool.acquire() as conn:
        # Check if contact is already registered
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE phone=$1", contact.phone_number
        )
        if user:
            await context.bot.send_message(
                chat_id=chat_id,
                text="This phone number is already registered!",
            )
            return

        # Insert new user
        await conn.execute(
            "INSERT INTO users(chat_id, first_name, phone) VALUES($1, $2, $3)",
            chat_id,
            update.effective_user.first_name,
            contact.phone_number,
        )

    await context.bot.send_message(
        chat_id=chat_id,
        text="Registration successful! Click Play to continue.",
        reply_markup=play_button(),
    )


# ---------- Play Button ----------

def play_button():
    keyboard = [
        [
            InlineKeyboardButton("Play 🎮", callback_data="play_game")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def handle_play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    await context.bot.send_message(chat_id=chat_id, text="🎉 Game started! Have fun!")


# ---------- Handlers ----------

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
app.add_handler(CallbackQueryHandler(handle_play, pattern="play_game"))

# ---------- Database Setup ----------

async def init_db():
    pool = await create_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT UNIQUE NOT NULL,
                first_name TEXT,
                phone TEXT UNIQUE NOT NULL
            );
        """)
    return pool


# ---------- Main ----------

async def main():
    db_pool = await init_db()
    app.bot_data["db_pool"] = db_pool
    print("Bot is running...")
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())
