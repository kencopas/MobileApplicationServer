from typing import Callable
from functools import lru_cache
import inspect


class EventBus:
    def __init__(self):
        self.handlers = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def publish(self, event_type: str, *args, **kwargs):
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                if inspect.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)


@lru_cache(maxsize=1)
def get_event_bus() -> EventBus:
    return EventBus()
