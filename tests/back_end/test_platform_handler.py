from typing import final

import pytest
from pytest_mock import MockerFixture
from vbl_aquarium.models.ephys_link import (
    AngularResponse,
    GetManipulatorsResponse,
    PlatformInfo,
    PositionalResponse,
    SetPositionRequest,
    ShankCountResponse,
)

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.bindings.fake_binding import FakeBinding
from ephys_link.utils.console import Console
from ephys_link.utils.constants import NO_SET_POSITION_WHILE_INSIDE_BRAIN_ERROR
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
    @pytest.mark.parametrize("test_manipulators", [[], DUMMY_STRING_LIST])
    async def test_get_manipulators_typical(
        self, test_fake_binding: FakeBinding, test_console: Console, test_manipulators: list[str], mocker: MockerFixture
    ) -> None:
        """Platform should return available binding manipulators.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            test_manipulators: Test values for manipulators.
            mocker: Binding mocker.
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
    async def test_get_manipulators_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should have error in response if binding raises exception.

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
    async def test_get_position_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should have error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(
            test_fake_binding, "get_position", side_effect=DUMMY_EXCEPTION, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_position("1")

        # Assert.
        patched_get_manipulators.assert_called()
        spied_exception_error_print.assert_called_with("Get Position", DUMMY_EXCEPTION)
        assert result == PositionalResponse(error=test_console.pretty_exception(DUMMY_EXCEPTION))

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
        patched_get_position = mocker.patch.object(
            test_fake_binding, "get_angles", return_value=DUMMY_VECTOR3, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_angles("1")

        # Assert.
        patched_get_position.assert_called_with("1")
        assert result == AngularResponse(angles=DUMMY_VECTOR3)

    @pytest.mark.asyncio
    async def test_get_angles_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should have error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(
            test_fake_binding, "get_angles", side_effect=DUMMY_EXCEPTION, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_angles("1")

        # Assert.
        patched_get_manipulators.assert_called()
        spied_exception_error_print.assert_called_with("Get Angles", DUMMY_EXCEPTION)
        assert result == AngularResponse(error=test_console.pretty_exception(DUMMY_EXCEPTION))

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
        patched_get_position = mocker.patch.object(
            test_fake_binding, "get_shank_count", return_value=DUMMY_INT, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_shank_count("1")

        # Assert.
        patched_get_position.assert_called_with("1")
        assert result == ShankCountResponse(shank_count=DUMMY_INT)

    @pytest.mark.asyncio
    async def test_get_shank_count_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should have error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(
            test_fake_binding, "get_shank_count", side_effect=DUMMY_EXCEPTION, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_shank_count("1")

        # Assert.
        patched_get_manipulators.assert_called()
        spied_exception_error_print.assert_called_with("Get Shank Count", DUMMY_EXCEPTION)
        assert result == ShankCountResponse(error=test_console.pretty_exception(DUMMY_EXCEPTION))

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

        # Patch _inside_brain list
        _ = mocker.patch.object(platform_handler, "_inside_brain", new=["1"])
        spied_error_print = mocker.spy(test_console, "error_print")

        # Act.
        result = await platform_handler.set_position(
            SetPositionRequest(manipulator_id="1", position=DUMMY_VECTOR4, speed=1.0)
        )

        # Assert.
        spied_error_print.assert_called_with("Set Position", NO_SET_POSITION_WHILE_INSIDE_BRAIN_ERROR)
        assert result == PositionalResponse(error=NO_SET_POSITION_WHILE_INSIDE_BRAIN_ERROR)
