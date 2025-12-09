from utils.wsp_utils import send_wsp_event
from models.wsp_schemas import WSPEvent
from models.game_state import GameState
from websockets.asyncio.server import ServerConnection
from typing import Dict, Optional
from core.websocket_service import get_websocket_service
from models.board_models import BoardSpace


websocket_service = get_websocket_service()


class ShowDialog:
    def __init__(self, ws: ServerConnection):
        self.ws = ws
    
    async def _show_dialog(self, *,
        prompt_type: str,
        message: str,
        space: Optional[BoardSpace] = None,
        action: Optional[str] = None,
        rent_amount: Optional[int] = None
    ) -> None:
        await send_wsp_event(self.ws, WSPEvent(
            event="showDialog",
            data={
                "promptType": prompt_type,
                "message": message,
                "space": space.model_dump() if space else None,
                "action": action,
                "rentAmount": rent_amount
            }
        ))

    async def alert(self, *, space: BoardSpace, message: str) -> None:
        await self._show_dialog(
            prompt_type="alert",
            message=message,
            space=space
        )
    
    async def ask_purchase_property(self, *, space: BoardSpace, message: str) -> None:
        await self._show_dialog(
            prompt_type="askPurchaseProperty",
            message=message,
            space=space
        )
    
    async def pay_rent(self, *, space: BoardSpace, message: str, rent_amount: int) -> None:
        await self._show_dialog(
            prompt_type="payRent",
            message=message,
            space=space,
            rent_amount=rent_amount
        )


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
