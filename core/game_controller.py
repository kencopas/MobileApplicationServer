from utils.wsp_utils import send_wsp_event
from .board_space import BoardSpace, PropertySpace, ActionSpace
from .user_state import UserState
from .state_manager import StateManager
import random
from models.wsp_schemas import WSPEvent
from utils.logger import get_logger
from typing import Literal
from websockets.asyncio.server import ServerConnection


log = get_logger("game_controller")


class GameController:
    """Singleton class that manages game logic with session state and board."""
    def __init__(self, board: list[BoardSpace], state_manager: StateManager):
        self.board = self._sort_board(board)
        self.state_manager = state_manager

    def _sort_board(self, board: list[BoardSpace]) -> list[BoardSpace]:
        """Sort the board spaces based on their space_id."""
        return sorted(board, key=lambda space: space.space_index)

    def save_game(self, user_id: str, session_id: str) -> None:
        """Save the current game state for a user."""
        log.info(f"Saving game for user_id {user_id} and session_id {session_id}")
        state = self.get_state(user_id)
        if state is None:
            log.error(f"Cannot save game: No state found for user_id {user_id}")
            return
        
        self.state_manager.set_state(user_id, session_id, state)
    
    def move_player(self, user_id: str, session_id: str) -> None:
        """Move a player based on a dice roll and update the current space."""
        
        player_state = self.get_state(user_id)
        if player_state is None:
            log.error(f"Cannot move player: No state found for user_id {user_id}")
            return

        roll = random.randint(1, 6) + random.randint(1, 6)
        log.info(f"Player {user_id} rolled a {roll}. Moving...")
        player_state.move_position(roll)

        self.state_manager.set_state(user_id, session_id, player_state)
    
    def get_state(self, user_id: str) -> UserState | None:
        """Get the current state for a user."""
        return self.state_manager.get_state(user_id)
    
    def start_session(self, user_id: str, session_id: str) -> None:
        """Start or restore a session for a user."""
        log.info(f"Starting session for user {user_id} with session ID {session_id}")

        # Retrieve or create state
        state = self.state_manager.get_state(user_id)
        if state is None:
            state = UserState(user_id=user_id, board_spaces=self.board)
        
        # Set the state in cache and persist it
        self.state_manager.set_state(user_id, session_id, state)

    async def handle_landing(self, ws: ServerConnection, user_id: str, session_id: str) -> None:
        self.move_player(user_id, session_id)
        state = self.get_state(user_id)

        await send_wsp_event(ws, WSPEvent(
            event="stateUpdate",
            data={
                "state": state.to_dict()
            }
        ))

        player_state = self.get_state(user_id)
        current_space_id = player_state.current_space_id
        current_space = next((space for space in self.board if space.space_id == current_space_id), None)
        if isinstance(current_space, PropertySpace):
            return WSPEvent(
                event="landedOnProperty",
                data={
                    "property": current_space.model_dump(),
                    "message": f"You landed on {current_space.name}."
                }
            )
        elif isinstance(current_space, ActionSpace):
            action = current_space.action

            return WSPEvent(
                event="landedOnActionSpace",
                data={
                    "action": current_space.action,
                    "message": f"You landed on {current_space.name} and must perform action: {current_space.action}."
                }
            )
