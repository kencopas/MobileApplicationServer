from typing import Dict
from utils.logger import get_logger
from utils.wsp_utils import validate_wsp, send_wsp_event
from websockets.asyncio.server import ServerConnection
from models.wsp_schemas import WSPEvent
from app import state_manager, session_manager, event_handler_registry, board
import sqlite3


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

    session_manager.save(
        user_id=user_id,
        session_id=session_id,
        state=state_manager.get_state(user_id)
    )

    return WSPEvent(
        event="saveSessionAck",
        data={"status": "success"}
    )


@event_handler_registry.event("monopolyMove")
async def handle_monopoly_move(ws: ServerConnection, data: Dict | None) -> WSPEvent:
    """Handle a Monopoly game move event."""

    log.info(f"Monopoly move made")

    user_state = state_manager.get_state(data.get("userId"))
    if not user_state:
        log.error(f"User state not found for userId: {data.get('userId')}")
        return WSPEvent(
            event="error",
            data={"message": "User state not found", "errorValue": data.get("userId")},
            error="stateNotFound"
        )
    
    board.move_player(user_state)

    await send_wsp_event(ws, WSPEvent(
        event="stateUpdate",
        data={
            "state": user_state.to_dict()
        }
    ))

    return board.handle_landing(user_state)


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
    
    session_id = data.get("sessionId")
    user_id = data.get("userId")

    if session_id is None:
        log.error("sessionInit missing sessionId")
        return WSPEvent(
            event="error",
            data={"message": "sessionId is required", "errorValue": "sessionId"},
            error="missingValue"
        )
    
    if user_id is None:
        log.error("sessionInit missing userId")
        return WSPEvent(
            event="error",
            data={"message": "userId is required", "errorValue": "userId"},
            error="missingValue"
        )

    try:
        session_state = session_manager.initialize_session(user_id=user_id, session_id=session_id)
    except sqlite3.IntegrityError as e:
        log.error(f"Failed to initialize session: {e}. Session already exists?")
        return WSPEvent(
            event="error",
            data={
                "message": f"Failed to initialize session: {e}",
                "errorValue": str(e)
            },
            error="sessionExists"
        )
    
    # Restore or create
    user_data = session_manager.get_or_create_user(user_id=user_id)

    # Construct user state object, save in memory
    state_manager.initialize_state(session_state)

    return WSPEvent(
        event="sessionAck",
        data={
            "userId": user_id,
            "userData": user_data,
            "sessionId": session_id,
            "state": session_state
        }
    )
