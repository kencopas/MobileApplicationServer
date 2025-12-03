from random import random
from core.state_manager import get_state_manager
from core.wsp_helpers import state_update
from models.board_models import BoardSpace
from typing import Dict, List
from copy import deepcopy
from models.wsp_schemas import WSPEvent
from utils.event_bus import get_event_bus
from utils.logger import get_logger
from uuid import uuid4
from models.game_state import GameState
from models.board_models import space_from_json
import json
from core.connection_manager import get_user_websocket
from utils.wsp_utils import send_wsp_event


with open('data/board_data.jsonl', 'r') as f:
    BOARD_DATA = [json.loads(line) for line in f.readlines()]

template_game_board = [space_from_json(space_json) for space_json in BOARD_DATA]

log = get_logger("board_manager")
_board_manager = None
event_bus = get_event_bus()
state_manager = get_state_manager()


class BoardManager:
    def __init__(self) -> None:
        self.online_games: Dict[str, List[str]] = {}            # Maps online_game_id to list of user_ids
        self.user_games: Dict[str, str] = {}                    # Maps user_id to online_game_id
        self.boards: Dict[str, list[BoardSpace]] = {}           # Maps user_id to their board spaces
        self.board_maps: Dict[str, Dict[str, BoardSpace]] = {}  # Maps user_id to their board map
    
    def get_players(self, online_game_id: str) -> List[str]:
        """Retrieve the list of players for a given online game."""
        return self.online_games.get(online_game_id, [])

    def new_board(self, user_id: str, online_game_id: str = '') -> list[BoardSpace]:
        """Create a new board for a given user."""

        if not online_game_id:
            online_game_id = str(uuid4())
            log.info(f"Generated new online_game_id: {online_game_id}")

        # Create a new board for the online game
        board_copy = [deepcopy(space) for space in template_game_board]

        # Store the board by online_game_id
        self.boards[online_game_id] = board_copy
        self.board_maps[online_game_id] = {space.space_id: space for space in board_copy}

        # Associate the user with the online game
        self.online_games[online_game_id] = [user_id]
        self.user_games[user_id] = online_game_id

        return board_copy

    def add_player(self, online_game_id: str, user_id: str) -> None:
        """Add a player to an existing online game."""
        log.info(f"Adding player {user_id} to online game {online_game_id}")
        if online_game_id in self.online_games:
            if user_id not in self.online_games[online_game_id]:
                self.online_games[online_game_id].append(user_id)
                self.user_games[user_id] = online_game_id
        else:
            raise ValueError(f"Online game ID {online_game_id} does not exist.")

    def get_board_map(self, *, user_id: str = '', online_game_id: str = '') -> Dict[str, BoardSpace]:
        """Retrieve the board map for a given user."""

        if not online_game_id and not user_id:
            raise ValueError("Either user_id or online_game_id must be provided.")

        if user_id:
            online_game_id = self.user_games.get(user_id, '')

        return self.board_maps.get(online_game_id, {})

    def get_board(self, *, user_id: str = '', online_game_id: str = '') -> list[BoardSpace]:
        """Retrieve the board for a given user."""

        if not online_game_id and not user_id:
            raise ValueError("Either user_id or online_game_id must be provided.")

        if user_id:
            online_game_id = self.user_games.get(user_id, '')

        return self.boards.get(online_game_id, [])
    

def initialize_board_manager() -> None:
    """Initialize the singleton BoardManager."""
    global _board_manager
    if _board_manager is None:
        _board_manager = BoardManager()


def get_board_manager() -> BoardManager:
    """Singleton accessor for BoardManager."""
    if _board_manager is None:
        raise ValueError("BoardManager has not been initialized. Call initialize_board_manager first.")
    return _board_manager


async def update_board(user_id: str, online_game_id: str, state: GameState) -> None:
    """Update the board state for a given user."""
    board_manager = get_board_manager()

    if not state.game_board:
        log.info("Initializing board spaces in state...")
        state.game_board = deepcopy(template_game_board)
        await event_bus.publish("state_update", user_id=user_id, online_game_id=online_game_id, state=state)
    
    board_manager.boards[online_game_id] = state.game_board
    board_manager.board_maps[online_game_id] = {space.space_id: space for space in state.game_board}
    board_manager.add_player(online_game_id, user_id)


async def monopoly_move(user_id: str, online_game_id: str) -> None:
        
    ws = get_user_websocket(user_id)
    board_manager = get_board_manager()

    game_state = state_manager.get_state(online_game_id)
    user_state = game_state.get_player_state(user_id)
    board = board_manager.get_board(online_game_id=online_game_id)

    if not game_state:
        log.error(f"Game state not found for onlineGameId: {online_game_id}")
        await send_wsp_event(ws, WSPEvent(
            event="error",
            data={"message": "Game state not found", "errorValue": online_game_id},
            error="stateNotFound"
        ))
        return
    
    prev_position = user_state.position

    dice_roll = random.randint(1, 6) + random.randint(1, 6)
    user_state.position = (user_state.position + dice_roll) % 40  # Assuming a board with 40 spaces
    user_state.current_space_id = board[user_state.position].space_id

    # Check if passed Go
    if user_state.position < prev_position:
        user_state.money_dollars += 200
        await send_wsp_event(ws, WSPEvent(
            event="passedGo",
            data={"message": "You passed Go and collected $200!"}
        ))
    
    event_bus.publish("state_update", online_game_id=online_game_id, state=game_state)
    event_bus.publish("userLanded", user_id=user_id, online_game_id=online_game_id, space_id=user_state.current_space_id)


event_bus.subscribe("monopolyMove", monopoly_move)
event_bus.subscribe("state_update", update_board)
