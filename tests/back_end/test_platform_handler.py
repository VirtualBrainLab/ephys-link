from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from vbl_aquarium.models.ephys_link import EphysLinkOptions

from ephys_link.back_end.platform_handler import PlatformHandler


class TestPlatformHandler:
    """Tests for the PlatformHandler class."""

    @pytest.fixture
    def mock_platform_handler(self, mock_console: MagicMock, mocker: MockerFixture) -> PlatformHandler:
        """Fixture for the PlatformHandler class.

        Args:
            mock_console: Mocked Console class.
            mocker: Mock fixture for the binding class.

        Returns:
            Mocked PlatformHandler class.
        """
        # Create dummy options.
        EphysLinkOptions(
            type="dummy"
        )

        # Patch get_bindings to return a dummy binding.

        # Create PlatformHandler instance.
        return PlatformHandler(self.options, mock_console)

    def test_get_display_name(self, mock_platform_handler: PlatformHandler) -> None:
        """Test the get_display_name method.

        Args:
            mock_platform_handler: Mocked PlatformHandler class.
        """
        mock_platform_handler.get_display_name()

        self.binding.assert_called()
