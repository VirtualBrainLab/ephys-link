from vbl_aquarium.models.ephys_link import (
    AngularResponse,
    BooleanStateResponse,
    DriveToDepthRequest,
    DriveToDepthResponse,
    GetManipulatorsResponse,
    GotoPositionRequest,
    InsideBrainRequest,
    PositionalResponse,
    ShankCountResponse,
)

from ephys_link.back_end.base_commands import BaseCommands


class PlatformHandler(BaseCommands):
    async def get_manipulators(self) -> GetManipulatorsResponse:
        pass

    async def get_pos(self, manipulator_id: str) -> PositionalResponse:
        pass

    async def get_angles(self, manipulator_id: str) -> AngularResponse:
        pass

    async def get_shank_count(self, manipulator_id: str) -> ShankCountResponse:
        pass

    async def goto_pos(self, request: GotoPositionRequest) -> PositionalResponse:
        pass

    async def drive_to_depth(self, request: DriveToDepthRequest) -> DriveToDepthResponse:
        pass

    async def set_inside_brain(self, request: InsideBrainRequest) -> BooleanStateResponse:
        pass

    async def calibrate(self, manipulator_id: str) -> str:
        pass

    async def stop(self) -> BooleanStateResponse:
        pass
