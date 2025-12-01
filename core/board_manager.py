from core.board_space import BoardSpace
from typing import Dict, List
from copy import deepcopy
from utils.logger import get_logger
from uuid import uuid4


log = get_logger("board_manager")


class BoardManager:
    def __init__(self, board_spaces: list[BoardSpace]):
        self.online_games: Dict[str, List[str]] = {}            # Maps online_game_id to list of user_ids
        self.user_games: Dict[str, str] = {}                    # Maps user_id to online_game_id
        self.boards: Dict[str, list[BoardSpace]] = {}           # Maps user_id to their board spaces
        self.board_maps: Dict[str, Dict[str, BoardSpace]] = {}  # Maps user_id to their board map
        self.board_spaces = board_spaces                        # Template board spaces
    
    def new_board(self, user_id: str, online_game_id: str = '') -> list[BoardSpace]:
        """Create a new board for a given user."""

        if not online_game_id:
            online_game_id = str(uuid4())
            log.info(f"Generated new online_game_id: {online_game_id}")

        # Create a new board for the online game
        board_copy = [deepcopy(space) for space in self.board_spaces]

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
