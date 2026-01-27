import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/bingo_bot"
    )
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBAPP_URL: str = os.getenv("TELEGRAM_WEBAPP_URL", "http://localhost:8000")
    
    # Game Settings
    NUMBER_CALL_DELAY: int = 3  # seconds between numbers
    GAME_START_DELAY: int = 10  # seconds before game starts
    MAX_PLAYERS_PER_ROOM: int = 100
    MAX_CARDS_PER_PLAYER: int = 2
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://web.telegram.org",
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
