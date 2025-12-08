from logging import Logger
from typing import Any, Callable, Optional, Dict, Awaitable
import json

from websockets import ServerConnection
from models.wsp_schemas import WSPEvent
import pydantic


EventHandler = Callable[[ServerConnection, Dict | None], Awaitable[WSPEvent]]


def get_missing_fields(data: Dict | None, required_fields: list[str]) -> list[str]:
    """Check for missing required fields in the provided data dictionary.
    
    Args:
        data (Dict | None): The data dictionary to check.
        required_fields (list[str]): A list of required field names.
    
    Returns:
        list[str]: A list of missing field names.
    """
    if data is None:
        return required_fields
    
    missing_fields = [field for field in required_fields if field not in data]
    return missing_fields


def validate_wsp(event_data: str, required_fields: list[str] | None = None) -> WSPEvent:
    """Validate incoming event data against WSPEvent schema.
    
    Args:
        event_data (str): The raw event data as a JSON string.
    
    Returns:
        WSPEvent: The validated WSPEvent object.
    
    Raises:
        pydantic.ValidationError: If the event data does not conform to the WSPEvent schema.
    """
    try:
        event_dict = json.loads(event_data)
        event = WSPEvent.model_validate(event_dict)
        return event
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}")
    except pydantic.ValidationError as e:
        raise ValueError(f"Event data validation error: {e}")


async def send_wsp_event(ws: ServerConnection, event: WSPEvent) -> None:
    """Send a WSPEvent over a WebSocket connection.
    
    Args:
        ws (ServerConnection): The WebSocket connection to send the event through.
        event (WSPEvent): The WSPEvent object to send.
    """
    if not validate_wsp(event.model_dump_json()):
        raise ValueError("Invalid WSPEvent data")
    await ws.send(event.model_dump_json())


class EventHandlerRegistry:
    """Class used for registering and routing event handlers.
    
    Use case:
    ```
    elr = EventHandlerRegistry(log=log.info)

    @elr.event("roll_dice")
    def dice_roll() -> int:
        return random.randint(0, 6)
    
    @elr.event("get_username")
    def username_request() -> str:
        return "ken.copas"
    
    def handle_event(event_type: str, *args, **kwargs) -> Any:
        event_handler: Callable = elr.get_handler(event_type)
        return event_handler(*args, **kwargs)
    
    ```
    """

    def __init__(self, log: Logger):
        self.log = log
        self.handlers = {}

    def get_handler(self, event_type: str) -> EventHandler | None:
        event_handler = self.handlers.get(event_type)
        if not event_handler:
            self.log.info(f"No handler has been registered for the event type {event_type}")
            return
        return event_handler

    def event(self, event_type: str):

        if event_type in self.handlers:
            raise ValueError(f"A handler has already been registered for the event type {event_type}.")

        def decorator(event_handler: EventHandler) -> EventHandler:
            async def wrapper(ws: ServerConnection, game_id: str, user_id: str, data: Dict | None) -> WSPEvent:
                self.log.info(f"Executing event handler {event_handler.__name__} for event {event_type}")
                result = await event_handler(
                    ws=ws,
                    game_id=game_id,
                    user_id=user_id,
                    data=data
                )
                self.log.info("Successfully executed event!")
                return result
            
            self.handlers[event_type] = wrapper

            return wrapper
        return decorator

    async def handle_event(self, ws: ServerConnection, user_id: str, game_id: str, event: WSPEvent) -> WSPEvent | None:
        event_handler = self.get_handler(event.event)
        if not event_handler:
            self.log.error(f"No handler found for event: {event.event}")
            return WSPEvent(
                event="error",
                data={"message": f"No handler found for event: {event.event}", "errorValue": event.event},
                error="invalidEvent"
            )
        return await event_handler(
            ws=ws,
            user_id=user_id,
            game_id=game_id,
            data=event.data
        )
