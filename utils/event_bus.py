from typing import Callable, Type, Dict, List, Optional
from functools import lru_cache
import inspect
from pydantic import BaseModel
from enum import Enum
from utils.logger import get_logger


log = get_logger('event_bus')


class DefaultPhase(Enum):
    INPUT = 1
    RESOLUTION = 2
    EFFECTS = 3
    CLEANUP = 4


class EventBus:

    handlers: Dict[Type, List[Callable]]
    queues: Dict[Enum, List[BaseModel]]

    def __init__(self, Phase: Optional[Type[Enum]] = None):
        self.handlers = {}
        self.queues = {}
        self.Phase = Phase if Phase else DefaultPhase
    
    def on(self, event_type: Type):
        async def decorator(func):
            self.subscribe(event_type, func)
            return func
        return decorator

    def subscribe(self, event_type: Type, handler: Callable) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def publish(self, phase: Enum, event: BaseModel) -> None:
        if phase not in self.queues:
            self.queues[phase] = []
        self.queues[phase].append(event)
    
    async def run_listeners(self, event: BaseModel) -> None:
        """Runs all event listeners for a given event type"""
        event_type = type(event)
        log.info(f"Running listeners for event type {event_type} with data {event.model_dump_json()}")
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                log.info(f"Running handler {handler.__name__}")
                await handler(event)
    
    async def process_phase(self, phase: Enum) -> None:
        """Runs all events in a specific queue by phase enum"""
        log.info(f"Processing queued events for phase: {phase}")
        for event in self.queues[phase]:
            await self.run_listeners(event)
    
    async def process_all_phases(self) -> None:
        """Runs all events in each of the queues, in order of phase enum"""
        ordered_phases = sorted(self.Phase, key=lambda phase: phase.value)
        log.info(f"Processing all phases in this order: {', '.join([phase.name for phase in ordered_phases])}")
        for phase in ordered_phases:
            await self.process_phase(phase)


@lru_cache(maxsize=1)
def get_event_bus() -> EventBus:
    return EventBus()
