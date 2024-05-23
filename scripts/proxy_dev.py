from __future__ import annotations

from asyncio import run

from socketio import AsyncClient

pinpoint_id = "4158ebf3"
is_requester = True

sio = AsyncClient()


async def main():
    await sio.connect("http://localhost:3000")
    # await sio.emit("get_manipulators", lambda m: print(m))
    await sio.wait()


@sio.event
async def get_pinpoint_id() -> tuple[str, bool]:
    return pinpoint_id, is_requester


run(main())
