from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.database import Base, engine
from backend.routes import auth, games, wallet, profile, websocket
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bingo Bot API",
    description="Web-based Bingo Game for Telegram",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

