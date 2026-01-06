from typing import Dict, Set
import secrets
import string
from pydantic import BaseModel, Field

from utils.logger import get_logger


def generate_room_code(length: int = 6) -> str:
    """Creates a 6-character alphanumeric string as a room code"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


log = get_logger("room_manager")


class Room(BaseModel):
    room_id: str
    host: str
    members: Set[str] = Field(default_factory=Set, description="The player IDs of players within a room (includes the host)")

    def add_player(self, player_id: str) -> None:
        self.members.add(player_id)
    
    def remove_player(self, player_id: str) -> None:
        self.members.remove(player_id)
    
    def has_player(self, player_id: str) -> bool:
        return player_id in self.members


class RoomManager:
    rooms: Dict[str, Room]
    players: Dict[str, str | None]

    def __init__(self):
        self.rooms = {}
        self.players = {}
    
    def join_room(self, room_id: str, player_id: str) -> None:
        if not room_id in self.rooms:
            raise ValueError(f"Player {player_id} attempted to join non-existent room {room_id}.")
        if self.rooms[room_id].has_player(player_id):
            log.warning(f"Player {player_id} attempted to join room {room_id} which they are already in.")
            return
        self.rooms[room_id].add_player(player_id)
        self.players[player_id] = room_id

    def leave_room(self, room_id: str, player_id: str) -> None:
        if not room_id in self.rooms:
            raise ValueError(f"Player {player_id} attempted to leave non-existent room {room_id}")
        if not self.rooms[room_id].has_player(player_id):
            log.warning(f"Player {player_id} attempted to leave room {room_id} which they are not in.")
            return
        self.rooms[room_id].remove_player(player_id)
        self.players[player_id] = None
    
    def create_room(self, player_id: str) -> str:
        if self.players.get(player_id):
            log.warning(f"Player {player_id} attempted to create a room while currently in another room.")
            return
        
        # Create unique room code
        room_code = generate_room_code()
        while room_code in self.rooms:
            room_code = generate_room_code()
        
        # Create room
        self.rooms[room_code] = Room(
            room_id=room_code,
            host=player_id,
            members={player_id}
        )
        self.players[player_id] = room_code

        return room_code
