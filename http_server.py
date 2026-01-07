from fastapi import FastAPI, WebSocket
from typing import Dict

from core.room_manager import get_room_manager
from wss_server import event_router, lobby_handler
from utils.logger import get_logger

log = get_logger("http_server")
app = FastAPI()


@app.get('/')
async def home():
    return {"status": "Server is up and running!"}


# -----------------------
# HTTP (Lobby / Lifecycle)
# -----------------------


@app.post("/rooms/create")
async def create_room(data: Dict):
    player_id = data.get('player_id')
    log.info(f"Creating room with host {player_id}")
    room_id = get_room_manager().create_room(player_id)
    return {"status": "success", "room_id": room_id}


@app.post("/rooms/{room_id}/join")
async def join_room(room_id: str, data: Dict):
    player_id = data.get('player_id')
    log.info(f"Player {player_id} joining room {room_id}")
    await get_room_manager().join_room(room_id, player_id)
    return {"status": "success"}


@app.post("/games/{game_id}/start")
async def start_game(game_id: str):
    log.info(f"Starting game {game_id}")
    return {"status": "started"}


# -----------------------
# WebSocket
# -----------------------


@app.websocket("/rooms/{room_id}/ws")
async def lobby_websocket(ws: WebSocket, room_id: str):
    await ws.accept()
    await lobby_handler(ws, room_id)


@app.websocket("/games/{game_id}/ws")
async def online_game_websocket(ws: WebSocket, game_id: str):
    await ws.accept()
    await event_router(ws, game_id)
