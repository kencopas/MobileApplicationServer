from typing import Any, Dict
from .board_space import BoardSpace
from copy import deepcopy


class UserState:

    user_id: Dict[str, Any]
    money_dollars: int
    position: int = 0
    current_space: BoardSpace

    def __init__(self, user_id: str, money_dollars: int = 0, position: int = 0, current_space: BoardSpace = None):
        self.user_id = user_id
        self.money_dollars = money_dollars
        self.position = position
        self.current_space = current_space

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        data = deepcopy(self.__dict__)
        if self.current_space:
            data["current_space"] = self.current_space.model_dump()
        return data
    
    def add_money(self, amount: int) -> None:
        self.money_dollars += amount

    def subtract_money(self, amount: int) -> None:
        self.money_dollars -= amount
    
    def move_position(self, spaces: int) -> None:
        self.position = (self.position + spaces) % 40  # Assuming a board with 40 spaces
    
    def update_current_space(self, board_space: BoardSpace) -> None:
        self.current_space = board_space
