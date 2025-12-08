from typing import List, Optional
from pydantic import BaseModel
from models.board_models import PropertySpace


class GameEvent(BaseModel):
    game_id: str
    user_id: Optional[str]


class SessionInit(GameEvent):
    user_id: str
    session_id: str


class PlayerRollDice(GameEvent):
    dice_roll: int


class PlayerMoved(GameEvent):
    old_position: int
    new_position: int


class LandedOnUnownedSpace(GameEvent):
    user_position: int
    space: PropertySpace


class LandedOnSelfOwnedSpace(GameEvent):
    user_position: int
    space: PropertySpace


class LandedOnOpponentSpace(GameEvent):
    user_position: int
    space: PropertySpace


class PurchasedProperty(GameEvent):
    space: PropertySpace
