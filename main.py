from server import handler, load_sessions, save_sessions
from utils.logger import get_logger
import websockets
import asyncio


log = get_logger("websocket_server")


async def main():
    load_sessions()
    log.info("WebSocket server running on ws://localhost:8080")
    async with websockets.serve(handler, "localhost", 8080):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        save_sessions()
        exit(0)
