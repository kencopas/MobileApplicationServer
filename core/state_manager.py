from functools import lru_cache
from typing import Dict, Any
from core.wsp_helpers import state_update
from models.game_state import UserState, GameState
from utils.session_manager import SessionManager
from config.config import SESSION_PERSIST_PATH
from utils.logger import get_logger
from utils.event_bus import get_event_bus
from core.connection_manager import get_user_websocket
from utils.wsp_utils import send_wsp_event
from models.wsp_schemas import WSPEvent


log = get_logger("state_manager")
event_bus = get_event_bus()


class StateManager:
    """Singleton class that manages user states and sessions."""
    def __init__(self):
        self.game_states: Dict[str, GameState] = {}
        self.user_states: Dict[str, UserState] = {}
        self.session_manager = SessionManager(
            persist_path=str(SESSION_PERSIST_PATH),
            log=get_logger("session_manager")
        )

    def add_player(self, online_game_id: str, user_id: str) -> None:
        """Add a player to the game state."""
        log.info(f"Adding player {user_id} to game {online_game_id}")
        state = self.get_state(online_game_id)
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
            raise ValueError(f"Game state for online_game_id {online_game_id} does not exist.")
        
        self.set_state(online_game_id, state)
    
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
        
    def create_state(self, online_game_id: str) -> GameState:
        """Create a new state for a given user."""
        log.info("Creating new state...")
        new_state = GameState(
            online_game_id=online_game_id,
            player_states={},
            game_board=[]
        )
        self.set_state(online_game_id, new_state)
        return new_state

    def get_state(self, online_game_id: str) -> GameState | None:
        """Retrieve the state for a given user."""

        cached_state = self.game_states.get(online_game_id)
        
        if cached_state:
            log.info('Fetching state from cache...')
            return cached_state
        # else:
            # log.info('Fetching state from persistent storage...')
            # state_data = self.session_manager.get_session_state(online_game_id)

        state_data = None

        if not state_data:
            return None

        retrieved_state = GameState(**state_data)
        log.warning('Overwriting cache with retrieved state... Watch for stale object references!')
        self.set_state(online_game_id, retrieved_state)  # Cache it

        return retrieved_state

    def set_state(self, online_game_id: str, state: GameState | Dict[str, Any]) -> None:
        """Set or update the state for a given user."""
        log.info("Setting state...")
        self.game_states[online_game_id] = state if isinstance(state, GameState) else GameState(**state)  # Cache
        # self.session_manager.save_session(online_game_id, online_game_id, self.game_states[online_game_id].to_dict())          # Persist


@lru_cache(maxsize=1)
def get_state_manager() -> StateManager:
    """Retrieve the global state manager instance."""
    return StateManager()


async def initialize_session(user_id: str, session_id: str, online_game_id: str) -> None:
    log.info(f"Starting session for user {user_id} with session ID {session_id}")

    state_manager = get_state_manager()
    ws = get_user_websocket(user_id)

    # Retrieve or create state
    state = state_manager.get_state(online_game_id)
    if state is None:
        state = state_manager.create_state(online_game_id)
        log.info(f"Created new state for game {online_game_id}")
        update_event = WSPEvent(
            event="sessionInitAck",
            data={"status": "newSession", "onlineGameId": online_game_id}
        )
    else:
        log.info(f"Loaded existing state for game {online_game_id}")
        update_event = WSPEvent(
            event="sessionInitAck",
            data={"status": "existingSession", "onlineGameId": online_game_id}
        )
    
    await send_wsp_event(ws, update_event)
    
    # Set the state in cache and persist it
    await event_bus.publish("state_update", user_id=user_id, online_game_id=online_game_id, state=state)


async def update_state(online_game_id: str, state: GameState) -> None:
    log.info(f"Updating state for game {online_game_id}")

    state_manager = get_state_manager()
    state_manager.set_state(online_game_id, state)
    
    for user_id in state.player_states.keys():
        ws = get_user_websocket(user_id)
        if ws:
            await state_update(ws, state)


event_bus.subscribe("session_init", initialize_session)
event_bus.subscribe("state_update", update_state)
