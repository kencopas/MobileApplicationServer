import asyncio
import websockets


# Track all connected clients
connected_clients = set()


async def handler(websocket):
    # Add client on connect
    connected_clients.add(websocket)
    print("Client connected")

    try:
        async for message in websocket:
            print("Received:", message)

            # Broadcast to all other clients
            for client in list(connected_clients):
                if client != websocket:
                    try:
                        await client.send(message)
                    except Exception:
                        # Remove any dead/broken websockets
                        connected_clients.remove(client)

    except websockets.ConnectionClosed:
        print("Client disconnected")

    finally:
        # Always remove on disconnect
        if websocket in connected_clients:
            connected_clients.remove(websocket)


async def main():
    print("WebSocket server running on ws://localhost:8080")
    async with websockets.serve(handler, "localhost", 8080):
        await asyncio.Future()  # run forever


asyncio.run(main())
