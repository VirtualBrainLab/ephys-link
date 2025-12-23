import asyncio
from json import dumps, loads

import pytest
from pytest_mock import MockerFixture
from socketio import AsyncServer  # pyright: ignore[reportMissingTypeStubs]
from vbl_aquarium.models.ephys_link import (
    AngularResponse,
    BooleanStateResponse,
    EphysLinkOptions,
    GetManipulatorsResponse,
    PlatformInfo,
    PositionalResponse,
    SetDepthRequest,
    SetDepthResponse,
    SetInsideBrainRequest,
    SetPositionRequest,
    ShankCountResponse,
)

import ephys_link.back_end.server
from ephys_link.__about__ import __version__
from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.back_end.server import Server
from ephys_link.front_end.console import Console
from ephys_link.utils.constants import (
    MALFORMED_REQUEST_ERROR,
    SERVER_NOT_INITIALIZED_ERROR,
    UNKNOWN_EVENT_ERROR,
    cannot_connect_as_client_is_already_connected_error,
    client_disconnected_without_being_connected_error,
)
from tests.conftest import DUMMY_STRING, DUMMY_STRING_LIST, DUMMY_VECTOR3, DUMMY_VECTOR4


class TestServer:
    @pytest.fixture
    def platform_handler(self, mocker: MockerFixture) -> PlatformHandler:
        """Fixture for mock PlatformHandler."""
        return mocker.Mock(spec=PlatformHandler)

    @pytest.fixture
    def console(self, mocker: MockerFixture) -> Console:
        """Fixture for mock console."""
        return mocker.Mock(spec=Console)

    @pytest.fixture
    def server(self, platform_handler: PlatformHandler, console: Console) -> Server:
        """Fixture for server."""
        return Server(EphysLinkOptions(), platform_handler, console)

    def test_failed_server_init(
        self, platform_handler: PlatformHandler, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should raise error if sio is not an AsyncServer."""
        # Mock out the AsyncServer init.
        patched_async_server = mocker.patch.object(AsyncServer, "__new__")

        # Act
        with pytest.raises(TypeError) as init_error:
            _ = Server(EphysLinkOptions(), platform_handler, console)

        # Assert
        patched_async_server.assert_called_once()
        assert init_error.value.args[0] == SERVER_NOT_INITIALIZED_ERROR

    def test_launch_server(
        self, server: Server, platform_handler: PlatformHandler, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should print info then start."""
        # Add mocks and spies.
        # noinspection DuplicatedCode
        spied_info_print = mocker.spy(console, "info_print")

        patched_get_display_name = mocker.patch.object(platform_handler, "get_display_name", return_value=DUMMY_STRING)

        # Mock out get manipulators.
        patched_get_manipulators = mocker.patch.object(platform_handler, "get_manipulators", new=mocker.Mock())
        asyncio_loop = mocker.Mock()
        patched_run_until_complete = mocker.patch.object(
            asyncio_loop, "run_until_complete", return_value=GetManipulatorsResponse(manipulators=DUMMY_STRING_LIST)
        )
        patched_new_event_loop = mocker.patch.object(
            ephys_link.back_end.server, "new_event_loop", return_value=asyncio_loop
        )

        # Mock out run_app.
        mocked_run_app = mocker.patch.object(ephys_link.back_end.server, "run_app")

        # Act.
        server.launch()

        # Assert.
        patched_get_display_name.assert_called_once()
        patched_get_manipulators.assert_called_once()
        patched_run_until_complete.assert_called_once()
        patched_new_event_loop.assert_called_once()
        spied_info_print.assert_any_call("PLATFORM", platform_handler.get_display_name())
        spied_info_print.assert_any_call("MANIPULATORS", str(DUMMY_STRING_LIST))
        mocked_run_app.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_success(self, server: Server, console: Console, mocker: MockerFixture) -> None:
        """Server should allow connection if there is no existing connection."""
        # Spy console.
        spied_info_print = mocker.spy(console, "info_print")

        # Act.
        result = await server.connect(DUMMY_STRING, DUMMY_STRING)

        # Assert.
        spied_info_print.assert_any_call("CONNECTION REQUEST", DUMMY_STRING)
        assert server._client_sid == DUMMY_STRING  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]
        spied_info_print.assert_any_call("CONNECTION GRANTED", DUMMY_STRING)
        assert result

    @pytest.mark.asyncio
    async def test_connect_failure(self, server: Server, console: Console, mocker: MockerFixture) -> None:
        """Server should not allow connection if there is an existing connection."""
        # Spy console.
        spied_info_print = mocker.spy(console, "info_print")
        spied_error_print = mocker.spy(console, "error_print")

        # Mock client sid.
        _ = mocker.patch.object(server, "_client_sid", new=DUMMY_STRING)

        # Act.
        result = await server.connect(DUMMY_STRING, DUMMY_STRING)

        # Assert.
        spied_info_print.assert_any_call("CONNECTION REQUEST", DUMMY_STRING)
        spied_error_print.assert_called_once_with(
            "CONNECTION REFUSED", cannot_connect_as_client_is_already_connected_error(DUMMY_STRING, DUMMY_STRING)
        )
        assert not result

    @pytest.mark.asyncio
    async def test_disconnect_success(self, server: Server, console: Console, mocker: MockerFixture) -> None:
        """Server should allow disconnection if the SID matches the existing connection."""
        # Spy console.
        spied_info_print = mocker.spy(console, "info_print")

        # Mock client sid.
        _ = mocker.patch.object(server, "_client_sid", new=DUMMY_STRING)

        # Act.
        await server.disconnect(DUMMY_STRING)

        # Assert.
        spied_info_print.assert_any_call("DISCONNECTION REQUEST", DUMMY_STRING)
        assert server._client_sid == ""  # noqa: SLF001 # pyright: ignore[reportPrivateUsage]
        spied_info_print.assert_any_call("DISCONNECTED", DUMMY_STRING)

    @pytest.mark.asyncio
    async def test_disconnect_failure(self, server: Server, console: Console, mocker: MockerFixture) -> None:
        """Server should not allow disconnection if there is no existing connection."""
        # Spy console.
        spied_info_print = mocker.spy(console, "info_print")
        spied_error_print = mocker.spy(console, "error_print")

        # Act.
        await server.disconnect(DUMMY_STRING)

        # Assert.
        spied_info_print.assert_any_call("DISCONNECTION REQUEST", DUMMY_STRING)
        spied_error_print.assert_called_once_with(
            "DISCONNECTION", client_disconnected_without_being_connected_error(DUMMY_STRING)
        )

    @pytest.mark.asyncio
    async def test_platform_event_handler_get_version(
        self, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should return version."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Act.
        event_name = "get_version"
        result = await server.platform_event_handler(event_name, DUMMY_STRING, None)

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert result == __version__

    @pytest.mark.asyncio
    async def test_platform_event_handler_get_platform_info(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should return platform info."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock platform info.
        dummy_info = PlatformInfo(name=DUMMY_STRING, cli_name=DUMMY_STRING, axes_count=4, dimensions=DUMMY_VECTOR4)
        event_name = "get_platform_info"
        _ = mocker.patch.object(platform_handler, event_name, return_value=dummy_info)

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, None)
        parsed_result = PlatformInfo(**loads(result))  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == dummy_info

    @pytest.mark.asyncio
    async def test_platform_event_handler_get_manipulators(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should return manipulators."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock manipulators.
        dummy_manipulators = GetManipulatorsResponse(manipulators=DUMMY_STRING_LIST)
        event_name = "get_manipulators"
        _ = mocker.patch.object(platform_handler, event_name, return_value=dummy_manipulators)

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, None)
        parsed_result = GetManipulatorsResponse(**loads(result))  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == dummy_manipulators

    @pytest.mark.asyncio
    async def test_run_if_data_available_malformed_request(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should raise error on malformed request."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")
        spied_error_print = mocker.spy(console, "error_print")

        # Mock position.
        dummy_position = PositionalResponse(position=DUMMY_VECTOR4)
        event_name = "get_position"
        _ = mocker.patch.object(platform_handler, event_name, return_value=dummy_position)

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, None)
        parsed_result = loads(result)  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        spied_error_print.assert_called_once_with("MALFORMED REQUEST", f"{event_name}: {None}")
        assert parsed_result == MALFORMED_REQUEST_ERROR

    @pytest.mark.asyncio
    async def test_platform_event_handler_get_position(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should return position."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock position.
        dummy_position = PositionalResponse(position=DUMMY_VECTOR4)
        event_name = "get_position"
        _ = mocker.patch.object(platform_handler, event_name, return_value=dummy_position)

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, DUMMY_STRING)
        parsed_result = PositionalResponse(**loads(result))  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == dummy_position

    @pytest.mark.asyncio
    async def test_platform_event_handler_get_angles(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should return angles."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock angles.
        dummy_angles = AngularResponse(angles=DUMMY_VECTOR3)
        event_name = "get_angles"
        _ = mocker.patch.object(platform_handler, event_name, return_value=dummy_angles)

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, DUMMY_STRING)
        parsed_result = AngularResponse(**loads(result))  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == dummy_angles

    @pytest.mark.asyncio
    async def test_platform_event_handler_get_shank_count(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should return shank count."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock shank count.
        dummy_shank_count = ShankCountResponse(shank_count=4)
        event_name = "get_shank_count"
        _ = mocker.patch.object(platform_handler, event_name, return_value=dummy_shank_count)

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, DUMMY_STRING)
        parsed_result = ShankCountResponse(**loads(result))  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == dummy_shank_count

    @pytest.mark.asyncio
    async def test_platform_event_handler_set_position(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should set position."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock set position.
        dummy_request = SetPositionRequest(manipulator_id=DUMMY_STRING, position=DUMMY_VECTOR4, speed=1)
        dummy_response = PositionalResponse(position=DUMMY_VECTOR4)
        event_name = "set_position"
        _ = mocker.patch.object(platform_handler, event_name, return_value=dummy_response)

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, dummy_request.to_json_string())
        parsed_result = PositionalResponse(**loads(result))  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == dummy_response

    @pytest.mark.asyncio
    async def test_platform_event_handler_json_decode_error(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should return error on malformed data."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock set position.
        dummy_request = SetPositionRequest(manipulator_id=DUMMY_STRING, position=DUMMY_VECTOR4, speed=1)
        event_name = "set_position"
        _ = mocker.patch.object(platform_handler, event_name, return_value=PositionalResponse(position=DUMMY_VECTOR4))

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, dummy_request)
        parsed_result = loads(result)  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == MALFORMED_REQUEST_ERROR

    @pytest.mark.asyncio
    async def test_platform_event_handler_parse_validation_error(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should log exception and return error on invalid data."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")
        spied_exception_error_print = mocker.spy(console, "exception_error_print")

        # Mock set position.
        event_name = "set_position"
        _ = mocker.patch.object(platform_handler, event_name, return_value=PositionalResponse(position=DUMMY_VECTOR4))

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, dumps({DUMMY_STRING: DUMMY_STRING}))
        parsed_result = loads(result)  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        spied_exception_error_print.assert_called_once()
        assert parsed_result == MALFORMED_REQUEST_ERROR

    @pytest.mark.asyncio
    async def test_platform_event_handler_parse_no_data_error(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should return error on empty data."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock set position.
        event_name = "set_position"
        _ = mocker.patch.object(platform_handler, event_name, return_value=PositionalResponse(position=DUMMY_VECTOR4))

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, None)
        parsed_result = loads(result)  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == MALFORMED_REQUEST_ERROR

    @pytest.mark.asyncio
    async def test_platform_event_handler_set_depth(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should set depth."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock set depth.
        dummy_request = SetDepthRequest(manipulator_id=DUMMY_STRING, depth=1, speed=1)
        dummy_response = SetDepthResponse(depth=1)
        event_name = "set_depth"
        _ = mocker.patch.object(platform_handler, event_name, return_value=dummy_response)

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, dummy_request.to_json_string())
        parsed_result = SetDepthResponse(**loads(result))  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == dummy_response

    @pytest.mark.asyncio
    async def test_platform_event_handler_set_inside_brain(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should set inside brain state."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock set depth.
        dummy_request = SetInsideBrainRequest(manipulator_id=DUMMY_STRING, inside=True)
        dummy_response = BooleanStateResponse(state=True)
        event_name = "set_inside_brain"
        _ = mocker.patch.object(platform_handler, event_name, return_value=dummy_response)

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, dummy_request.to_json_string())
        parsed_result = BooleanStateResponse(**loads(result))  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == dummy_response

    @pytest.mark.asyncio
    async def test_platform_event_handler_stop(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should stop all manipulators."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock stop.
        _ = mocker.patch.object(platform_handler, "stop", return_value="")

        # Act.
        event_name = "stop"
        result = await server.platform_event_handler(event_name, DUMMY_STRING, DUMMY_STRING)

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert result == ""

    @pytest.mark.asyncio
    async def test_platform_event_handler_stop_no_data(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should stop all manipulators."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock stop.
        _ = mocker.patch.object(platform_handler, "stop", return_value="")

        # Act.
        event_name = "stop"
        result = await server.platform_event_handler(event_name, DUMMY_STRING, None)
        parsed_result = loads(result)  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert parsed_result == MALFORMED_REQUEST_ERROR

    @pytest.mark.asyncio
    async def test_platform_event_handler_stop_all(
        self, platform_handler: PlatformHandler, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should stop all manipulators."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")

        # Mock stop.
        event_name = "stop_all"
        _ = mocker.patch.object(platform_handler, event_name, return_value="")

        # Act.
        result = await server.platform_event_handler(event_name, DUMMY_STRING, DUMMY_STRING)

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        assert result == ""

    @pytest.mark.asyncio
    async def test_platform_event_handler_unknown_event(
        self, server: Server, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should stop all manipulators."""
        # Spy console.
        spied_info_print = mocker.spy(console, "debug_print")
        spied_error_print = mocker.spy(console, "error_print")

        # Act.
        event_name = DUMMY_STRING
        result = await server.platform_event_handler(event_name, DUMMY_STRING, DUMMY_STRING)
        parsed_result = loads(result)  # pyright: ignore[reportAny]

        # Assert.
        spied_info_print.assert_called_once_with("EVENT", event_name)
        spied_error_print.assert_called_once_with("EVENT", f"Unknown event: {event_name}.")
        assert parsed_result == UNKNOWN_EVENT_ERROR
