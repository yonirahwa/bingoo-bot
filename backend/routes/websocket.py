from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from websocket_manager import manager

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/game/{room_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    user_id: int
):
    """WebSocket connection for real-time game updates"""
    await manager.connect(websocket, room_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type")
            
            if message_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "status_check":
                await websocket.send_json({
                    "type": "connection_status",
                    "status": "connected",
                    "user_id": user_id
                })
            
            else:
                # Broadcast to room
                await manager.broadcast_to_room(room_id, data)
    
    except WebSocketDisconnect:
        await manager.disconnect(room_id, user_id)
        await manager.broadcast_to_room(room_id, {
            "type": "player_left",
            "user_id": user_id
        })
