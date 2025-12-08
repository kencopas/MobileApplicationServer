from core.state_manager import get_state_manager
from core.websocket_service import get_websocket_service

from models.wsp_schemas import WSPEvent
from models.events import PlayerMoved, PlayerRollDice, PurchasedProperty
from models.commands import MovePlayer, BuyProperty, ModifyFunds
from models.board_models import PropertySpace, ActionSpace

from utils.event_bus import get_event_bus
from utils.wsp_utils import send_wsp_event
from utils.logger import get_logger


log = get_logger('event_bus_listeners')
websocket_service = get_websocket_service()
state_manager = get_state_manager()
event_bus = get_event_bus()


@event_bus.on(PurchasedProperty)
async def handle_buy_property(event: PurchasedProperty):
    # Logic for buying a property
    return BuyProperty(
        game_id=event.game_id,
        user_id=event.user_id,
        space=event.space
    )


@event_bus.on(PlayerMoved)
async def check_if_passed_go(event: PlayerMoved):
    if event.old_position >= event.new_position:
        return ModifyFunds(
            user_id=event.user_id,
            game_id=event.game_id,
            money_dollars=200
        )


@event_bus.on(PlayerMoved)
async def handle_player_landing(event: PlayerMoved):
    game_state = state_manager.get_game_state(event.game_id)
    user_state = state_manager.get_user_state(event.user_id)
    landed_space = game_state.game_board[event.new_position]
    ws = websocket_service.get_websocket_by_user(user_state.user_id)

    if isinstance(landed_space, PropertySpace):
        if not landed_space.owned_by:
            # Unowned space
            log.info(f"User landed on unowned property: {landed_space.name}")
            if user_state.money_dollars >= landed_space.purchase_price:
                await send_wsp_event(ws, WSPEvent(
                    event="showDialog",
                    data={
                        "space": landed_space.model_dump(),
                        "promptType": "askPurchaseProperty",
                        "message": f"Would you like to purchase this property for ${landed_space.purchase_price}?"
                    }
                ))
            else:
                await send_wsp_event(ws, WSPEvent(
                    event="showDialog",
                    data={
                        "space": landed_space.model_dump(),
                        "promptType": "alert",
                        "message": f"You do not have enough money to purchase this property."
                    }
                ))
            return

        if landed_space.owned_by == user_state.user_id:
            # Self-owned space
            log.info(f"User landed on their own property: {landed_space.name}")
            await send_wsp_event(ws, WSPEvent(
                event="showDialog",
                data={
                    "space": landed_space.model_dump(),
                    "promptType": "alert",
                    "message": f"You already own this property."
                }
            ))
            return

        # Opponent-owned space
        log.info(f"User landed on their opponent's property: {landed_space.name}")
        await send_wsp_event(ws, WSPEvent(
            event="showDialog",
            data={
                "space": landed_space.model_dump(),
                "promptType": "payRent",
                "message": f"Your opponent owns this property. You must pay ${50} (hard-coded placeholder value) in rent."
            }
        ))
        return

    elif isinstance(landed_space, ActionSpace):
        log.info(f"User landed on action space: {landed_space.name}")
        await send_wsp_event(ws, WSPEvent(
            event="showDialog",
            data={
                "space": landed_space.model_dump(),
                "promptType": "actionSpace",
                "message": f"You must perform {landed_space.action}"
            }
        ))


@event_bus.on(PlayerRollDice)
async def update_player_position(event: PlayerRollDice):
    
    user_state = state_manager.get_user_state(event.user_id)

    if not user_state:
        raise ValueError(f"Unable to update player position for user state which does not exist. User ID: {event.user_id}")

    new_position = (user_state.position + event.dice_roll) % 40

    return MovePlayer(
        game_id=event.game_id,
        user_id=event.user_id,
        old_position=user_state.position,
        new_position=new_position
    )
