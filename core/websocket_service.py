from websockets.asyncio.server import ServerConnection
from typing import List, Dict
from functools import lru_cache


class WebsocketService:
    _websockets_by_user: Dict[str, ServerConnection]
    """Maps user_id to a websocket"""
    _websockets_by_game: Dict[str, Dict[str, ServerConnection]]
    """Maps game_id to a Dictionary that maps user_id to websocket, but only users in the game and they're corresponding websocket"""

    def __init__(self):
        self._websockets_by_user = {}
        self._websockets_by_game = {}
    
    def register_websocket(self, ws: ServerConnection, user_id: str, game_id: str) -> None:
        self._websockets_by_user[user_id] = ws
        if self._websockets_by_game.get(game_id) is None:
            self._websockets_by_game[game_id] = {}
        self._websockets_by_game[game_id][user_id] = ws
    
    def get_websocket_by_user(self, user_id: str) -> ServerConnection | None:
        return self._websockets_by_user.get(user_id)

    def get_websockets_by_game(self, game_id: str) -> List[ServerConnection] | None:
        return self._websockets_by_game.get(game_id)


@lru_cache(maxsize=1)
def get_websocket_service() -> WebsocketService:
    return WebsocketService()
