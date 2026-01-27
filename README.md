# 🎉 Bingo Bot - Web App Telegram Mini App

A fully functional, real-time Bingo game built for Telegram Mini Apps with WebSocket support, wallet integration, and beautiful UI.

## Features

✅ **Real-time Multiplayer Gaming**
- WebSocket-based live updates
- 3-second delay between number calls
- Auto-marking of numbers
- Real-time player count updates

✅ **Game Features**
- Select up to 2 bingo cards per game
- Multiple game rooms with different stakes
- Automatic winner detection
- Win notifications with rewards

✅ **Wallet System**
- Deposit via TeleBirr, CBE Birr, Commercial Bank
- Withdraw funds
- Transfer between players
- Transaction history

✅ **User Profile**
- Profile photo upload
- Language selection (English, Amharic, Oromo)
- User statistics

✅ **Connection Status**
- Real-time connection indicator
- Auto-reconnection
- Graceful disconnection handling

## Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL
- SQLAlchemy ORM
- WebSockets
- Uvicorn

**Frontend:**
- HTML5 / CSS3
- Vanilla JavaScript
- Telegram Web App SDK
- WebSocket Client

**Deployment:**
- Render (Backend + Database)
- GitHub (Version Control)

## Local Development

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Node.js (optional, for npm packages)

### Setup

1. **Clone the repository**
```bash
git clone YOUR_REPO_URL
cd bingo-bot
