from typing import Dict
from utils.logger import get_logger
from utils.wsp_utils import send_wsp_event, get_missing_fields
from websockets.asyncio.server import ServerConnection
from models.wsp_schemas import WSPEvent
from app import event_handler_registry, event_bus
from models.events import PlayerRollDice, PlayerPositionUpdate
from utils.event_bus import Phase
import random
from state_manager import StateManager


state_manager: StateManager = None
game_controller = None
log = get_logger("event_handlers")


@event_bus.on(PlayerRollDice)
async def update_player_position(event: PlayerRollDice):
    
    user_state = state_manager.get_player_state(event.user_id)
    new_position = (user_state.position + event.dice_roll) % 40

    event_bus.publish(
        Phase.RESOLUTION,
        PlayerPositionUpdate(
            user_id=event.user_id,
            online_game_id=event.online_game_id,
            old_position=user_state.position,
            new_position=new_position
        )
    )


@event_handler_registry.event("monopolyMove")
async def handle_monopoly_move(ws: ServerConnection, data: Dict | None) -> WSPEvent | None:
    """Handle a Monopoly game move event."""

    user_id = data.get("userId")
    online_game_id = data.get("onlineGameId")

    await event_bus.publish(
        Phase.INPUT,
        PlayerRollDice(
            online_game_id=online_game_id,
            user_id=user_id,
            dice_roll=(random.randint(1, 6) + random.randint(1, 6))
        )
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


@event_handler_registry.event("buyProperty")
async def handle_buy_property(ws: ServerConnection, data: Dict | None) -> WSPEvent | None:
    """Handle a buy property event."""

    user_id = data.get("userId")
    session_id = data.get("sessionId")

    user_state = game_controller.state_manager.get_state(user_id)
    if not user_state:
        log.error(f"User state not found for userId: {user_id}")
        return WSPEvent(
            event="error",
            data={"message": "User state not found", "errorValue": user_id},
            error="stateNotFound"
        )
    
    try:
        await game_controller.buy_property(ws, user_id, session_id)
    except Exception as e:
        log.error(f"Error during handle_buy_property for userId {user_id}: {e}")
        return WSPEvent(
            event="error",
            data={"message": "Error processing property purchase", "errorValue": str(e)},
            error="purchaseError"
        )
    

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
    online_game_id = data.get("onlineGameId")

    await event_bus.publish("session_init",
        user_id=user_id,
        session_id=session_id,
        online_game_id=online_game_id
    )

    return WSPEvent(event="sessionAck")
