import asyncio
import websockets
from utils.logger import get_logger
from websockets.asyncio.server import ServerConnection
import json
from schemas.wsp_schemas import WSPEvent
import pydantic
from event_handlers import elr


log = get_logger("websocket-server")

# Track all connected clients
connected_clients = set()
SESSIONS = {}  # sessionId -> {websocket, data...}


def save_sessions():
    with open("sessions.json", "w") as f:
        json.dump({sid: data["state"] for sid, data in SESSIONS.items()}, f)


def load_sessions():
    try:
        with open("sessions.json") as f:
            states = json.load(f)
            for sid, state in states.items():
                SESSIONS[sid] = {"ws": None, "state": state}
    except FileNotFoundError:
        pass


def update_state(session_id: str, event: WSPEvent):
    if session_id is None:
        log.error("update_state called with session_id=None")
        return

    if session_id not in SESSIONS:
        log.error(f"update_state called for unknown session: {session_id}")
        return

    SESSIONS[session_id]["state"].append(event.model_dump())


async def handle_session_init(ws, event: WSPEvent):
    session_id = event.data.get("sessionId")

    if session_id is None:
        log.error("session_init missing sessionId")
        return
    
    # Attach to websocket
    ws.session_id = session_id

    # Restore or create
    if session_id in SESSIONS:
        log.info(f"Session restored: {session_id}")
        SESSIONS[session_id]["ws"] = ws

    else:
        log.info(f"New session created: {session_id}")
        SESSIONS[session_id] = {
            "ws": ws,
            "state": [],
        }

    # Respond
    await ws.send(json.dumps({
        "event": "session_ack",
        "data": {
            "sessionId": session_id,
            "state": SESSIONS[session_id]["state"]
        }
    }))


async def dispatch_event(ws, event: WSPEvent):
    if event.event == "session_init":
        await handle_session_init(ws, event)
        return False  # don't broadcast this
        
    return True  # broadcast everything else for now


async def handler(websocket: ServerConnection):
    """Handler for websocket connections. Messages are expected to be JSON."""

    # Add client on connect
    connected_clients.add(websocket)
    log.info(f"Client connected: {websocket}")

    try:
        async for message in websocket:
            try:
                raw_data = json.loads(message)
                data = WSPEvent(**raw_data)
            except (json.JSONDecodeError, pydantic.ValidationError) as e:
                log.error(f"Invalid message: {message}\n{e}")
                continue

            log.info(f"Received:\n\n{data.model_dump_json(indent=4)}")

            # FIRST: dispatch the event (this sets websocket.session_id)
            do_broadcast = await dispatch_event(websocket, data)

            # SECOND: NOW extract session_id AFTER session_init runs
            session_id = getattr(websocket, "session_id", None)

            # THIRD: update state ONLY if session_id exists
            if session_id:
                update_state(session_id, data)
            else:
                log.error("update_state called with session_id=None")

            # FOURTH: optionally broadcast
            if not do_broadcast:
                continue

            for client in list(connected_clients):
                try:
                    await client.send(data.model_dump_json())
                except Exception as e:
                    log.error(f"Removing broken websocket: {e}")
                    connected_clients.remove(client)

    except websockets.ConnectionClosed:
        log.info("Client disconnected")

    finally:
        # Always remove on disconnect
        if websocket in connected_clients:
            connected_clients.remove(websocket)
