import websockets
from utils.logger import get_logger
from websockets.asyncio.server import ServerConnection
from app import event_handler_registry
import core.event_handlers  # Ensure event handlers are registered
from utils.wsp_utils import validate_wsp, send_wsp_event


log = get_logger("websocket-server")

# Track all connected clients
_connected_clients = set()


async def event_router(websocket: ServerConnection) -> None:
    """Handler for websocket connections. Messages are expected to be JSON."""

    # Add client on connect
    _connected_clients.add(websocket)
    log.info(f"Client connected: {websocket}")

    try:
        # Wait for websocket events
        async for message in websocket:

            # Validate incoming message
            data = validate_wsp(message)

            log.info(f"Received:\n\n{data.model_dump_json(indent=4)}")

            response_event = await event_handler_registry.handle_event(websocket, data)

            if not response_event:
                log.info(f"No response event generated for incoming event: {data.event}")
                continue

            await send_wsp_event(websocket, response_event)

    except websockets.ConnectionClosed:
        log.info("Client disconnected")

    finally:
        # Always remove on disconnect
        if websocket in _connected_clients:
            _connected_clients.remove(websocket)
