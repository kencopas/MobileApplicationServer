from typing import Dict, Type, Any
from .user_state import UserState
from utils.session_manager import SessionManager
from config.config import SESSION_PERSIST_PATH
from utils.logger import get_logger
from logging import Logger


log = get_logger("state_manager")


class StateManager:
    """Singleton class that manages user states and sessions."""
    def __init__(self):
        self.user_states: Dict[str, UserState] = {}
        self.session_manager = SessionManager(
            persist_path=str(SESSION_PERSIST_PATH),
            log=get_logger("session_manager")
        )
    
    def initialize_state(self, initial_state: Dict) -> None:
        """Initialize state for a given user."""
        log.info("Initializing state...")
        try:
            user_id = initial_state.get("user_id") or initial_state.get("userId")
            if not user_id:
                raise ValueError("Initial state must contain 'user_id' key.")
            
            state_object = UserState(**initial_state)
            self.set_state(user_id, state_object)
        except TypeError as e:
            # Handle the case where initial_state has unexpected keys
            raise ValueError(f"Invalid initial state data: {e}")

    def get_state(self, user_id: str) -> UserState | None:
        """Retrieve the state for a given user."""

        cached_state = self.user_states.get(user_id)
        
        if cached_state:
            log.info('Fetching state from cache...')
            state_data = cached_state.to_dict()
        else:
            log.info('Fetching state from persistent storage...')
            state_data = self.session_manager.get_session_state(user_id)

        if state_data is None:
            return None

        return UserState(**state_data) if state_data else None

    def set_state(self, user_id: str, session_id: str, state: UserState | Dict[str, Any]) -> None:
        """Set or update the state for a given user."""
        log.info("Setting state...")
        self.user_states[user_id] = state if isinstance(state, UserState) else UserState(**state)  # Cache
        self.session_manager.save_session(user_id, session_id, self.user_states[user_id].to_dict())          # Persist
