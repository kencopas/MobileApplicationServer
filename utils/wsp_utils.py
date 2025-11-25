from typing import Any, Callable, Optional, Dict, Awaitable
import json

from websockets import ServerConnection
from models.wsp_schemas import WSPEvent
import pydantic


EventHandler = Callable[[ServerConnection, Dict | None], Awaitable[WSPEvent]]


def validate_wsp(event_data: str) -> WSPEvent:
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
        return WSPEvent(
            event="error",
            data={"message": f"Invalid JSON format: {e}", "errorValue": str(e)},
            error="invalidJson"
        )
    except pydantic.ValidationError as e:
        raise ValueError(f"Event data validation error: {e}")


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

    def __init__(self, log: Optional[Callable]):
        if not isinstance(log, Callable):
            raise ValueError("Logger provided is not a Callable. Ensure you are passing a function or method, not an instance (e.g. log=log.info)")
        self.log = log or print
        self.handlers = {}

    def get_handler(self, event_type: str) -> EventHandler | None:
        event_handler = self.handlers.get(event_type)
        if not event_handler:
            self.log(f"No handler has been registered for the event type {event_type}")
            return
        return event_handler

    def event(self, event_type: str):

        if event_type in self.handlers:
            raise ValueError(f"A handler has already been registered for the event type {event_type}.")

        def decorator(event_handler: EventHandler) -> EventHandler:
            async def wrapper(ws: ServerConnection, event_data: Dict | None) -> WSPEvent:
                self.log(f"Executing event handler {event_handler.__name__} for event {event_type}")
                result = await event_handler(ws, event_data)
                self.log("Successfully executed event!")
                return result
            
            self.handlers[event_type] = wrapper

            return wrapper
        return decorator

    async def handle_event(self, ws: ServerConnection, event: WSPEvent) -> WSPEvent | None:
        event_handler = self.get_handler(event.event)
        if not event_handler:
            self.log(f"No handler found for event: {event.event}")
            return WSPEvent(
                event="error",
                data={"message": f"No handler found for event: {event.event}", "errorValue": event.event},
                error="invalidEvent"
            )
        return await event_handler(ws, event.data)
