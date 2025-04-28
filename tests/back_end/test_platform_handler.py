import pytest
from pytest_mock import MockerFixture
from vbl_aquarium.models.ephys_link import GetManipulatorsResponse, PlatformInfo, PositionalResponse
from vbl_aquarium.models.unity import Vector4

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.bindings.fake_binding import FakeBinding
from ephys_link.utils.console import Console


class TestPlatformHandler:
    """Tests for the PlatformHandler class."""

    @pytest.mark.parametrize("test_name", ["", "Dummy Binding"])
    def test_get_display_name(
        self, test_name: str, test_fake_binding: FakeBinding, test_console: Console, mocker: MockerFixture
    ) -> None:
        """Platform should return binding display name.

        Args:
            test_name: Test value for display name.
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_display_name = mocker.patch.object(
            test_fake_binding, "get_display_name", return_value=test_name, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = platform_handler.get_display_name()

        # Assert.
        patched_get_display_name.assert_called()
        assert result == test_name

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
        # Define dummy binding data.
        dummy_name = "Dummy Binding"
        dummy_cli_name = "dummy"
        dummy_axes_count = 3
        dummy_dimensions = Vector4(x=1.0, y=2.0, z=3.0, w=4.0)

        # Mock binding.
        patched_get_display_name = mocker.patch.object(
            test_fake_binding, "get_display_name", return_value=dummy_name, autospec=True
        )
        patched_get_cli_name = mocker.patch.object(
            test_fake_binding, "get_cli_name", return_value=dummy_cli_name, autospec=True
        )
        patched_get_axes_count = mocker.patch.object(
            test_fake_binding, "get_axes_count", return_value=dummy_axes_count, autospec=True
        )
        patched_get_dimensions = mocker.patch.object(
            test_fake_binding, "get_dimensions", return_value=dummy_dimensions, autospec=True
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
            name=dummy_name, cli_name=dummy_cli_name, axes_count=dummy_axes_count, dimensions=dummy_dimensions
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_manipulators", [[], ["1", "2"]])
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
    @pytest.mark.parametrize("test_exception", [RuntimeError("Test runtime error"), ValueError("Test value error")])
    async def test_get_manipulators_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, test_exception: Exception, mocker: MockerFixture
    ) -> None:
        """Platform should have error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            test_exception: Test exception to raise.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(
            test_fake_binding, "get_manipulators", side_effect=test_exception, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_manipulators()

        # Assert.
        patched_get_manipulators.assert_called()
        spied_exception_error_print.assert_called_with("Get Manipulators", test_exception)
        assert result == GetManipulatorsResponse(error=test_console.pretty_exception(test_exception))

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "test_position", [Vector4(x=0.0, y=0.0, z=0.0, w=0.0), Vector4(x=1.0, y=2.0, z=3.0, w=4.0)]
    )
    async def test_get_position_typical(
        self, test_fake_binding: FakeBinding, test_console: Console, test_position: Vector4, mocker: MockerFixture
    ) -> None:
        """Platform should return a unified space position

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            test_position: Test values for manipulators.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_position = mocker.patch.object(
            test_fake_binding, "get_position", return_value=test_position, autospec=True
        )

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_position("1")

        # Assert.
        patched_get_position.assert_called_with("1")
        assert result == PositionalResponse(position=test_fake_binding.platform_space_to_unified_space(test_position))

    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_exception", [RuntimeError("Test runtime error"), ValueError("Test value error")])
    async def test_get_position_exception(
        self, test_fake_binding: FakeBinding, test_console: Console, test_exception: Exception, mocker: MockerFixture
    ) -> None:
        """Platform should have error in response if binding raises exception.

        Args:
            test_fake_binding: FakeBinding instance.
            test_console: Console instance.
            test_exception: Test exception to raise.
            mocker: Binding mocker.
        """
        # Mock binding.
        patched_get_manipulators = mocker.patch.object(
            test_fake_binding, "get_position", side_effect=test_exception, autospec=True
        )
        spied_exception_error_print = mocker.spy(test_console, "exception_error_print")

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(test_fake_binding, test_console)

        # Act.
        result = await platform_handler.get_position("1")

        # Assert.
        patched_get_manipulators.assert_called()
        spied_exception_error_print.assert_called_with("Get Position", test_exception)
        assert result == PositionalResponse(error=test_console.pretty_exception(test_exception))
