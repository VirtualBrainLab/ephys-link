from asyncio import run

from socketio import AsyncClient

pinpoint_id = "abcdefgh"
is_requester = False

sio = AsyncClient()


async def main():
    await sio.connect("http://localhost:3000")
    await sio.wait()


@sio.event
async def get_pinpoint_id() -> tuple[str, bool]:
    return pinpoint_id, is_requester


run(main())
