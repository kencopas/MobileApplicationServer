from core.state_manager import get_state_manager

from utils.logger import get_logger
from utils.wsp_utils import EventHandlerRegistry
from utils.event_bus import EventBus, initialize_event_bus


event_handler_registry = EventHandlerRegistry(
    log=get_logger("event_handler_registry")
)

state_manager = get_state_manager()
initialize_event_bus(state_manager=state_manager)
