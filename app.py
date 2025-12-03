from core.board_manager import initialize_board_manager, get_board_manager
from core.game_controller import GameController
from utils.logger import get_logger
from utils.wsp_utils import EventHandlerRegistry
from utils.event_bus import EventBus


state_manager = None
event_bus = EventBus()

initialize_board_manager()

game_controller = GameController()

event_handler_registry = EventHandlerRegistry(
    log=get_logger("event_handler_registry")
)
