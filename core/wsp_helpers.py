from utils.wsp_utils import send_wsp_event
from models.wsp_schemas import WSPEvent
from models.game_state import UserState
from websockets.asyncio.server import ServerConnection
from typing import Dict


async def state_update(ws: ServerConnection, state: UserState | Dict) -> None:
    """Send a state update event over the websocket connection."""

    state_data = state.to_dict() if isinstance(state, UserState) else state

    await send_wsp_event(ws, WSPEvent(
        event="stateUpdate",
        data={
            "state": state_data
        }
    ))
