from typing import Dict, Type, Any
from .user_state import UserState


class StateManager:
    def __init__(self):
        self.user_states: Dict[str, UserState] = {}
    
    def initialize_state(self, user_id: str, initial_state: Dict) -> None:
        """Initialize state for a given user."""

        try:
            state_object = UserState(user_id=user_id, **initial_state)
            self.user_states[user_id] = state_object
        except TypeError as e:
            # Handle the case where initial_state has unexpected keys
            raise ValueError(f"Invalid initial state data: {e}")

    def get_state(self, user_id: str) -> UserState | None:
        """Retrieve the state for a given user."""
        return self.user_states.get(user_id, None)
