import asyncio
import websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:22267/ws/oas") as ws:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=10)
            print("recv:", msg)
        except asyncio.TimeoutError:
            print("no greeting")
        await ws.send("stop")
        print("sent: stop")
        await asyncio.sleep(2)

asyncio.run(main())
