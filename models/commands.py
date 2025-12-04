from typing import List, Optional
from pydantic import BaseModel


class StateCommand(BaseModel):
    online_game_id: str
    user_id: Optional[str]


class MovePlayer(StateCommand):
    old_position: int
    new_position: int
