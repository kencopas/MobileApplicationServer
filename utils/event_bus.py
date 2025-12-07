from typing import Callable, Type, Dict, List, Optional, Protocol, Any, Awaitable
from functools import lru_cache
import inspect
from pydantic import BaseModel
from enum import Enum
from utils.logger import get_logger
from inspect import iscoroutinefunction


log = get_logger('event_bus')
_event_bus = None


class DefaultPhase(Enum):
    INPUT = 1
    RESOLUTION = 2
    EFFECTS = 3
    CLEANUP = 4


Event = BaseModel


class Command(Protocol):
    def to_event(self) -> Event:
        """Converts a command into it's corresponding Event."""
        ...


Handler = Callable[[Event], Awaitable[Command | List[Command]]]


class StateMngr(Protocol):
    def apply(self, cmd: Command) -> None:
        """Applies the necessary state changes for a given Command"""
        ...


class EventBus:

    handlers: Dict[Type, List[Handler]]
    queues: Dict[Enum, List[Event]]

    def __init__(self, state_manager: StateMngr, Phase: Optional[Type[Enum]] = None):

        if not hasattr(state_manager, 'apply'):
            raise ValueError("state_manager passed to EventBus must implement an apply method for executing commands.")

        self.state_manager = state_manager
        self.handlers = {}
        self.queues = {}
        self.Phase = Phase if Phase else DefaultPhase
    
    def on(self, event_type: Type):
        def decorator(func: Callable):
            if not iscoroutinefunction(func):
                raise ValueError("Attempted to subscribe synchronous function to EventBus use EventBus.on decorator. Event listeners must be asynchronous.")
            log.info(f"Subscribing handler {func.__name__} to event {event_type.__name__}")
            self.subscribe(event_type, func)
            return func
        return decorator

    def subscribe(self, event_type: Type, handler: Callable) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def publish(self, phase: Enum, event: Event) -> None:
        if phase not in self.queues:
            self.queues[phase] = []
        self.queues[phase].append(event)
    
    async def run_listeners(self, event: Event) -> List[Command] | None:
        """Runs all event listeners for a given event type, returns a list of commands returneed from event listeners"""
        event_type = type(event)
        if not event_type in self.handlers:
            log.error(f'Event type {event_type.__name__} not found in EventBus.handlers')
            return

        log.info(f"Running listeners for event type {event_type.__name__} with data {event.model_dump_json()}")
        event_commands: List[Command] = []
        for handler in self.handlers[event_type]:
            log.info(f"Running handler {handler.__name__}")

            handler_commands = await handler(event)
            if not handler_commands:
                log.info("Handler returned no commands. Continuing...")
                continue
            if not isinstance(handler_commands, list):
                handler_commands = [handler_commands]

            log.info(f"Handler returned commands: {', '.join([type(cmd).__name__ for cmd in handler_commands])}")
            event_commands.extend(handler_commands if handler_commands else [])

        return event_commands
    
    async def process_phase(self, phase: Enum) -> None:
        """Runs all events in a specific queue by phase enum"""

        if not phase in self.queues:
            log.info(f"Phase {phase.name} not present in current event queue. Skipping...")
            return

        log.info(f"Processing queued events for phase: {phase}")
        phase_commands: List[Command] = []
        for event in self.queues[phase]:
            event_commands = await self.run_listeners(event)
            phase_commands.extend(event_commands if event_commands else [])
        
        self.queues[phase] = []
        
        if not phase_commands:
            log.info(f'Phase {phase.name} returned no commands. Continuing...')
            return

        try:
            next_phase = type(phase)(phase.value + 1)
        except ValueError:
            log.warning("Recieved commands from the last phase type of event listeners. These commands WILL NOT be executed. Ignoring...")
            return
        
        log.info(f"Registering command events for the phase {next_phase.name}")

        for cmd in phase_commands:
            log.info(f"Applying state updates for command: {type(cmd).__name__}")
            self.state_manager.apply(cmd)
            event = cmd.to_event() if hasattr(cmd, "to_event") else None
            if event:
                log.info(f"Publishing event {type(event).__name__}")
                await self.publish(next_phase, event)
    
    async def process_all_phases(self) -> None:
        """Runs all events in each of the queues, in order of phase enum"""
        ordered_phases = sorted(self.Phase, key=lambda phase: phase.value)
        log.info(f"Processing all phases in this order: {', '.join([phase.name for phase in ordered_phases])}")
        for phase in ordered_phases:
            await self.process_phase(phase)


def initialize_event_bus(state_manager: object) -> None:
    global _event_bus
    _event_bus = EventBus(state_manager=state_manager)
    log.info("Event Bus initialized.")


def get_event_bus() -> EventBus:

    if not _event_bus:
        raise ValueError('Attempted to retrieve EventBus object before initialization.')

    return _event_bus
