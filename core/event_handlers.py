import random
from typing import Dict
from websockets.asyncio.server import ServerConnection

from app import event_handler_registry, state_manager

from core.state_manager import get_state_manager
from core.websocket_service import get_websocket_service
from core.wsp_helpers import state_update, send_wsp_event

from models.wsp_schemas import WSPEvent
from models.events import PlayerRollDice, SessionInit

from utils.logger import get_logger
from utils.wsp_utils import get_missing_fields
from utils.event_bus import DefaultPhase, get_event_bus


log = get_logger("event_handlers")
event_bus = get_event_bus()
state_manager = get_state_manager()
websocket_service = get_websocket_service()


@event_handler_registry.event("buyProperty")
async def handle_buy_property(ws: ServerConnection, data: Dict | None) -> WSPEvent | None:
    game_id 


@event_handler_registry.event("onlineGame")
async def handle_online_game(ws: ServerConnection, data: Dict | None) -> WSPEvent | None:
    game_id = data.get('onlineGameId')
    user_id = data.get('userId')

    # Create state if it doesn't exist
    state_manager.initialize_session(user_id=user_id, game_id=game_id)
    game_state = state_manager.get_state(game_id)

    # Update the board so that the player occupies the go space
    if user_id not in game_state.game_board[0].visual_properties.occupied_by:
        game_state.game_board[0].visual_properties.occupied_by.append(user_id)
    state_manager.set_state(game_id, game_state)

    await state_update(game_state)


@event_handler_registry.event("monopolyMove")
async def handle_monopoly_move(ws: ServerConnection, data: Dict | None) -> WSPEvent | None:
    """Handle a Monopoly game move event."""

    user_id = data.get("userId")
    game_id = data.get("onlineGameId")
    game_state = state_manager.get_state(game_id=game_id)

    await event_bus.publish(
        DefaultPhase.INPUT,
        PlayerRollDice(
            game_id=game_id,
            user_id=user_id,
            dice_roll=(random.randint(1, 6) + random.randint(1, 6))
        )
    )

    await event_bus.process_all_phases()
    await state_update(game_state)


@event_handler_registry.event("sessionInit")
async def handle_session_init(ws: ServerConnection, data: Dict | None) -> WSPEvent:
    """Handle session initialization or restoration.

    Expected Data:
    ```
    {
        "sessionId": "string",
        "userId": "string",
        "onlineGameId": "string"
    }
    ```
    """

    missing_fields = get_missing_fields(data, ["sessionId", "userId", "onlineGameId"])

    if missing_fields:
        log.error(f"sessionInit missing fields: {missing_fields}")
        return WSPEvent(
            event="error",
            data={"message": f"Missing fields: {', '.join(missing_fields)}", "errorValue": missing_fields},
            error="missingValue"
        )

    session_id = data.get("sessionId")
    user_id = data.get("userId")
    game_id = data.get("onlineGameId")

    await event_bus.publish(
        DefaultPhase.INPUT,
        SessionInit(
            user_id=user_id,
            session_id=session_id,
            game_id=game_id
        )
    )

    state_manager.initialize_session(user_id=user_id, game_id=game_id)
    game_state = state_manager.get_state(game_id=game_id)
    await state_update(game_state)
