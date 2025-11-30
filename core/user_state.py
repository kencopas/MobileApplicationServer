from typing import Any, Dict, List
from .board_space import BoardSpace
from copy import deepcopy
from utils.logger import get_logger
import random


log = get_logger("user_state")


class UserState:
    """
    {
  ///   "user_id": String,
  ///   "money_dollars": int,
  ///   "position": int,
  ///   "current_space_id": String,
  ///   "board_spaces": [
  ///     {
  ///       "name": String,
  ///       "space_type": String,
  ///       "space_id": String,
  ///       "space_index": int,
  ///       "visual_properties": {
  ///         "color": String?,
  ///         "icon": String?,
  ///         "description": String?,
  ///         "occupied_by": String?
  ///       }
  ///     },
  ///     ...
  ///   ],
  /// }
    """

    user_id: str
    money_dollars: int
    position: int = 0
    current_space_id: str
    _board_spaces: List[BoardSpace] = []

    def __init__(self, user_id: str, money_dollars: int = 0, position: int = 0, current_space_id: str = "", board_spaces: List[BoardSpace] | List[Dict] = []):
        self.user_id = user_id
        self.money_dollars = money_dollars
        self.position = position
        self.current_space_id = current_space_id
        self._board_spaces = self.construct_board_space(board_spaces)

    @property
    def board_spaces(self) -> List[BoardSpace]:
        # Update board spaces to reflect current user state
        for i, space in enumerate(self._board_spaces):
            if self.position == space.space_index:
                self._board_spaces[i].visual_properties.occupied_by = "Player"
            else:
                self._board_spaces[i].visual_properties.occupied_by = None

        return self._board_spaces

    def construct_board_space(self, board_spaces: List[BoardSpace] | List[Dict]) -> List[BoardSpace]:
        constructed_spaces = []
        for space in board_spaces:
            if isinstance(space, BoardSpace):
                constructed_spaces.append(space)
            elif isinstance(space, dict):
                constructed_spaces.append(BoardSpace(**space))
        return constructed_spaces

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        data = deepcopy(self.__dict__)
        if "_board_spaces" in data:
            del data["_board_spaces"]
        if self.board_spaces:
            data["board_spaces"] = [space.model_dump() for space in self.board_spaces]
        return data
    
    def add_money(self, amount: int) -> None:
        log.info(f"Adding {amount} to user {self.user_id}'s money")
        self.money_dollars += amount

    def subtract_money(self, amount: int) -> None:
        log.info(f"Subtracting {amount} from user {self.user_id}'s money")
        self.money_dollars -= amount
    
    def player_move(self) -> None:
        """Simulate a dice roll and return the total move spaces."""
        roll = random.randint(1, 6) + random.randint(1, 6)
        log.info(f"User {self.user_id} rolled a {roll}")
        self.update_position(roll)

    def update_position(self, spaces: int) -> None:
        """Move the player's position on the board, updates current space accordingly."""
        log.info(f"Moving position for user {self.user_id} by {spaces} spaces")
        self.position = (self.position + spaces) % 40  # Assuming a board with 40 spaces
        self.update_current_space(self.board_spaces[self.position].space_id)
    
    def update_current_space(self, board_space_id: str) -> None:
        log.info(f"Updating current space for user {self.user_id} to {board_space_id}")
        self.current_space_id = board_space_id
