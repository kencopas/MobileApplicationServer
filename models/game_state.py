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
    current_turn: int = 0 # Player list index of the player whose turn it is
    current_turn_uid: str = ''
    
    def to_dict(self) -> Dict:
        return self.model_dump()
