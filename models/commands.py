from typing import List, Optional
from pydantic import BaseModel
from models.events import PlayerMoved


class StateCommand(BaseModel):
    game_id: str
    user_id: Optional[str] = ""


class MovePlayer(StateCommand):
    old_position: int
    new_position: int

    def to_event(self) -> PlayerMoved:
        return PlayerMoved(**self.__dict__)
