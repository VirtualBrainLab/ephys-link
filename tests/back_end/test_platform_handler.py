from typing import final

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
from ephys_link.bindings.fake_binding import FakeBinding
from ephys_link.front_end.console import Console
from ephys_link.utils.constants import (
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


@final
class TestPlatformHandler:
    """Tests for the PlatformHandler class."""

    def test_get_display_name(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return binding display name.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_display_name = mocker.patch.object(
            test_fake_binding, "get_display_name", return_value=DUMMY_STRING, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = platform_handler.get_display_name()

        # Assert.
        patched_get_display_name.assert_called()
        assert result == DUMMY_STRING

    @pytest.mark.asyncio
    async def test_get_platform_info(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return binding platform info.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_display_name = mocker.patch.object(
            test_fake_binding, "get_display_name", return_value=DUMMY_STRING, autospec=True
        )
        patched_get_cli_name = mocker.patch.object(
            test_fake_binding, "get_cli_name", return_value=DUMMY_SMALL_STRING, autospec=True
        )
        patched_get_axes_count = mocker.patch.object(
            test_fake_binding, "get_axes_count", return_value=DUMMY_INT, autospec=True
        )
        patched_get_dimensions = mocker.patch.object(
            test_fake_binding, "get_dimensions", return_value=DUMMY_VECTOR4, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_platform_info()

        # Assert.
        patched_get_display_name.assert_called()
        patched_get_cli_name.assert_called()
        patched_get_axes_count.assert_called()
        patched_get_dimensions.assert_called()
        assert result == PlatformInfo(
            name=DUMMY_STRING,
            cli_name=DUMMY_SMALL_STRING,
            axes_count=DUMMY_INT,
            dimensions=DUMMY_VECTOR4,
        )

    @pytest.mark.asyncio
    async def test_get_manipulators_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(
            test_fake_binding, "get_manipulators", side_effect=DUMMY_EXCEPTION, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_manipulators()

        # Assert.
        patched_get_manipulators.assert_called()
        spied_exception_error_print.assert_called_with("Get Manipulators", DUMMY_EXCEPTION)
        assert result == GetManipulatorsResponse(error=test_console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_manipulators", [[], DUMMY_STRING_LIST])
    async def test_get_manipulators_typical(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture, test_manipulators: list[str]
    ) -> None:
        """Platform should return available binding manipulators.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
            test_manipulators: Test values for manipulators.
        """
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(
            test_fake_binding, "get_manipulators", return_value=test_manipulators, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_manipulators()

        # Assert.
        patched_get_manipulators.assert_called()
        assert result == GetManipulatorsResponse(manipulators=test_manipulators)

    @pytest.mark.asyncio
    async def test_get_position_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_position = mocker.patch.object(
            test_fake_binding, "get_position", side_effect=DUMMY_EXCEPTION, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_position("1")

        # Assert.
        patched_get_position.assert_called()
        spied_exception_error_print.assert_called_with("Get Position", DUMMY_EXCEPTION)
        assert result == PositionalResponse(error=test_console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    async def test_get_position_typical(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return a unified space position.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_position = mocker.patch.object(
            test_fake_binding, "get_position", return_value=DUMMY_VECTOR4, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_position("1")

        # Assert.
        patched_get_position.assert_called_with("1")
        assert result == PositionalResponse(position=test_fake_binding.platform_space_to_unified_space(DUMMY_VECTOR4))

    @pytest.mark.asyncio
    async def test_get_angles_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_angles = mocker.patch.object(
            test_fake_binding, "get_angles", side_effect=DUMMY_EXCEPTION, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_angles("1")

        # Assert.
        patched_get_angles.assert_called()
        spied_exception_error_print.assert_called_with("Get Angles", DUMMY_EXCEPTION)
        assert result == AngularResponse(error=test_console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    async def test_get_angles_typical(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return manipulator angles.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_angles = mocker.patch.object(
            test_fake_binding, "get_angles", return_value=DUMMY_VECTOR3, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_angles("1")

        # Assert.
        patched_get_angles.assert_called_with("1")
        assert result == AngularResponse(angles=DUMMY_VECTOR3)

    @pytest.mark.asyncio
    async def test_get_shank_count_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_shank_count = mocker.patch.object(
            test_fake_binding, "get_shank_count", side_effect=DUMMY_EXCEPTION, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_shank_count("1")

        # Assert.
        patched_get_shank_count.assert_called()
        spied_exception_error_print.assert_called_with("Get Shank Count", DUMMY_EXCEPTION)
        assert result == ShankCountResponse(error=test_console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    async def test_get_shank_count_typical(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return manipulator angles.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_shank_count = mocker.patch.object(
            test_fake_binding, "get_shank_count", return_value=DUMMY_INT, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_shank_count("1")

        # Assert.
        patched_get_shank_count.assert_called_with("1")
        assert result == ShankCountResponse(shank_count=DUMMY_INT)

    @pytest.mark.asyncio
    async def test_set_position_inside_brain(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should reject set position if manipulator is inside brain.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: PlatformHandler patcher.
        """
        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Mock binding.
        _ = mocker.patch.object(platform_handler, "_inside_brain", new=["1"])
        spied_error_print = mocker.spy(test_console, "error_print")
        spied_binding_set_position = mocker.spy(test_fake_binding, "set_position")

        # Act.
        result = await platform_handler.set_position(
            SetPositionRequest(manipulator_id="1", position=DUMMY_VECTOR4, speed=1.0)
        )

        # Assert.
        spied_error_print.assert_called_with("Set Position", NO_SET_POSITION_WHILE_INSIDE_BRAIN_ERROR)
        spied_binding_set_position.assert_not_called()
        assert result == PositionalResponse(error=NO_SET_POSITION_WHILE_INSIDE_BRAIN_ERROR)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_axes_count", [3, 4])
    @pytest.mark.parametrize("test_final_position_offset_index", range(4))
    async def test_set_position_beyond_tolerance(
        self,
        test_fake_binding: FakeBinding,
        test_console: Console,
        mocker: MockerFixture,
        test_axes_count: int,
        test_final_position_offset_index: int,
    ) -> None:
        """Platform should return error if final position is not close enough to target position.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: PlatformHandler patcher.
            test_axes_count: Test number of axes.
            test_final_position_offset_index: Test offset from final position.
        """
        # Data for test.
        dummy_offsets = [
            Vector4(x=1, y=0, z=0, w=0),
            Vector4(x=0, y=1, z=0, w=0),
            Vector4(x=0, y=0, z=1, w=0),
            Vector4(x=0, y=0, z=0, w=1),
        ]
        dummy_final_position = DUMMY_VECTOR4 + dummy_offsets[test_final_position_offset_index]
        dummy_request = SetPositionRequest(manipulator_id="1", position=DUMMY_VECTOR4, speed=1.0)
        error_message = did_not_reach_target_position_error(
            dummy_request, test_final_position_offset_index, dummy_final_position
        )

        # Mock binding.
        patched_set_position = mocker.patch.object(
            test_fake_binding,
            "set_position",
            return_value=test_fake_binding.unified_space_to_platform_space(dummy_final_position),
            autospec=True,
        )
        patched_get_axes_count = mocker.patch.object(
            test_fake_binding, "get_axes_count", return_value=test_axes_count, autospec=True
        )
        patched_get_binding_tolerance = mocker.patch.object(
            test_fake_binding, "get_movement_tolerance", return_value=0, autospec=True
        )
        spied_error_print = mocker.spy(test_console, "error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.set_position(dummy_request)

        # Assert.
        patched_set_position.assert_called_with(
            manipulator_id="1", position=test_fake_binding.unified_space_to_platform_space(DUMMY_VECTOR4), speed=1.0
        )
        patched_get_axes_count.assert_called()
        patched_get_binding_tolerance.assert_called()
        if test_axes_count == 3 and test_final_position_offset_index == 3:
            spied_error_print.assert_not_called()
            assert result == PositionalResponse(position=dummy_final_position)
        else:
            spied_error_print.assert_called_with("Set Position", error_message)
            assert result == PositionalResponse(error=error_message)

    @pytest.mark.asyncio
    async def test_set_position_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_set_position = mocker.patch.object(
            test_fake_binding, "set_position", side_effect=DUMMY_EXCEPTION, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.set_position(
            SetPositionRequest(manipulator_id="1", position=DUMMY_VECTOR4, speed=1.0)
        )

        # Assert.
        patched_set_position.assert_called()
        spied_exception_error_print.assert_called_with("Set Position", DUMMY_EXCEPTION)
        assert result == PositionalResponse(error=test_console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_axes_count", [3, 4])
    async def test_set_position_typical(
        self,
        test_fake_binding: FakeBinding,
        test_console: Console,
        mocker: MockerFixture,
        test_axes_count: int,
    ) -> None:
        """Platform should return manipulator's final position.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: PlatformHandler patcher.
            test_axes_count: Test number of axes.
        """
        # Data for test.
        dummy_request = SetPositionRequest(manipulator_id="1", position=DUMMY_VECTOR4, speed=1.0)

        # Mock binding.
        patched_set_position = mocker.patch.object(
            test_fake_binding,
            "set_position",
            return_value=test_fake_binding.unified_space_to_platform_space(DUMMY_VECTOR4),
            autospec=True,
        )
        patched_get_axes_count = mocker.patch.object(
            test_fake_binding, "get_axes_count", return_value=test_axes_count, autospec=True
        )
        patched_get_binding_tolerance = mocker.patch.object(
            test_fake_binding, "get_movement_tolerance", return_value=0.001, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.set_position(dummy_request)

        # Assert.
        patched_set_position.assert_called_with(
            manipulator_id="1", position=test_fake_binding.unified_space_to_platform_space(DUMMY_VECTOR4), speed=1.0
        )
        patched_get_axes_count.assert_called()
        patched_get_binding_tolerance.assert_called()
        assert result == PositionalResponse(position=dummy_request.position)

    @pytest.mark.asyncio
    async def test_set_depth_beyond_tolerance(
        self,
        test_fake_binding: FakeBinding,
        test_console: Console,
        mocker: MockerFixture,
    ) -> None:
        """Platform should return error if final depth is not close enough to target depth.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: PlatformHandler patcher.
        """
        # Data for test.
        dummy_final_depth = DUMMY_VECTOR4.w + 1
        dummy_request = SetDepthRequest(manipulator_id="1", depth=DUMMY_VECTOR4.w, speed=1.0)
        error_message = did_not_reach_target_depth_error(dummy_request, dummy_final_depth)

        # Mock binding.
        patched_set_depth = mocker.patch.object(
            test_fake_binding,
            "set_depth",
            return_value=dummy_final_depth,
            autospec=True,
        )
        patched_get_binding_tolerance = mocker.patch.object(
            test_fake_binding, "get_movement_tolerance", return_value=0, autospec=True
        )
        spied_error_print = mocker.spy(test_console, "error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.set_depth(dummy_request)

        # Assert.
        patched_set_depth.assert_called_with(manipulator_id="1", depth=DUMMY_VECTOR4.w, speed=1.0)
        patched_get_binding_tolerance.assert_called()
        spied_error_print.assert_called_with("Set Depth", error_message)
        assert result == SetDepthResponse(error=error_message)

    @pytest.mark.asyncio
    async def test_set_depth_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_set_depth = mocker.patch.object(
            test_fake_binding, "set_depth", side_effect=DUMMY_EXCEPTION, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.set_depth(SetDepthRequest(manipulator_id="1", depth=DUMMY_VECTOR4.w, speed=1.0))

        # Assert.
        patched_set_depth.assert_called()
        spied_exception_error_print.assert_called_with("Set Depth", DUMMY_EXCEPTION)
        assert result == SetDepthResponse(error=test_console.pretty_exception(DUMMY_EXCEPTION))

    @pytest.mark.asyncio
    async def test_set_depth_typical(
        self,
        test_fake_binding: FakeBinding,
        test_console: Console,
        mocker: MockerFixture,
    ) -> None:
        """Platform should return manipulator's final depth.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: PlatformHandler patcher.
        """
        # Data for test.
        dummy_request = SetDepthRequest(manipulator_id="1", depth=DUMMY_VECTOR4.w, speed=1.0)

        # Mock binding.
        patched_set_depth = mocker.patch.object(
            test_fake_binding,
            "set_depth",
            return_value=DUMMY_VECTOR4.w,
            autospec=True,
        )
        patched_get_movement_tolerance = mocker.patch.object(
            test_fake_binding, "get_movement_tolerance", return_value=0.001, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.set_depth(dummy_request)

        # Assert.
        patched_set_depth.assert_called_with(manipulator_id="1", depth=DUMMY_VECTOR4.w, speed=1.0)
        patched_get_movement_tolerance.assert_called()
        assert result == SetDepthResponse(depth=DUMMY_VECTOR4.w)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_state", [True, False])
    async def test_set_inside_brain(
        self,
        test_fake_binding: FakeBinding,
        test_console: Console,
        test_state: bool,  # noqa: FBT001
    ) -> None:
        """Platform should return error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            test_state: Test value for inside brain.
        """
        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.set_inside_brain(SetInsideBrainRequest(manipulator_id="1", inside=test_state))

        # Assert.
        assert result == BooleanStateResponse(state=test_state)
        if test_state:
            assert platform_handler._inside_brain == {"1"}  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]
        else:
            assert platform_handler._inside_brain == set()  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]
