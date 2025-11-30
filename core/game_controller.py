from utils.wsp_utils import send_wsp_event
from .board_space import BoardSpace, PropertySpace, ActionSpace
from .user_state import UserState
from .state_manager import StateManager
from .wsp_helpers import state_update
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
        state = self.state_manager.get_state(user_id)
        if state is None:
            log.error(f"Cannot save game: No state found for user_id {user_id}")
            return
        
        self.state_manager.set_state(user_id, session_id, state)
    
    def start_session(self, user_id: str, session_id: str) -> None:
        """Start or restore a session for a user."""
        log.info(f"Starting session for user {user_id} with session ID {session_id}")

        # Retrieve or create state
        state = self.state_manager.get_state(user_id)
        if state is None:
            state = UserState(user_id=user_id, board_spaces=self.board)
        
        # Set the state in cache and persist it
        self.state_manager.set_state(user_id, session_id, state)

    async def monopoly_move(self, ws: ServerConnection, user_id: str, session_id: str) -> None:
        
        state = self.state_manager.get_state(user_id)
        state.player_move()

        await state_update(ws, state)

        current_space_id = state.current_space_id
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
