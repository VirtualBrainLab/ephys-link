"""Handle communications with Sensapex uMp-3 API

Uses the Sensapex uMp handler which implements for the uMp-4 manipulator
and extends it to support the uMp-3 manipulator.

This is a subclass of :class:`ephys_link.platforms.sensapex_handler`.
"""

from __future__ import annotations

from vbl_aquarium.models.unity import Vector4

from ephys_link.platforms.sensapex_handler import SensapexHandler
from ephys_link.platforms.ump3_manipulator import UMP3Manipulator


class UMP3Handler(SensapexHandler):
    def __init__(self):
        super().__init__()

        self.num_axes = 3
        self.dimensions = Vector4(x=20, y=20, z=20, w=0)

    def _register_manipulator(self, manipulator_id: str) -> None:
        if not manipulator_id.isnumeric():
            msg = "Manipulator ID must be numeric"
            raise ValueError(msg)

        self.manipulators[manipulator_id] = UMP3Manipulator(self.ump.get_device(int(manipulator_id)))

    def _platform_space_to_unified_space(self, platform_position: Vector4) -> Vector4:
        # unified   <-  platform
        # +x        <-  +y
        # +y        <-  -x
        # +z        <-  -z
        # +d        <-  +d/x

        return Vector4(
            x=platform_position.y,
            y=self.dimensions.x - platform_position.x,
            z=self.dimensions.z - platform_position.z,
            w=platform_position.w,
        )

    def _unified_space_to_platform_space(self, unified_position: Vector4) -> Vector4:
        # platform  <-  unified
        # +x        <-  -y
        # +y        <-  +x
        # +z        <-  -z
        # +d/x      <-  +d

        return Vector4(
            x=self.dimensions.y - unified_position.y,
            y=unified_position.x,
            z=self.dimensions.z - unified_position.z,
            w=unified_position.w,
        )
