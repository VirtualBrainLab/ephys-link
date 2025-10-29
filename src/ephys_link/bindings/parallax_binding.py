from asyncio import get_running_loop, sleep
from json import dumps
from typing import Any, final, override

from requests import JSONDecodeError, get, put
from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.converters import scalar_mm_to_um, vector4_to_array


@final
class ParallaxBinding(BaseBinding):
    """Bindings for Parallax platform."""

    # Server data update rate (30 FPS).
    SERVER_DATA_UPDATE_RATE = 1 / 30

    # Movement polling preferences.
    UNCHANGED_COUNTER_LIMIT = 10

    # Speed preferences (mm/s to use coarse mode).
    COARSE_SPEED_THRESHOLD = 0.1
    INSERTION_SPEED_LIMIT = 9_000

    def __init__(self, port: int = 8081) -> None:
        """Initialize connection to MPM HTTP server.

        Args:
            port: Port number for MPM HTTP server.
        """
        self._url = f"http://localhost:{port}"
        self._movement_stopped = False

        # Data cache.
        self.cache: dict[str, Any] = {}  # pyright: ignore [reportExplicitAny]
        self.cache_time = 0

    @staticmethod
    @override
    def get_display_name() -> str:
        return "Parallax"

    @staticmethod
    @override
    def get_cli_name() -> str:
        return "parallax"

    @override
    async def get_manipulators(self) -> list[str]:
        data = await self._query_data()
        return list(data.keys())

    @override
    async def get_axes_count(self) -> int:
        return 3

    @override
    def get_dimensions(self) -> Vector4:
        return Vector4(x=15, y=15, z=15, w=15)

    @override
    async def get_position(self, manipulator_id: str) -> Vector4:
        manipulator_data: dict[str, Any] = await self._manipulator_data(manipulator_id)
        global_z = float(manipulator_data.get("global_Z", 0.0) or 0.0)

        await sleep(self.SERVER_DATA_UPDATE_RATE)  # Wait for the stage to stabilize.

        global_x = float(manipulator_data.get("global_X", 0.0) or 0.0)
        global_y = float(manipulator_data.get("global_Y", 0.0) or 0.0)

        return Vector4(x=global_x, y=global_y, z=global_z, w=global_z)

    @override
    async def get_angles(self, manipulator_id: str) -> Vector3:
        manipulator_data: dict[str, Any] = await self._manipulator_data(manipulator_id)

        yaw = int(manipulator_data.get("yaw", 0) or 0)
        pitch = int(manipulator_data.get("pitch", 90) or 90)
        roll = int(manipulator_data.get("roll", 0) or 0)

        return Vector3(x=yaw, y=pitch, z=roll)

    @override
    async def get_shank_count(self, manipulator_id: str) -> int:
        manipulator_data: dict[str, Any] = await self._manipulator_data(manipulator_id)
        return int(manipulator_data.get("shank_cnt", 1) or 1)

    @staticmethod
    @override
    def get_movement_tolerance() -> float:
        return 0.01

    @override
    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        # Keep track of the previous position to check if the manipulator stopped advancing.
        current_position = await self.get_position(manipulator_id)
        previous_position = current_position
        unchanged_counter = 0

        # Set step mode based on speed.
        await self._put_request(
            {
                "move_type": "stepMode",
                "stage_sn": manipulator_id,
                "step_mode": 0 if speed > self.COARSE_SPEED_THRESHOLD else 1,
            }
        )

        # Send move request.
        await self._put_request(
            {
                "move_type": "moveXYZ",
                "world": "global",  # Use global coordinates
                "stage_sn": manipulator_id,
                "Absolute": 1,
                "Stereotactic": 0,
                "AxisMask": 7,
                "x": position.x,
                "y": position.y,
                "z": position.z,
            }
        )
        # Wait for the manipulator to reach the target position or be stopped or stuck.
        while (
            not self._movement_stopped
            and not self._is_vector_close(current_position, position)
            and unchanged_counter < self.UNCHANGED_COUNTER_LIMIT
        ):
            # Wait for a short time before checking again.
            await sleep(self.SERVER_DATA_UPDATE_RATE)

            # Update current position.
            current_position = await self.get_position(manipulator_id)

            # Check if manipulator is not moving.
            if self._is_vector_close(previous_position, current_position):
                # Position did not change.
                unchanged_counter += 1
            else:
                # Position changed.
                unchanged_counter = 0
                previous_position = current_position

        # Reset movement stopped flag.
        self._movement_stopped = False

        # Return the final position.
        return await self.get_position(manipulator_id)

    @override
    async def set_depth(self, manipulator_id: str, depth: float, speed: float) -> float:
        # Keep track of the previous depth to check if the manipulator stopped advancing unexpectedly.
        current_depth = (await self.get_position(manipulator_id)).w
        previous_depth = current_depth
        unchanged_counter = 0

        # Send move request.
        # Convert mm/s to um/min and cap speed at the limit.
        await self._put_request(
            {
                "move_type": "insertion",
                "stage_sn": manipulator_id,
                "world": "global",  # distance in global space
                "distance": scalar_mm_to_um(current_depth - depth),
                "rate": min(scalar_mm_to_um(speed) * 60, self.INSERTION_SPEED_LIMIT),
            }
        )

        # Wait for the manipulator to reach the target depth or be stopped or get stuck.
        while (
            not self._movement_stopped
            and not abs(current_depth - depth) <= self.get_movement_tolerance()
            and unchanged_counter < self.UNCHANGED_COUNTER_LIMIT
        ):
            # Wait for a short time before checking again.
            await sleep(self.SERVER_DATA_UPDATE_RATE)

            # Get the current depth.
            current_depth = (await self.get_position(manipulator_id)).w

            # Check if manipulator is not moving.
            if abs(previous_depth - current_depth) <= self.get_movement_tolerance():
                # Depth did not change.
                unchanged_counter += 1
            else:
                # Depth changed.
                unchanged_counter = 0
                previous_depth = current_depth

        # Reset movement stopped flag.
        self._movement_stopped = False

        # Return the final depth.
        return float((await self.get_position(manipulator_id)).w)

    @override
    async def stop(self, manipulator_id: str) -> None:
        request: dict[str, str | int | float] = {
            "PutId": "stop",
            "Probe": manipulator_id,
        }
        await self._put_request(request)
        self._movement_stopped = True

    @override
    def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        # unified   <-  platform
        # +x        <-  +x
        # +y        <-  +z
        # +z        <-  +y
        # +w        <-  +w

        return Vector4(
            x=platform_space.x,
            y=platform_space.z,
            z=platform_space.y,
            w=self.get_dimensions().w - platform_space.w,
        )

    @override
    def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        # platform  <-  unified
        # +x        <-  +x
        # +y        <-  +z
        # +z        <-  +y
        # +w        <-  -w

        return Vector4(
            x=unified_space.x,
            y=unified_space.z,
            z=unified_space.y,
            w=self.get_dimensions().w - unified_space.w,
        )

    # Helper functions.
    async def _query_data(self) -> dict[str, Any]:  # pyright: ignore [reportExplicitAny]
        try:
            # Update cache if it's expired.
            if get_running_loop().time() - self.cache_time > self.SERVER_DATA_UPDATE_RATE:
                # noinspection PyTypeChecker
                self.cache = (await get_running_loop().run_in_executor(None, get, self._url)).json()
                self.cache_time = get_running_loop().time()
        except ConnectionError as connectionError:
            error_message = f"Unable to connect to MPM HTTP server: {connectionError}"
            raise RuntimeError(error_message) from connectionError
        except JSONDecodeError as jsonDecodeError:
            error_message = f"Unable to decode JSON response from MPM HTTP server: {jsonDecodeError}"
            raise ValueError(error_message) from jsonDecodeError
        else:
            # Return cached data.
            return self.cache

    async def _manipulator_data(self, manipulator_id: str) -> dict[str, Any]:  # pyright: ignore [reportExplicitAny]
        """Retrieve data for a specific manipulator (probe) using its serial number."""
        data = await self._query_data()

        if manipulator_id in data:
            return data[manipulator_id]
        return None

    async def _put_request(self, request: dict[str, Any]) -> None:  # pyright: ignore [reportExplicitAny]
        _ = await get_running_loop().run_in_executor(None, put, self._url, dumps(request))

    def _is_vector_close(self, target: Vector4, current: Vector4) -> bool:
        return all(abs(axis) <= self.get_movement_tolerance() for axis in vector4_to_array(target - current)[:3])
