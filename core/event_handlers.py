from typing import Dict
from utils.logger import get_logger
from utils.wsp_utils import send_wsp_event, get_missing_fields
from websockets.asyncio.server import ServerConnection
from models.wsp_schemas import WSPEvent
from app import event_handler_registry, game_controller


log = get_logger("event_handlers")


@event_handler_registry.event("baseEvent")
async def base_event_handler(ws: ServerConnection, data: Dict | None) -> WSPEvent:
    return WSPEvent(
        event="baseEventAck",
        data={"message": "This is a response from baseEvent"}
    )


@event_handler_registry.event("saveSession")
async def save_session_handler(ws: ServerConnection, data: Dict | None) -> WSPEvent:
    
    user_id = data.get("userId")
    session_id = data.get("sessionId")

    game_controller.save_game(
        user_id=user_id,
        session_id=session_id
    )

    return WSPEvent(
        event="saveSessionAck",
        data={"status": "success"}
    )


@event_handler_registry.event("monopolyMove")
async def handle_monopoly_move(ws: ServerConnection, data: Dict | None) -> WSPEvent:
    """Handle a Monopoly game move event."""

    user_id = data.get("userId")
    session_id = data.get("sessionId")

    user_state = game_controller.get_state(user_id)
    if not user_state:
        log.error(f"User state not found for userId: {user_id}")
        return WSPEvent(
            event="error",
            data={"message": "User state not found", "errorValue": user_id},
            error="stateNotFound"
        )
    
    game_controller.move_player(user_id, session_id)
    state = game_controller.get_state(user_id)

    await send_wsp_event(ws, WSPEvent(
        event="stateUpdate",
        data={
            "state": state.to_dict()
        }
    ))

    return game_controller.handle_landing(user_id)


@event_handler_registry.event("sessionInit")
async def handle_session_init(ws: ServerConnection, data: Dict | None) -> WSPEvent:
    """Handle session initialization or restoration.
    
    Expected Data:
    ```
    {
        "sessionId": "string",
        "userId": "string"
    }
    ```
    """

    missing_fields = get_missing_fields(data, ["sessionId", "userId"])

    if missing_fields:
        log.error(f"sessionInit missing fields: {missing_fields}")
        return WSPEvent(
            event="error",
            data={"message": f"Missing fields: {', '.join(missing_fields)}", "errorValue": missing_fields},
            error="missingValue"
        )

    session_id = data.get("sessionId")
    user_id = data.get("userId")

    # Restore or create
    game_controller.start_session(user_id=user_id, session_id=session_id)

    user_state = game_controller.get_state(user_id=user_id).to_dict()
    user_data = game_controller.state_manager.session_manager.get_user_data(user_id)

    return WSPEvent(
        event="sessionAck",
        data={
            "userId": user_id,
            "userData": user_data,
            "sessionId": session_id,
            "state": user_state if user_state else {}
        }
    )
