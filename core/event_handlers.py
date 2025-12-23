import random
from typing import Dict
from websockets.asyncio.server import ServerConnection

from app import event_handler_registry, state_manager

from core.state_manager import get_state_manager
from core.websocket_service import get_websocket_service
from core.wsp_helpers import state_update, send_wsp_event

from models.wsp_schemas import WSPEvent
from models.events import PlayerRollDice, SessionInit, PurchasedProperty, PayedRent
from models.board_models import PropertySpace

from utils.logger import get_logger
from utils.event_bus import DefaultPhase, get_event_bus


log = get_logger("event_handlers")
event_bus = get_event_bus()
state_manager = get_state_manager()
websocket_service = get_websocket_service()


async def process_and_update(game_id: str):
    await event_bus.process_all_phases()
    game_state = state_manager.get_game_state(game_id)
    await state_update(game_state)


@event_handler_registry.event("connectionClosed")
async def handle_connection_closed(ws: ServerConnection, game_id: str, user_id: str, data: Dict | None) -> None:
    disconnected_users = websocket_service.get_closed_websockets()
    for gid, uids in disconnected_users.items():
        for uid in uids:
            state_manager.remove_player(game_id=gid, user_id=uid)
        game_state = state_manager.get_game_state(game_id=gid)
        await state_update(game_state)


@event_handler_registry.event("payRentConfirmation")
async def handle_pay_rent(ws: ServerConnection, game_id: str, user_id: str, data: Dict | None) -> WSPEvent | None:

    user_state = state_manager.get_user_state(user_id)
    game_state = state_manager.get_game_state(game_id)

    space = game_state.game_board[user_state.position]

    if not isinstance(space, PropertySpace):
        raise ValueError("Attempted to pay rent on a non-property space.")

    opponent_id = space.owned_by
    rent = 100

    await event_bus.publish(
        DefaultPhase.INPUT,
        PayedRent(
            game_id=game_id,
            user_id=user_id,
            opponent_id=opponent_id,
            rent_dollars=rent
        )
    )

    await process_and_update(game_id)


@event_handler_registry.event("buyProperty")
async def handle_buy_property(ws: ServerConnection, game_id: str, user_id: str, data: Dict | None) -> WSPEvent | None:
    
    user_state = state_manager.get_user_state(user_id)
    game_state = state_manager.get_game_state(game_id)
    space = game_state.game_board[user_state.position]

    if not isinstance(space, PropertySpace):
        raise ValueError("buyProperty event was triggered while user is occupying a non-property space.")

    await event_bus.publish(
        DefaultPhase.INPUT,
        PurchasedProperty(
            game_id=game_id,
            user_id=user_id,
            space=space
        )
    )

    await process_and_update(game_id)


@event_handler_registry.event("onlineGame")
async def handle_online_game(ws: ServerConnection, game_id: str, user_id: str, data: Dict | None) -> WSPEvent | None:

    # Create state if it doesn't exist
    state_manager.initialize_session(user_id=user_id, game_id=game_id)
    game_state = state_manager.get_game_state(game_id)

    # Update the board so that the player occupies the Boot Sequence space
    game_state.game_board[0].add_occupant(user_id)
    state_manager.set_state(game_id, game_state)

    await state_update(game_state)


@event_handler_registry.event("monopolyMove")
async def handle_monopoly_move(ws: ServerConnection, game_id: str, user_id: str, data: Dict | None) -> WSPEvent | None:
    """Handle a Monopoly game move event."""

    await event_bus.publish(
        DefaultPhase.INPUT,
        PlayerRollDice(
            game_id=game_id,
            user_id=user_id,
            dice_roll=(random.randint(1, 6) + random.randint(1, 6))
        )
    )

    await process_and_update(game_id)


@event_handler_registry.event("sessionInit")
async def handle_session_init(ws: ServerConnection, game_id: str, user_id: str, data: Dict | None) -> WSPEvent:
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

    session_id = data.get("sessionId")

    await event_bus.publish(
        DefaultPhase.INPUT,
        SessionInit(
            user_id=user_id,
            session_id=session_id,
            game_id=game_id
        )
    )

    state_manager.initialize_session(user_id=user_id, game_id=game_id)
    await process_and_update(game_id)
