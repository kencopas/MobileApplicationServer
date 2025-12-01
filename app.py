from core.board_manager import BoardManager
from core.game_controller import GameController
from core.board_space import space_from_json
from core.state_manager import StateManager
from utils.logger import get_logger
from utils.session_manager import SessionManager
from utils.wsp_utils import EventHandlerRegistry
from config.config import SESSION_PERSIST_PATH
import json


with open('data/board_data.jsonl', 'r') as f:
    BOARD_DATA = [json.loads(line) for line in f.readlines()]

state_manager = StateManager()

board_manager = BoardManager(
    board_spaces=[space_from_json(space_json) for space_json in BOARD_DATA]
)

game_controller = GameController(
    board_manager=board_manager,
    state_manager=state_manager
)

event_handler_registry = EventHandlerRegistry(
    log=get_logger("event_handler_registry")
)
