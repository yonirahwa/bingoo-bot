from typing import Set, Dict, List
import json
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}  # room_id -> set of websockets
        self.user_connections: Dict[int, WebSocket] = {}  # user_id -> websocket
    
    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
        self.user_connections[user_id] = websocket
    
    async def disconnect(self, room_id: int, user_id: int):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(self.user_connections.get(user_id))
            if len(self.active_connections[room_id]) == 0:
                del self.active_connections[room_id]
        if user_id in self.user_connections:
            del self.user_connections[user_id]
    
    async def broadcast_to_room(self, room_id: int, message: dict):
        """Send message to all users in a room"""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting to room {room_id}: {e}")
    
    async def send_personal_message(self, user_id: int, message: dict):
        """Send message to a specific user"""
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except Exception as e:
                print(f"Error sending personal message to user {user_id}: {e}")

manager = ConnectionManager()
