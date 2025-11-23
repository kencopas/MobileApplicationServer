from typing import Callable, Optional


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

    def get_handler(self, event_type: str) -> Callable | None:
        event_handler = self.handlers.get(event_type)
        if not event_handler:
            self.log(f"No handler has been registered for the event type {event_type}")
            return
        return event_handler

    def event(self, event_type: str):

        if event_type in self.handlers:
            raise ValueError(f"A handler has already been registered for the event type {event_type}.")

        def decorator(event_handler: Callable):
            def wrapper(*args, **kwargs):
                self.log(f"Executing event handler {event_handler.__name__} for event {event_type}")
                result = event_handler(*args, **kwargs)
                self.log("Successfully executed event!")
                return result
            
            self.handlers[event_type] = wrapper

            return wrapper
        return decorator
