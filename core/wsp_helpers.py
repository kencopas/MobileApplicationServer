from utils.wsp_utils import send_wsp_event
from models.wsp_schemas import WSPEvent
from models.game_state import GameState
from websockets.asyncio.server import ServerConnection
from typing import Dict
from core.websocket_service import get_websocket_service


websocket_service = get_websocket_service()


async def state_update(state: GameState | Dict) -> None:
    """Send a state update event over the websocket connection."""

    state_data = state.to_dict() if isinstance(state, GameState) else state
    websockets = websocket_service.get_websockets_by_game(game_id=state.game_id)

    for ws in websockets.values():
        await send_wsp_event(ws, WSPEvent(
            event="stateUpdate",
            data={
                "state": state_data
            }
        ))
