import json
from typing import Dict
from utils.logger import get_logger
from utils.wsp_utils import EventHandlerRegistry
from utils.session_manager import SessionManager
from app.state_manager import StateManager
from websockets.asyncio.server import ServerConnection
from models.wsp_schemas import WSPEvent
from config.config import SESSION_PERSIST_PATH
import sqlite3
import random


log = get_logger("websocket-server")

elr = EventHandlerRegistry(log=log.info)
session_manager = SessionManager(
    persist_path=str(SESSION_PERSIST_PATH),
    logger=log
)
state_manager = StateManager()


@elr.event("baseEvent")
async def base_event_handler(ws: ServerConnection, data: Dict | None) -> WSPEvent:
    return WSPEvent(
        event="baseEventAck",
        data={"message": "This is a response from baseEvent"}
    )


@elr.event("saveSession")
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


@elr.event("monopolyMove")
async def handle_monopoly_move(ws: ServerConnection, data: Dict | None) -> WSPEvent:
    """Handle a Monopoly game move event."""

    log.info(f"Monopoly move made")
    money_made = random.randint(50, 500)

    user_state = state_manager.get_state(data.get("userId"))
    if not user_state:
        log.error(f"User state not found for userId: {data.get('userId')}")
        return WSPEvent(
            event="error",
            data={"message": "User state not found", "errorValue": data.get("userId")},
            error="stateNotFound"
        )

    user_state.add_money(money_made)

    # Here you would add logic to process the move, update game state, etc.

    return WSPEvent(
        event="stateUpdate",
        data={
            "state": user_state.to_dict()
        }
    )


@elr.event("sessionInit")
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

    # Restore or create
    user_data = session_manager.get_or_create_user(user_id=user_id)
    state_data = session_manager.get_session_state(user_id=user_id, session_id=session_id)

    # Construct user state object, save in memory
    state_manager.initialize_state(user_id=user_id, initial_state=state_data)

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

    return WSPEvent(
        event="sessionAck",
        data={
            "userId": user_id,
            "userData": user_data,
            "sessionId": session_id,
            "state": session_state
        }
    )
