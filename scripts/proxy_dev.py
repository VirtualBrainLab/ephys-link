from asyncio import run

from socketio import AsyncClient

pinpoint_id = "abcdefgh"

sio = AsyncClient()


async def main():
    await sio.connect("http://localhost:3000")
    await sio.wait()


@sio.event
async def get_id():
    return pinpoint_id


run(main())
