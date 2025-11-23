from utils.logger import get_logger
from utils.wsp_utils import EventHandlerRegistry


log = get_logger("websocket-server")
elr = EventHandlerRegistry(log=log.info)


@elr.event("roll_dice")
def roll_dice_handler():
    return "You rolled 6!"


@elr.event("get_secret")
def get_secret_handler():
    return "super_cool_secret123"
