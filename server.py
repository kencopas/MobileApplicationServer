import websockets
from utils.logger import get_logger
from websockets.asyncio.server import ServerConnection
from app.event_handlers import elr
from utils.wsp_utils import validate_wsp


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

            response_event = await elr.handle_event(websocket, data)

            if not response_event:
                log.warning(f"No response event generated for incoming event: {data.event}")
                continue

            await websocket.send(response_event.model_dump_json())

    except websockets.ConnectionClosed:
        log.info("Client disconnected")

    finally:
        # Always remove on disconnect
        if websocket in _connected_clients:
            _connected_clients.remove(websocket)
