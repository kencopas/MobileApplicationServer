from websockets.asyncio.server import ServerConnection
from websockets.protocol import State
from typing import List, Dict, Set
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

    def get_websockets_by_game(self, game_id: str) -> Dict[str, ServerConnection] | None:
        return self._websockets_by_game.get(game_id)
    
    def get_closed_websockets(self) -> Dict[str, Set]:
        """Returns the game and user ids for each user that has disconnected"""
        output = {}
        for game_id, user_ws in self._websockets_by_game.items():
            disconnected_user_ids = {
                user_id for user_id, ws in user_ws.items()
                if ws.state is State.CLOSED
            }
            if disconnected_user_ids:
                output[game_id] = disconnected_user_ids
        return output


@lru_cache(maxsize=1)
def get_websocket_service() -> WebsocketService:
    return WebsocketService()
