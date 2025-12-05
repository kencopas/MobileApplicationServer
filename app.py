from core.board_manager import initialize_board_manager
from core.state_manager import StateManager
from core.game_controller import GameController
from utils.logger import get_logger
from utils.wsp_utils import EventHandlerRegistry
from utils.event_bus import EventBus


event_handler_registry = EventHandlerRegistry(
    log=get_logger("event_handler_registry")
)

event_bus = EventBus()
state_manager = StateManager(bus=event_bus)

initialize_board_manager()

game_controller = GameController()
