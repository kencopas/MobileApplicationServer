from utils.wsp_utils import send_wsp_event
from models.board_models import BoardSpace, PropertySpace, ActionSpace
from models.game_state import UserState
from core.state_manager import StateManager
from core.wsp_helpers import state_update
import random
from models.wsp_schemas import WSPEvent
from utils.logger import get_logger
from utils.event_bus import EventBus, get_event_bus
from typing import Literal
from websockets.asyncio.server import ServerConnection
from core.connection_manager import get_user_websocket
from core.state_manager import get_state_manager


state_manager = get_state_manager()
log = get_logger("game_controller")
event_bus = get_event_bus()


class GameController:
    """Singleton class that manages game logic with session state and board."""
    def __init__(self) -> None:
        pass
        # self.register_event_handlers()

    def _sort_board(self, board: list[BoardSpace]) -> list[BoardSpace]:
        """Sort the board spaces based on their space_id."""
        return sorted(board, key=lambda space: space.space_index)
    

    def save_game(self, user_id: str, session_id: str) -> None:
        """Save the current game state for a user."""
        log.info(f"Saving game for user_id {user_id} and session_id {session_id}")
        state = self.state_manager.get_state(user_id)
        if state is None:
            log.error(f"Cannot save game: No state found for user_id {user_id}")
            return
        
        self.state_manager.set_state(user_id, session_id, state)
    
    async def connect_online_game(self, ws: ServerConnection, user_id: str, session_id: str, online_game_id: str) -> None:
        """Connect a user to an online game session or start a new one."""
        log.info(f"Connecting user {user_id} to online game {online_game_id} with session ID {session_id}")
        
        if online_game_id not in self.board_manager.online_games:
            log.info(f"Online game {online_game_id} not found. Creating new online game session.")
            new_board = self.board_manager.new_board(user_id, online_game_id)
            state = self.state_manager.new_state(user_id, session_id, new_board)

            await send_wsp_event(ws, WSPEvent(
                event="showDialog",
                data={
                    "promptType": "alert",
                    "message": f"New online game session created! Share this ID with your friends:\n{online_game_id}"
                }
            ))

            await state_update(ws, state)
        else:
            log.info(f"Restoring user {user_id} to existing online game {online_game_id}.")
            self.start_session(user_id, session_id)
            state = self.state_manager.get_state(user_id)

            self.board_manager.add_player(online_game_id, user_id)
            await state_update(ws, state)

    def start_session(self, user_id: str, session_id: str, new: bool = False) -> None:
        """Start or restore a session for a user."""
        log.info(f"Starting session for user {user_id} with session ID {session_id}")

        # Retrieve or create state
        state = self.state_manager.get_state(user_id)
        if state is None or new:
            new_board = self.board_manager.new_board(user_id)
            state = self.state_manager.new_state(user_id, session_id, new_board)
        
        # Set the state in cache and persist it
        self.state_manager.set_state(user_id, session_id, state)

    
    async def handle_landing(self, ws: ServerConnection, state: UserState, current_space: BoardSpace) -> None:
        """Handle actions based on the space the player lands on."""
        log.info(f"User {state.user_id} landed on space {current_space.name} ({current_space.space_type})")

        user_id = state.user_id
        
        if isinstance(current_space, PropertySpace):
            # Property Space
            if not current_space.owned_by:
                # Unowned property
                if state.money_dollars >= current_space.purchase_price:
                    # User can afford property
                    await send_wsp_event(ws, WSPEvent(
                        event="showDialog",
                        data={
                            "promptType": "askPurchaseProperty",
                            "space": current_space.model_dump(),
                            "message": f"This property is unowned. Would you like to purchase it for ${current_space.purchase_price}?"
                        }
                    ))
                return
            
            if current_space.owned_by == user_id:
                # Player owns property
                await send_wsp_event(ws, WSPEvent(
                    event="showDialog",
                    data={
                        "promptType": "alert",
                        "message": f"This is your own property.",
                        "space": current_space.model_dump()
                    }
                ))
                return
            
            # Opponent owns property - pay rent
            placeholder_rent = 100

            if state.money_dollars < placeholder_rent:
                await send_wsp_event(ws, WSPEvent(
                    event="showDialog",
                    data={
                        "promptType": "alert",
                        "message": f"You do not have enough money to pay rent of ${placeholder_rent}.",
                        "space": current_space.model_dump()
                    }
                ))
                return
            else:
                await send_wsp_event(ws, WSPEvent(
                    event="showDialog",
                    data={
                        "promptType": "payRent",
                        "space": current_space.model_dump(),
                        "message": f"This is your opponent's property. You must pay rent of ${placeholder_rent}.",
                        "rentAmount": placeholder_rent
                    }
                ))

        elif isinstance(current_space, ActionSpace):
            # Action Space
            action = current_space.action

            match action:
                case "pay_tax":
                    state.subtract_money(200)
                case "draw_chest":
                    pass
                case "draw_chance":
                    pass
                case "go_to_jail":
                    state.position = 10  # Jail position
                case "no_effect":
                    pass

            await send_wsp_event(ws, WSPEvent(
                event="showDialog",
                data={
                    "promptType": "actionSpace",
                    "space": current_space.model_dump(),
                    "action": current_space.action,
                    "message": f"You landed on {current_space.name} and must perform action: {current_space.action}."
                }
            ))

    async def monopoly_move(self, ws: ServerConnection, user_id: str, session_id: str) -> None:
        
        state = self.state_manager.get_state(user_id)
        board_map = self.board_manager.get_board_map(user_id=user_id)

        if not state:
            log.error(f"User state not found for userId: {user_id}")
            await send_wsp_event(ws, WSPEvent(
                event="error",
                data={"message": "User state not found", "errorValue": user_id},
                error="stateNotFound"
            ))
            return
        
        prev_position = state.position
        state.player_move()

        # Check if passed Go
        if state.position < prev_position:
            state.add_money(200)
            await send_wsp_event(ws, WSPEvent(
                event="passedGo",
                data={"message": "You passed Go and collected $200!"}
            ))

        await state_update(ws, state)

        current_space_id = state.current_space_id
        current_space = board_map.get(current_space_id)

        await self.handle_landing(ws, state, current_space)
    
    async def buy_property(self, ws: ServerConnection, user_id: str, session_id: str) -> None:
        state = self.state_manager.get_state(user_id)
        board_map = self.board_manager.get_board_map(user_id=user_id)

        current_space_id = state.current_space_id
        current_space = board_map.get(current_space_id)

        # Validate space type
        if not isinstance(current_space, PropertySpace):
            await send_wsp_event(ws, WSPEvent(
                event="error",
                data={
                    "message": "Current space is not a property.",
                    "errorValue": current_space_id
                },
                error="invalidSpaceType"
            ))
            return

        # Deduct money
        state.subtract_money(current_space.purchase_price)

        # Set property ownership
        current_space.owned_by = user_id
        state.add_owned_property(current_space.space_id)

        # Update state
        await state_update(ws, state)

        await send_wsp_event(ws, WSPEvent(
            event="propertyPurchased",
            data={
                "property": current_space.model_dump(),
                "message": f"You purchased {current_space.name} for ${current_space.purchase_price}!"
            }
        ))
