from typing import List, Optional
from pydantic import BaseModel
from models.events import PlayerMoved, GameEvent
from models.board_models import PropertySpace


class StateCommand(BaseModel):
    game_id: str
    user_id: Optional[str] = ""

    def to_event(self) -> GameEvent:
        ...


class MovePlayer(StateCommand):
    old_position: int
    new_position: int

    def to_event(self) -> PlayerMoved:
        return PlayerMoved(**self.__dict__)


class BuyProperty(StateCommand):
    space: PropertySpace


class ModifyFunds(StateCommand):
    money_dollars: int
    """The amount of money the user's balance should increase/decrease by"""
