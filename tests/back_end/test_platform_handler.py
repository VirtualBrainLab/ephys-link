import pytest
from pytest_mock import MockerFixture
from vbl_aquarium.models.ephys_link import GetManipulatorsResponse, PlatformInfo
from vbl_aquarium.models.unity import Vector4

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.bindings.fake_binding import FakeBinding
from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.console import Console


class TestPlatformHandler:
    """Tests for the PlatformHandler class."""

    def test_get_display_name(self, mock_console: Console, mocker: MockerFixture) -> None:
        """Platform should return binding display name.

        Args:
            mock_console: Mocked Console instance.
            mocker: Binding mocker.
        """
        # Define dummy data.
        dummy_name = "Dummy Binding"

        # Mock binding.
        patched_get_display_name = mocker.patch.object(
            FakeBinding, "get_display_name", return_value=dummy_name, autospec=True
        )
        platform_handler = PlatformHandler(FakeBinding(), mock_console)

        # Assert.
        patched_get_display_name.assert_called()
        assert platform_handler.get_display_name() == dummy_name

    @pytest.mark.asyncio
    async def test_get_platform_info(self, mock_console: Console, mocker: MockerFixture) -> None:
        """Platform should return binding platform info.

        Args:
            mock_console: Mocked Console instance.
            mocker: Binding mocker.
        """
        # Define dummy binding data.
        dummy_name = "Dummy Binding"
        dummy_cli_name = "dummy"
        dummy_axes_count = 3
        dummy_dimensions = Vector4(x=1.0, y=2.0, z=3.0, w=4.0)

        # Mock binding.
        mock_binding = mocker.create_autospec(BaseBinding, instance=True)
        mock_binding.get_display_name.return_value = dummy_name  # pyright: ignore[reportAny]
        mock_binding.get_cli_name.return_value = dummy_cli_name  # pyright: ignore[reportAny]
        mock_binding.get_axes_count.return_value = dummy_axes_count  # pyright: ignore[reportAny]
        mock_binding.get_dimensions.return_value = dummy_dimensions  # pyright: ignore[reportAny]

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(mock_binding, mock_console)

        # Test.
        assert await platform_handler.get_platform_info() == PlatformInfo(
            name=dummy_name, cli_name=dummy_cli_name, axes_count=dummy_axes_count, dimensions=dummy_dimensions
        )

    @pytest.mark.asyncio
    async def test_get_manipulators_typical(self, mock_console: Console, mocker: MockerFixture) -> None:
        """Platform should return available binding manipulators.

        Args:
            mock_console: Mocked Console instance.
            mocker: Binding mocker.
        """
        # Define dummy manipulators.
        dummy_manipulators = ["1", "2"]

        # Mock binding.
        mock_binding = mocker.create_autospec(BaseBinding, instance=True)
        mock_binding.get_manipulators.return_value = dummy_manipulators  # pyright: ignore[reportAny]

        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(mock_binding, mock_console)

        # Test.
        assert await platform_handler.get_manipulators() == GetManipulatorsResponse(manipulators=dummy_manipulators)
