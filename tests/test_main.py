from tests.test_server import event_router
from utils.logger import get_logger
import websockets
import asyncio


log = get_logger("test-main")


async def main():
    log.info("WebSocket server running on ws://localhost:8080")
    async with websockets.serve(event_router, "0.0.0.0", 8080):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)
