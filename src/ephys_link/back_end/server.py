from uuid import uuid4

from aiohttp.web import Application
from socketio import AsyncClient, AsyncServer
from vbl_aquarium.models.ephys_link import (
    AngularResponse,
    BooleanStateResponse,
    DriveToDepthRequest,
    DriveToDepthResponse,
    EphysLinkOptions,
    GetManipulatorsResponse,
    GotoPositionRequest,
    InsideBrainRequest,
    PositionalResponse,
    ShankCountResponse,
)

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.util.base_commands import BaseCommands
from ephys_link.util.common import console


class Server(BaseCommands):
    def __init__(self, options: EphysLinkOptions, platform_handler: PlatformHandler) -> None:
        """Initialize server fields based on options and platform handler."""

        # Initialize based on proxy usage.
        if options.use_proxy:
            self._sio = AsyncClient()
            self._pinpoint_id = str(uuid4())[:8]
        else:
            self._sio = AsyncServer()
            self._app = Application()
            self._sio.attach(self._app)

            # Bind connection events.
            self._sio.on("connect", self.connect)
            self._sio.on("disconnect", self.disconnect)

        # Platform handler.
        self.platform_handler = platform_handler

        # Store connected client.
        self._client_sid: str = ""

        # Bind events.
        self._sio.on("get_platform_type", self.get_platform_type)
        self._sio.on("get_manipulators", self.get_manipulators)
        self._sio.on("get_position", self.get_position)
        self._sio.on("get_angles", self.get_angles)
        self._sio.on("get_shank_count", self.get_shank_count)
        self._sio.on("set_position", self.set_position)
        self._sio.on("set_depth", self.set_depth)
        self._sio.on("set_inside_brain", self.set_inside_brain)
        self._sio.on("stop", self.stop)

    # Server launch.
    def launch(self) -> None:
        console.info_print("SERVER", "Starting server...")

    # Event Handlers.

    async def connect(self, sid: str) -> bool:
        """Handle connections to the server

        :param sid: Socket session ID.
        :type sid: str
        :returns: False on error to refuse connection, True otherwise.
        :rtype: bool
        """
        console.info_print("CONNECTION REQUEST", sid)

        if self._client_sid == "":
            self._client_sid = sid
            console.info_print("CONNECTION GRANTED", sid)
            return True

        console.error_print(f"CONNECTION REFUSED to {sid}. Client {self._client_sid} already connected.")
        return False

    async def disconnect(self, sid: str) -> None:
        """Handle disconnections from the server

        :param sid: Socket session ID.
        :type sid: str
        """
        console.info_print("DISCONNECTED", sid)
        if self._client_sid == sid:
            self._client_sid = ""
        else:
            console.error_print(f"Client {sid} disconnected without being connected.")

    async def get_platform_type(self) -> str:
        pass

    async def get_manipulators(self) -> GetManipulatorsResponse:
        pass

    async def get_position(self, manipulator_id: str) -> PositionalResponse:
        pass

    async def get_angles(self, manipulator_id: str) -> AngularResponse:
        pass

    async def get_shank_count(self, manipulator_id: str) -> ShankCountResponse:
        pass

    async def set_position(self, request: GotoPositionRequest) -> PositionalResponse:
        pass

    async def set_depth(self, request: DriveToDepthRequest) -> DriveToDepthResponse:
        pass

    async def set_inside_brain(self, request: InsideBrainRequest) -> BooleanStateResponse:
        pass

    async def stop(self) -> str:
        pass
