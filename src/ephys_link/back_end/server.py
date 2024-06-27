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


class Server(BaseCommands):
    def __init__(self, options: EphysLinkOptions, platform_handler: PlatformHandler):
        """Initialize server fields based on options and platform handler."""

        # Initialize based on proxy usage.
        if options.use_proxy:
            self._sio = AsyncClient()
            self._pinpoint_id = str(uuid4())[:8]
        else:
            self._sio = AsyncServer()
            self._app = Application()

        # Platform handler.
        self.platform_handler = platform_handler

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
