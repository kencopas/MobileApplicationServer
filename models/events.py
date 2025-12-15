from typing import Dict, Optional
from pydantic import BaseModel
from models.board_models import PropertySpace, BoardSpace


class GameEvent(BaseModel):
    game_id: str
    user_id: Optional[str]

    @property
    def ids(self) -> Dict:
        return {
            'game_id': self.game_id,
            'user_id': self.user_id
        }


class SessionInit(GameEvent):
    user_id: str
    session_id: str


class PlayerRollDice(GameEvent):
    dice_roll: int


class PlayerMoved(GameEvent):
    old_position: int
    new_position: int
    space: BoardSpace


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


class PayedRent(GameEvent):
    opponent_id: str
    rent_dollars: int
