import pytest
from pytest_mock import MockerFixture
from vbl_aquarium.models.ephys_link import (
    AngularResponse,
    BooleanStateResponse,
    GetManipulatorsResponse,
    PlatformInfo,
    PositionalResponse,
    SetDepthRequest,
    SetDepthResponse,
    SetInsideBrainRequest,
    SetPositionRequest,
    ShankCountResponse,
)
from vbl_aquarium.models.unity import Vector4

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.front_end.console import Console
from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.constants import (
    EMERGENCY_STOP_MESSAGE,
    NO_SET_POSITION_WHILE_INSIDE_BRAIN_ERROR,
    did_not_reach_target_depth_error,
    did_not_reach_target_position_error,
)
from tests.conftest import (
    DUMMY_EXCEPTION,
    DUMMY_INT,
    DUMMY_SMALL_STRING,
    DUMMY_STRING,
    DUMMY_STRING_LIST,
    DUMMY_VECTOR3,
    DUMMY_VECTOR4,
)


class TestPlatformHandler:
    """Tests for the PlatformHandler class."""

    @pytest.fixture
    def console(self, mocker: MockerFixture) -> Console:
        """Console instance for testing."""

        def exception_to_string(exception: Exception) -> str:
            return str(exception)

        # Create mock.
        mocked_console = mocker.Mock(spec=Console)

        # Patch internally used functions.
        _ = mocker.patch.object(mocked_console, "pretty_exception", side_effect=exception_to_string)

        # Return mocked console.
        return mocked_console

    @pytest.fixture
    def binding(self, mocker: MockerFixture) -> BaseBinding:
        """FakeBinding instance for testing."""

        def reflect_vector4(input_vector: Vector4) -> Vector4:
            return input_vector

        # Create mock.
        mocked_binding = mocker.Mock(spec=BaseBinding)

        # Patch internally used functions.
        _ = mocker.patch.object(mocked_binding, "platform_space_to_unified_space", side_effect=reflect_vector4)
        _ = mocker.patch.object(mocked_binding, "unified_space_to_platform_space", side_effect=reflect_vector4)

        # Return mocked binding.
        return mocked_binding

    @pytest.fixture
    def platform_handler(self, binding: BaseBinding, console: Console) -> PlatformHandler:
        """Fixture for creating a PlatformHandler instance."""
        return PlatformHandler(binding, console)

    def test_get_display_name(
        self, platform_handler: PlatformHandler, binding: BaseBinding, mocker: MockerFixture
    ) -> None:
        """Platform should return binding display name."""
        # Mock binding.
        patched_get_display_name = mocker.patch.object(binding, "get_display_name", return_value=DUMMY_STRING)

        # Act.
        result = platform_handler.get_display_name()

        # Assert.
        patched_get_display_name.assert_called_once()
        assert result == DUMMY_STRING

    @pytest.mark.asyncio
    async def test_get_platform_info(
        self, platform_handler: PlatformHandler, binding: BaseBinding, mocker: MockerFixture
    ) -> None:
        """Platform should return binding platform info."""
        # Mock binding.
        patched_get_display_name = mocker.patch.object(binding, "get_display_name", return_value=DUMMY_STRING)
        patched_get_cli_name = mocker.patch.object(binding, "get_cli_name", return_value=DUMMY_SMALL_STRING)
        patched_get_axes_count = mocker.patch.object(binding, "get_axes_count", return_value=DUMMY_INT)
        patched_get_dimensions = mocker.patch.object(binding, "get_dimensions", return_value=DUMMY_VECTOR4)

        # Act.
        result = await platform_handler.get_platform_info()

        # Assert.
        patched_get_display_name.assert_called_once()
        patched_get_cli_name.assert_called_once()
        patched_get_axes_count.assert_called_once()
        patched_get_dimensions.assert_called_once()
        assert result == PlatformInfo(
            name=DUMMY_STRING,
            cli_name=DUMMY_SMALL_STRING,
            axes_count=DUMMY_INT,
            dimensions=DUMMY_VECTOR4,
        )

    @pytest.mark.asyncio
    async def test_get_manipulators_exception(
        self, platform_handler: PlatformHandler, binding: BaseBinding, console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception."""
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(binding, "get_manipulators", side_effect=DUMMY_EXCEPTION)
        spied_exception_error_print = mocker.spy(console, "exception_error_print")

        # Act.
        result = await platform_handler.get_manipulators()

        # Assert.
        patched_get_manipulators.assert_called_once()
        spied_exception_error_print.assert_called_once_with("Get Manipulators", DUMMY_EXCEPTION)
        assert result == GetManipulatorsResponse(error=console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    @pytest.mark.parametrize("manipulators", [[], DUMMY_STRING_LIST])
    async def test_get_manipulators_typical(
        self,
        platform_handler: PlatformHandler,
        binding: BaseBinding,
        mocker: MockerFixture,
        manipulators: list[str],
    ) -> None:
        """Platform should return available binding manipulators."""
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(binding, "get_manipulators", return_value=manipulators)

        # Act.
        result = await platform_handler.get_manipulators()

        # Assert.
        patched_get_manipulators.assert_called_once()
        assert result == GetManipulatorsResponse(manipulators=manipulators)

    @pytest.mark.asyncio
    async def test_get_position_exception(
        self, platform_handler: PlatformHandler, binding: BaseBinding, console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception."""
        # Mock binding.
        patched_get_position = mocker.patch.object(binding, "get_position", side_effect=DUMMY_EXCEPTION)
        spied_exception_error_print = mocker.spy(console, "exception_error_print")

        # Act.
        result = await platform_handler.get_position("1")

        # Assert.
        patched_get_position.assert_called_once_with("1")
        spied_exception_error_print.assert_called_once_with("Get Position", DUMMY_EXCEPTION)
        assert result == PositionalResponse(error=console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    async def test_get_position_typical(
        self, platform_handler: PlatformHandler, binding: BaseBinding, mocker: MockerFixture
    ) -> None:
        """Platform should return a unified space position."""
        # Mock binding.
        patched_get_position = mocker.patch.object(binding, "get_position", return_value=DUMMY_VECTOR4)

        # Act.
        result = await platform_handler.get_position("1")

        # Assert.
        patched_get_position.assert_called_once_with("1")
        assert result == PositionalResponse(position=binding.platform_space_to_unified_space(DUMMY_VECTOR4))

    @pytest.mark.asyncio
    async def test_get_angles_exception(
        self, platform_handler: PlatformHandler, binding: BaseBinding, console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception."""
        # Mock binding.
        patched_get_angles = mocker.patch.object(binding, "get_angles", side_effect=DUMMY_EXCEPTION)
        spied_exception_error_print = mocker.spy(console, "exception_error_print")

        # Act.
        result = await platform_handler.get_angles("1")

        # Assert.
        patched_get_angles.assert_called_once()
        spied_exception_error_print.assert_called_once_with("Get Angles", DUMMY_EXCEPTION)
        assert result == AngularResponse(error=console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    async def test_get_angles_typical(
        self, platform_handler: PlatformHandler, binding: BaseBinding, mocker: MockerFixture
    ) -> None:
        """Platform should return manipulator angles."""
        # Mock binding.
        patched_get_angles = mocker.patch.object(binding, "get_angles", return_value=DUMMY_VECTOR3)

        # Act.
        result = await platform_handler.get_angles("1")

        # Assert.
        patched_get_angles.assert_called_once_with("1")
        assert result == AngularResponse(angles=DUMMY_VECTOR3)

    @pytest.mark.asyncio
    async def test_get_shank_count_exception(
        self, platform_handler: PlatformHandler, binding: BaseBinding, console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception."""
        # Mock binding.
        patched_get_shank_count = mocker.patch.object(binding, "get_shank_count", side_effect=DUMMY_EXCEPTION)
        spied_exception_error_print = mocker.spy(console, "exception_error_print")

        # Act.
        result = await platform_handler.get_shank_count("1")

        # Assert.
        patched_get_shank_count.assert_called_once()
        spied_exception_error_print.assert_called_once_with("Get Shank Count", DUMMY_EXCEPTION)
        assert result == ShankCountResponse(error=console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    async def test_get_shank_count_typical(
        self, platform_handler: PlatformHandler, binding: BaseBinding, mocker: MockerFixture
    ) -> None:
        """Platform should return manipulator angles."""
        # Mock binding.
        patched_get_shank_count = mocker.patch.object(binding, "get_shank_count", return_value=DUMMY_INT)

        # Act.
        result = await platform_handler.get_shank_count("1")

        # Assert.
        patched_get_shank_count.assert_called_once_with("1")
        assert result == ShankCountResponse(shank_count=DUMMY_INT)

    @pytest.mark.asyncio
    async def test_set_position_inside_brain(
        self, platform_handler: PlatformHandler, binding: BaseBinding, console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should reject set position if manipulator is inside brain."""
        # Mock binding.
        _ = mocker.patch.object(platform_handler, "_inside_brain", new=["1"])
        spied_error_print = mocker.spy(console, "error_print")
        spied_binding_set_position = mocker.spy(binding, "set_position")

        # Act.
        result = await platform_handler.set_position(
            SetPositionRequest(manipulator_id="1", position=DUMMY_VECTOR4, speed=1.0)
        )

        # Assert.
        spied_error_print.assert_called_once_with("Set Position", NO_SET_POSITION_WHILE_INSIDE_BRAIN_ERROR)
        spied_binding_set_position.assert_not_called()
        assert result == PositionalResponse(error=NO_SET_POSITION_WHILE_INSIDE_BRAIN_ERROR)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("axes_count", [3, 4])
    @pytest.mark.parametrize("final_position_offset_index", range(4))
    async def test_set_position_beyond_tolerance(
        self,
        platform_handler: PlatformHandler,
        binding: BaseBinding,
        console: Console,
        mocker: MockerFixture,
        axes_count: int,
        final_position_offset_index: int,
    ) -> None:
        """Platform should return error if final position is not close enough to target position.

        Args:
            axes_count: Test number of axes.
            final_position_offset_index: Test offset from final position.
        """
        # Data for test.
        dummy_offsets = [
            Vector4(x=1, y=0, z=0, w=0),
            Vector4(x=0, y=1, z=0, w=0),
            Vector4(x=0, y=0, z=1, w=0),
            Vector4(x=0, y=0, z=0, w=1),
        ]
        dummy_final_position = DUMMY_VECTOR4 + dummy_offsets[final_position_offset_index]
        dummy_request = SetPositionRequest(manipulator_id="1", position=DUMMY_VECTOR4, speed=1.0)
        error_message = did_not_reach_target_position_error(
            dummy_request, final_position_offset_index, dummy_final_position
        )

        # Mock binding.
        patched_set_position = mocker.patch.object(
            binding,
            "set_position",
            return_value=binding.unified_space_to_platform_space(dummy_final_position),
        )
        patched_get_axes_count = mocker.patch.object(binding, "get_axes_count", return_value=axes_count)
        patched_get_movement_tolerance = mocker.patch.object(binding, "get_movement_tolerance", return_value=0)
        spied_error_print = mocker.spy(console, "error_print")

        # Act.
        result = await platform_handler.set_position(dummy_request)

        # Assert.
        patched_set_position.assert_called_once_with(
            manipulator_id="1", position=binding.unified_space_to_platform_space(DUMMY_VECTOR4), speed=1.0
        )
        patched_get_axes_count.assert_called()
        patched_get_movement_tolerance.assert_called()
        if axes_count == 3 and final_position_offset_index == 3:
            spied_error_print.assert_not_called()
            assert result == PositionalResponse(position=dummy_final_position)
        else:
            spied_error_print.assert_called_once_with("Set Position", error_message)
            assert result == PositionalResponse(error=error_message)

    @pytest.mark.asyncio
    async def test_set_position_exception(
        self, platform_handler: PlatformHandler, binding: BaseBinding, console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception."""
        # Mock binding.
        patched_set_position = mocker.patch.object(binding, "set_position", side_effect=DUMMY_EXCEPTION)
        spied_exception_error_print = mocker.spy(console, "exception_error_print")

        # Act.
        result = await platform_handler.set_position(
            SetPositionRequest(manipulator_id="1", position=DUMMY_VECTOR4, speed=1.0)
        )

        # Assert.
        patched_set_position.assert_called_once()
        spied_exception_error_print.assert_called_once_with("Set Position", DUMMY_EXCEPTION)
        assert result == PositionalResponse(error=console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    @pytest.mark.parametrize("axes_count", [3, 4])
    async def test_set_position_typical(
        self,
        platform_handler: PlatformHandler,
        binding: BaseBinding,
        mocker: MockerFixture,
        axes_count: int,
    ) -> None:
        """Platform should return manipulator's final position.

        Args:
            axes_count: Test number of axes.
        """
        # Data for test.
        dummy_request = SetPositionRequest(manipulator_id="1", position=DUMMY_VECTOR4, speed=1.0)

        # Mock binding.
        patched_set_position = mocker.patch.object(
            binding,
            "set_position",
            return_value=binding.unified_space_to_platform_space(DUMMY_VECTOR4),
        )
        patched_get_axes_count = mocker.patch.object(binding, "get_axes_count", return_value=axes_count)
        patched_get_movement_tolerance = mocker.patch.object(binding, "get_movement_tolerance", return_value=0.001)

        # Act.
        result = await platform_handler.set_position(dummy_request)

        # Assert.
        patched_set_position.assert_called_with(
            manipulator_id="1", position=binding.unified_space_to_platform_space(DUMMY_VECTOR4), speed=1.0
        )
        patched_get_axes_count.assert_called()
        patched_get_movement_tolerance.assert_called()
        assert result == PositionalResponse(position=dummy_request.position)

    @pytest.mark.asyncio
    async def test_set_depth_beyond_tolerance(
        self,
        platform_handler: PlatformHandler,
        binding: BaseBinding,
        console: Console,
        mocker: MockerFixture,
    ) -> None:
        """Platform should return error if final depth is not close enough to target depth."""
        # Data for test.
        dummy_final_depth = DUMMY_VECTOR4.w + 1
        dummy_request = SetDepthRequest(manipulator_id="1", depth=DUMMY_VECTOR4.w, speed=1.0)
        error_message = did_not_reach_target_depth_error(dummy_request, dummy_final_depth)

        # Mock binding.
        patched_set_depth = mocker.patch.object(
            binding,
            "set_depth",
            return_value=dummy_final_depth,
        )
        patched_get_movement_tolerance = mocker.patch.object(binding, "get_movement_tolerance", return_value=0)
        spied_error_print = mocker.spy(console, "error_print")

        # Act.
        result = await platform_handler.set_depth(dummy_request)

        # Assert.
        patched_set_depth.assert_called_once_with(manipulator_id="1", depth=DUMMY_VECTOR4.w, speed=1.0)
        patched_get_movement_tolerance.assert_called_once()
        spied_error_print.assert_called_once_with("Set Depth", error_message)
        assert result == SetDepthResponse(error=error_message)

    @pytest.mark.asyncio
    async def test_set_depth_exception(
        self, platform_handler: PlatformHandler, binding: BaseBinding, console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception."""
        # Mock binding.
        patched_set_depth = mocker.patch.object(binding, "set_depth", side_effect=DUMMY_EXCEPTION)
        spied_exception_error_print = mocker.spy(console, "exception_error_print")

        # Act.
        result = await platform_handler.set_depth(SetDepthRequest(manipulator_id="1", depth=DUMMY_VECTOR4.w, speed=1.0))

        # Assert.
        patched_set_depth.assert_called_once()
        spied_exception_error_print.assert_called_once_with("Set Depth", DUMMY_EXCEPTION)
        assert result == SetDepthResponse(error=console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    async def test_set_depth_typical(
        self,
        platform_handler: PlatformHandler,
        binding: BaseBinding,
        mocker: MockerFixture,
    ) -> None:
        """Platform should return manipulator's final depth."""
        # Data for test.
        dummy_request = SetDepthRequest(manipulator_id="1", depth=DUMMY_VECTOR4.w, speed=1.0)

        # Mock binding.
        patched_set_depth = mocker.patch.object(
            binding,
            "set_depth",
            return_value=DUMMY_VECTOR4.w,
        )
        patched_get_movement_tolerance = mocker.patch.object(binding, "get_movement_tolerance", return_value=0.001)

        # Act.
        result = await platform_handler.set_depth(dummy_request)

        # Assert.
        patched_set_depth.assert_called_once_with(manipulator_id="1", depth=DUMMY_VECTOR4.w, speed=1.0)
        patched_get_movement_tolerance.assert_called_once()
        assert result == SetDepthResponse(depth=DUMMY_VECTOR4.w)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("state", [True, False])
    @pytest.mark.parametrize("initial_inside_brain", [set(), {"2"}])  # pyright: ignore[reportUnknownArgumentType]
    async def test_set_inside_brain(
        self,
        platform_handler: PlatformHandler,
        mocker: MockerFixture,
        state: bool,  # noqa: FBT001
        initial_inside_brain: set[str],
    ) -> None:
        """Platform should return inside brain state.

        Args:
            state: Test value for inside brain.
            initial_inside_brain: Test initial inside brain values.
        """
        # Patch inside brain.
        _ = mocker.patch.object(platform_handler, "_inside_brain", new=initial_inside_brain)

        # Act.
        result = await platform_handler.set_inside_brain(SetInsideBrainRequest(manipulator_id="1", inside=state))

        # Assert.
        assert result == BooleanStateResponse(state=state)
        if state:
            initial_inside_brain.add("1")
        else:
            initial_inside_brain.discard("1")
        assert platform_handler._inside_brain == initial_inside_brain  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]

    @pytest.mark.asyncio
    async def test_stop_exception(
        self, platform_handler: PlatformHandler, binding: BaseBinding, console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception."""
        # Mock binding.
        patched_stop = mocker.patch.object(binding, "stop", side_effect=DUMMY_EXCEPTION)
        spied_exception_error_print = mocker.spy(console, "exception_error_print")

        # Act.
        result = await platform_handler.stop("1")

        # Assert.
        patched_stop.assert_called_once()
        spied_exception_error_print.assert_called_once_with("Stop", DUMMY_EXCEPTION)
        assert result == console.pretty_exception(DUMMY_EXCEPTION)

    @pytest.mark.asyncio
    async def test_stop_typical(
        self, platform_handler: PlatformHandler, binding: BaseBinding, mocker: MockerFixture
    ) -> None:
        """Platform should return empty string on stop."""
        # Mock binding.
        patched_stop = mocker.patch.object(
            binding,
            "stop",
        )

        # Act.
        result = await platform_handler.stop("1")

        # Assert.
        patched_stop.assert_called_once_with("1")
        assert result == ""

    @pytest.mark.asyncio
    async def test_stop_all_exception(
        self, platform_handler: PlatformHandler, binding: BaseBinding, console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception."""
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(binding, "get_manipulators", return_value=["1"])
        patched_stop = mocker.patch.object(binding, "stop", side_effect=DUMMY_EXCEPTION)
        spied_exception_error_print = mocker.spy(console, "exception_error_print")

        # Act.
        result = await platform_handler.stop_all()

        # Assert.
        patched_get_manipulators.assert_called_once()
        patched_stop.assert_called_once()
        spied_exception_error_print.assert_called_once_with("Stop All", DUMMY_EXCEPTION)
        assert result == console.pretty_exception(DUMMY_EXCEPTION)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("manipulators", [[], DUMMY_STRING_LIST])
    async def test_stop_all_typical(
        self,
        platform_handler: PlatformHandler,
        binding: BaseBinding,
        mocker: MockerFixture,
        manipulators: list[str],
    ) -> None:
        """Platform should return empty string on stop all.

        Args:
            manipulators: Test values for manipulators.
        """
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(binding, "get_manipulators", return_value=manipulators)
        patched_stop = mocker.patch.object(
            binding,
            "stop",
        )

        # Act.
        result = await platform_handler.stop_all()

        # Assert.
        patched_get_manipulators.assert_called_once()
        for manipulator_id in manipulators:
            patched_stop.assert_any_call(manipulator_id)
        assert patched_stop.call_count == len(manipulators)
        assert result == ""

    @pytest.mark.asyncio
    async def test_emergency_stop(
        self, platform_handler: PlatformHandler, console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should call stop_all and print to critical console."""
        # Mock binding.
        patched_stop_all = mocker.patch.object(
            platform_handler,
            "stop_all",
        )
        spied_critical_print = mocker.spy(console, "critical_print")

        # Act.
        await platform_handler.emergency_stop()

        # Assert.
        patched_stop_all.assert_called_once()
        spied_critical_print.assert_called_once_with(EMERGENCY_STOP_MESSAGE)
