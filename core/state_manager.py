from functools import lru_cache
from typing import Dict, Any, List
from copy import deepcopy

from config.config import SESSION_PERSIST_PATH, template_game_board

from models.game_state import UserState, GameState
from models.commands import StateCommand, MovePlayer

from utils.session_manager import SessionManager
from utils.logger import get_logger


log = get_logger("state_manager")


class StateManager:
    """Singleton class that manages user states and sessions."""
    def __init__(self):
        self.game_states: Dict[str, GameState] = {}
        self.user_states: Dict[str, UserState] = {}
        self.user_games: Dict[str, GameState] = {}
        self.session_manager = SessionManager(
            persist_path=str(SESSION_PERSIST_PATH),
            log=get_logger("session_manager")
        )

    def initialize_session(self, user_id: str, game_id: str) -> None:
        user_state = self.get_player_state(user_id)
        game_state = self.create_state(game_id)
        self.add_player(game_id=game_id, user_id=user_id)

    def update_user_state(self, user_id: str, user_state: UserState):
        self.user_states[user_id] = user_state
    
    def update_game_state(self, game_id: str, game_state: GameState):
        self.game_states[game_id] = game_state
    
    def apply(self, command: StateCommand):
        
        user_id = command.user_id
        game_id = command.game_id
        game_state = self.game_states.get(game_id)
        user_state = self.user_states.get(user_id)

        if isinstance(command, MovePlayer):
            new_space = game_state.game_board[command.new_position]
            user_state.position = command.new_position
            user_state.current_space_id = new_space.space_id
            game_state.game_board[command.new_position].visual_properties.occupied_by = user_state.user_id
            self.update_game_state(game_id, game_state)
            self.update_user_state(user_id, user_state)


    def apply_all(self, commands: List[StateCommand]):
        for command in commands:
            self.apply(command)

    def add_player(self, game_id: str, user_id: str) -> None:
        """Add a player to the game state."""
        log.info(f"Adding player {user_id} to game {game_id}")
        state = self.get_state(game_id)
        if state:
            if user_id not in state.player_states:
                state.player_states[user_id] = UserState(
                    user_id=user_id,
                    money_dollars=1500,
                    position=0,
                    current_space_id='go',
                    owned_properties=[]
                )
        else:
            raise ValueError(f"Game state for game_id {game_id} does not exist.")
        
        self.set_state(game_id, state)
    
    def initialize_state(self, initial_state: Dict) -> None:
        """Initialize state for a given user."""
        log.info("Initializing state...")
        try:
            user_id = initial_state.get("user_id") or initial_state.get("userId")
            if not user_id:
                raise ValueError("Initial state must contain 'user_id' key.")
            
            state_object = UserState(**initial_state)
            self.update_user_state(user_id, state_object)
        except TypeError as e:
            # Handle the case where initial_state has unexpected keys
            raise ValueError(f"Invalid initial state data: {e}")
        
    def create_state(self, game_id: str) -> GameState:
        """Create a new state for a given user."""
        log.info("Creating new state...")
        new_state = GameState(
            game_id=game_id,
            player_states={},
            game_board=[deepcopy(space) for space in template_game_board]
        )
        self.set_state(game_id, new_state)
        return new_state
    
    def get_player_state(self, user_id: str) -> UserState | None:
        return self.user_states.get(user_id)

    def get_state(self, game_id: str) -> GameState | None:
        """Retrieve the state for a given game."""

        cached_state = self.game_states.get(game_id)
        
        if cached_state:
            log.info('Fetching state from cache...')
            return cached_state
        # else:
            # log.info('Fetching state from persistent storage...')
            # state_data = self.session_manager.get_session_state(game_id)

        state_data = None

        if not state_data:
            return None

        retrieved_state = GameState(**state_data)
        log.warning('Overwriting cache with retrieved state... Watch for stale object references!')
        self.set_state(game_id, retrieved_state)  # Cache it

        return retrieved_state

    def set_state(self, game_id: str, state: GameState | Dict[str, Any]) -> None:
        """Set or update the state for a given user."""
        log.info("Setting state...")
        self.game_states[game_id] = state if isinstance(state, GameState) else GameState(**state)  # Cache
        # self.session_manager.save_session(game_id, game_id, self.game_states[game_id].to_dict())          # Persist


@lru_cache(maxsize=1)
def get_state_manager() -> StateManager:
    """Retrieve the global state manager instance."""
    return StateManager()
