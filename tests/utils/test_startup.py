import sys
from io import StringIO

import pytest
from pytest_mock import MockerFixture
from requests import ConnectionError, ConnectTimeout
from vbl_aquarium.models.ephys_link import EphysLinkOptions

from ephys_link.__about__ import __version__
from ephys_link.bindings.fake_binding import FakeBinding
from ephys_link.bindings.mpm_binding import MPMBinding
from ephys_link.bindings.ump_binding import UmpBinding
from ephys_link.front_end.console import Console
from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.constants import ASCII, UNABLE_TO_CHECK_FOR_UPDATES_ERROR, ump_4_3_deprecation_error, \
    unrecognized_platform_type_error
from ephys_link.utils.startup import check_for_updates, get_bindings, preamble, get_binding_instance


class TestStartup:
    @pytest.fixture
    def console(self, mocker: MockerFixture) -> Console:
        """Fixture for mock console."""
        return mocker.Mock(spec=Console)

    def test_preamble(self) -> None:
        """Test the preamble function."""
        # Arrange.
        captured_output = StringIO()
        sys.stdout = captured_output

        # Act.
        preamble()

        # Assert.
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        assert "Ephys Link" in output
        assert "This is the Ephys Link server window." in output
        assert __version__ in output
        assert ASCII in output

    def test_check_for_updates_is_newer(self, console: Console, mocker: MockerFixture) -> None:
        """Test the check_for_updates function."""
        # Add mocks and spies.
        spied_critical_print = mocker.spy(console, "critical_print")

        # Mock requests.get to return a fake response with a lower version.
        fake_response = mocker.Mock()
        fake_response.json.return_value = [{"name": "0.0.0"}]  # pyright: ignore [reportAny]
        _ = mocker.patch("ephys_link.utils.startup.get", return_value=fake_response)

        # Act
        check_for_updates(console)

        # Assert: critical_print should NOT be called since no update is available.
        spied_critical_print.assert_not_called()

    def test_check_for_updates_is_older(self, console: Console, mocker: MockerFixture) -> None:
        """Test the check_for_updates function with a newer version."""
        # Add mocks and spies.
        spied_critical_print = mocker.spy(console, "critical_print")

        # Mock the json() method of the response from get
        fake_response = mocker.Mock()
        fake_response.json.return_value = [{"name": "1000000.0.0"}]  # pyright: ignore [reportAny]
        _ = mocker.patch("ephys_link.utils.startup.get", return_value=fake_response)

        # Act
        check_for_updates(console)

        # Assert: critical_print should be called since an update is available.
        spied_critical_print.assert_called()

    @pytest.mark.parametrize("exception", [ConnectionError, ConnectTimeout])
    def test_check_for_updates_connection_errors(
        self, exception: ConnectionError | ConnectTimeout, console: Console, mocker: MockerFixture
    ) -> None:
        """Test the check_for_updates function with connection-related errors."""
        # Add mocks and spies.
        spied_error_print = mocker.spy(console, "error_print")

        # Mock requests.get to raise a ConnectionError or ConnectTimeout.
        _ = mocker.patch("ephys_link.utils.startup.get", side_effect=exception)

        # Act
        check_for_updates(console)

        # Assert: error_print should be called with the correct message.
        spied_error_print.assert_called_with("UPDATE", UNABLE_TO_CHECK_FOR_UPDATES_ERROR)

    def test_get_bindings_returns_valid_bindings(self):
        """Test that get_bindings returns a list of valid binding classes."""
        # Act.
        bindings = get_bindings()

        # Assert.
        assert isinstance(bindings, list)
        assert all(issubclass(b, BaseBinding) for b in bindings)
        assert BaseBinding not in bindings
    
    @pytest.mark.parametrize("cli_name,binding", [("fake", FakeBinding), ("pathfinder-mpm", MPMBinding)])
    def test_get_binding_instance(self, cli_name:str, binding:BaseBinding, console: Console, mocker: MockerFixture):
        """Test that get_binding_instance returns an instance of the requested binding class."""
        # Arrange.
        spied_error_print = mocker.spy(console, "error_print")
        fake_options = EphysLinkOptions(type=cli_name)

        # Act.
        binding_instance = get_binding_instance(fake_options, console)

        # Assert.
        assert isinstance(binding_instance, binding)
        spied_error_print.assert_not_called()
    
    @pytest.mark.parametrize("cli_name", ["ump-4", "ump-3"])
    def test_get_binding_instance_ump(self, cli_name: str, console: Console, mocker: MockerFixture):
        """Test that get_binding_instance returns an instance of the UmpBinding class and handles deprecation."""
        # Arrange.
        spied_error_print = mocker.spy(console, "error_print")
        fake_options = EphysLinkOptions(type=cli_name)
        mock_ump = mocker.patch("ephys_link.bindings.ump_binding.UmpBinding", autospec=True)

        # Act.
        with pytest.raises(ValueError) as e:
            get_binding_instance(fake_options, console)

        # Assert.
        spied_error_print.assert_called_once_with("DEPRECATION", ump_4_3_deprecation_error(cli_name))
        assert str(e.value) == unrecognized_platform_type_error("ump")
