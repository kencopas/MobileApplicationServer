from typing import List, Optional
from pydantic import BaseModel


class GameEvent(BaseModel):
    online_game_id: str
    user_id: Optional[str]


class PlayerRollDice(GameEvent):
    dice_roll: int


class PlayerPositionUpdate(GameEvent):
    old_position: int
    new_position: int
