"""Handle communications with Sensapex uMp-3 API

Uses the Sensapex uMp handler which implements for the uMp-4 manipulator
and extends it to support the uMp-3 manipulator.

This is a subclass of :class:`ephys_link.platforms.sensapex_handler`.
"""

from __future__ import annotations

from ephys_link.platforms.sensapex_handler import SensapexHandler
from ephys_link.platforms.ump3_manipulator import UMP3Manipulator


class UMP3Handler(SensapexHandler):
    def __init__(self):
        super().__init__()

        self.num_axes = 3
        self.dimensions = [20, 20, 20]

    def _register_manipulator(self, manipulator_id: str) -> None:
        if not manipulator_id.isnumeric():
            msg = "Manipulator ID must be numeric"
            raise ValueError(msg)

        self.manipulators[manipulator_id] = UMP3Manipulator(self.ump.get_device(int(manipulator_id)))

    def _platform_space_to_unified_space(self, platform_position: list[float]) -> list[float]:
        # unified   <-  platform
        # +x        <-  +y
        # +y        <-  -x
        # +z        <-  -z
        # +d        <-  +d/x

        return [
            platform_position[1],
            self.dimensions[0] - platform_position[0],
            self.dimensions[2] - platform_position[2],
            platform_position[3],
        ]

    def _unified_space_to_platform_space(self, unified_position: list[float]) -> list[float]:
        # platform  <-  unified
        # +x        <-  -y
        # +y        <-  +x
        # +z        <-  -z
        # +d/x      <-  +d

        return [
            self.dimensions[1] - unified_position[1],
            unified_position[0],
            self.dimensions[2] - unified_position[2],
            unified_position[3],
        ]
