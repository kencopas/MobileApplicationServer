from fastapi import FastAPI, WebSocket

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


@app.post("/games")
async def create_game():
    log.info("Creating game")
    return {"gameId": "ABC123"}


@app.post("/games/{game_id}/join")
async def join_game(game_id: str):
    log.info(f"Joining game {game_id}")
    return {"status": "joined"}


@app.post("/games/{game_id}/start")
async def start_game(game_id: str):
    log.info(f"Starting game {game_id}")
    return {"status": "started"}


# -----------------------
# WebSocket
# -----------------------


@app.websocket("/rooms/{lobby_id}/ws")
async def lobby_websocket(ws: WebSocket, lobby_id: str):
    await ws.accept()
    await lobby_handler(ws, lobby_id)


@app.websocket("/games/{game_id}/ws")
async def online_game_websocket(ws: WebSocket):
    await ws.accept()
    await event_router(ws)
