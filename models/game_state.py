from typing import Dict, List
from models.board_models import BoardSpace
from pydantic import BaseModel
import random


class UserState(BaseModel):
    """Class representing the state of a user in the game."""
    user_id: str
    money_dollars: int
    position: int = 0
    current_space_id: str
    owned_properties: List[str] = []


class GameState(BaseModel):
    """Placeholder for future game state management."""
    game_id: str
    player_states: Dict[str, UserState]  # Maps user_id to UserState
    game_board: List[BoardSpace]

    def get_player_state(self, user_id: str) -> UserState | None:
        """Retrieve the UserState for a given user_id."""
        return self.player_states.get(user_id)

    def update_player_state(self, user_id: str, new_state: UserState) -> None:
        """Update the UserState for a given user_id."""
        self.player_states[user_id] = new_state
    
    def to_dict(self) -> Dict:
        return self.model_dump()
