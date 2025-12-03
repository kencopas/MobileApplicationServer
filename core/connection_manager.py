from websockets.asyncio.server import ServerConnection
from utils.logger import get_logger


log = get_logger("connection_manager")

_user_websockets: dict[str, ServerConnection] = {}


def get_user_websocket(user_id: str) -> ServerConnection | None:
    """Retrieve the websocket connection for a given user ID."""
    return _user_websockets.get(user_id)


def register_user_websocket(ws: ServerConnection, user_id: str) -> None:
    """Register a user's websocket connection in the event bus."""

    log.info(f"Registering websocket for user_id: {user_id}")
    global _user_websockets
    _user_websockets[user_id] = ws



