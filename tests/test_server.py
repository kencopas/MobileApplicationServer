import websockets
from utils.logger import get_logger
from websockets.asyncio.server import ServerConnection
from rich import print_json
import yaml
import json
from pathlib import Path


# Track all connected clients
_connected_clients = set()

log = get_logger("test-server")
CURRENT_DIR = Path(__file__).parent


async def event_router(websocket: ServerConnection) -> None:
    """Handler for websocket connections. Messages are expected to be JSON."""

    # Add client on connect
    _connected_clients.add(websocket)
    log.info(f"Client connected: {websocket}")

    try:
        # Wait for websocket events
        async for message in websocket:
            print_json(message)
            with open(str(CURRENT_DIR / 'event.yaml'), 'r') as f:
                event_data = yaml.safe_load(f)
            log.info(f'Sending test event {event_data.get('event')}')
            await websocket.send(message=json.dumps(event_data))

    except websockets.ConnectionClosed:
        log.info("Client disconnected")

    finally:
        # Always remove on disconnect
        if websocket in _connected_clients:
            _connected_clients.remove(websocket)
