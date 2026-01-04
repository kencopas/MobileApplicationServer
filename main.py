import uvicorn
from fastapi import FastAPI, WebSocket
from server import event_router
from utils.logger import get_logger

log = get_logger("api_server")

app = FastAPI()

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
# WebSocket (Gameplay)
# -----------------------

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    await event_router(ws)

# -----------------------
# Entry point
# -----------------------

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
    )
