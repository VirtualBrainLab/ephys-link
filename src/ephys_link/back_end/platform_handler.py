from typing import TYPE_CHECKING

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

from ephys_link.__main__ import console
from ephys_link.util.base_commands import BaseCommands
from ephys_link.platforms.ump_4_bindings import Ump4Bindings

if TYPE_CHECKING:
    from ephys_link.util.base_bindings import BaseBindings


class PlatformHandler(BaseCommands):
    """Handler for platform commands."""

    def __init__(self, platform_type: str) -> None:
        """Initialize platform handler.

        :param platform_type: Platform type to initialize bindings from.
        :type platform_type: str
        """

        # Define bindings based on platform type.
        match platform_type:
            case "ump-4":
                self._bindings: BaseBindings = Ump4Bindings()

    async def get_manipulators(self) -> GetManipulatorsResponse:
        try:
            return GetManipulatorsResponse(
                manipulators=self._bindings.get_manipulators(),
                num_axes=self._bindings.get_num_axes(),
                dimensions=self._bindings.get_dimensions(),
                error="",
            )
        except Exception as e:
            console.err_print("Get Manipulators", e)
            return GetManipulatorsResponse(error=str(e))

    async def get_pos(self, manipulator_id: str) -> PositionalResponse:
        try:
            raw_position = self._bindings.get_pos(manipulator_id)
            
            return PositionalResponse(
                position=self._bindings.platform_space_to_unified_space(raw_position),
                error="",
            )
        except Exception as e:
            console.err_print("Get Position", e)
            return PositionalResponse(error=str(e))

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
