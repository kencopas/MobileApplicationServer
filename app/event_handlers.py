import json
from typing import Dict
from utils.logger import get_logger
from utils.wsp_utils import EventHandlerRegistry
from utils.session_manager import SessionManager
from websockets.asyncio.server import ServerConnection
from models.wsp_schemas import WSPEvent
from config.config import SESSION_PERSIST_PATH
import sqlite3


log = get_logger("websocket-server")
elr = EventHandlerRegistry(log=log.info)
session_manager = SessionManager(
    persist_path=str(SESSION_PERSIST_PATH),
    logger=log
)


@elr.event("baseEvent")
async def base_event_handler(ws: ServerConnection, data: Dict | None) -> WSPEvent:
    return WSPEvent(
        event="baseEvent",
        data={"message": "This is a response from baseEvent"}
    )


@elr.event("saveSession")
async def save_session_handler(ws: ServerConnection, data: Dict | None) -> WSPEvent:
    
    session_manager.save(
        user_id=data.get("userId"),
        session_id=data.get("sessionId"),
        state=data.get("state", {})
    )

    return WSPEvent(
        event="saveSession",
        data={"status": "success"}
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

    try:
        session_state = session_manager.initialize_session(user_id=user_id, session_id=session_id)
    except sqlite3.IntegrityError as e:
        log.error(f"Failed to initialize session: {e}. Session already exists?")
        return WSPEvent(
            event="error",
            data={
                "message": f"Failed to initialize session: {e}",
                "errorValue": str(e),
                "userId": user_id,
                "userData": user_data,
                "sessionId": session_id,
                "state": session_manager.get_session_state(user_id, session_id)
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
