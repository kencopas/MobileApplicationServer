from typing import Dict, Type, Any
from .user_state import UserState


class StateManager:
    def __init__(self):
        self.user_states: Dict[str, UserState] = {}
    
    def initialize_state(self, initial_state: Dict) -> None:
        """Initialize state for a given user."""

        try:
            user_id = initial_state.get("user_id")
            if not user_id:
                raise ValueError("Initial state must contain 'user_id' key.")
            state_object = UserState(**initial_state)
            self.set_state(user_id, state_object)
        except TypeError as e:
            # Handle the case where initial_state has unexpected keys
            raise ValueError(f"Invalid initial state data: {e}")

    def get_state(self, user_id: str) -> UserState | None:
        """Retrieve the state for a given user."""
        return self.user_states.get(user_id, None)

    def set_state(self, user_id: str, state: UserState) -> None:
        """Set or update the state for a given user."""
        self.user_states[user_id] = state
