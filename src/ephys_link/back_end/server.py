"""Socket.IO Server.

Responsible to managing the Socket.IO connection and events.
Directs events to the platform handler or handles them directly.

Usage:
    Instantiate Server with the appropriate options, platform handler, and console.
    Then call `launch()` to start the server.

    ```python
    Server(options, platform_handler, console).launch()
    ```
"""

from asyncio import new_event_loop
from collections.abc import Callable, Coroutine
from json import JSONDecodeError, dumps, loads
from typing import Any, TypeVar, final

from aiohttp.web import Application, run_app
from pydantic import ValidationError
from socketio import AsyncServer  # pyright: ignore [reportMissingTypeStubs]
from vbl_aquarium.models.ephys_link import (
    EphysLinkOptions,
    SetDepthRequest,
    SetInsideBrainRequest,
    SetPositionRequest,
)
from vbl_aquarium.utils.vbl_base_model import VBLBaseModel

from ephys_link.__about__ import __version__
from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.front_end.console import Console
from ephys_link.utils.constants import (
    MALFORMED_REQUEST_ERROR,
    PORT,
    UNKNOWN_EVENT_ERROR,
    cannot_connect_as_client_is_already_connected_error,
    client_disconnected_without_being_connected_error,
)

# Server message generic types.
INPUT_TYPE = TypeVar("INPUT_TYPE", bound=VBLBaseModel)
OUTPUT_TYPE = TypeVar("OUTPUT_TYPE", bound=VBLBaseModel)


@final
class Server:
    def __init__(self, options: EphysLinkOptions, platform_handler: PlatformHandler, console: Console) -> None:
        """Initialize server fields based on options and platform handler.

        Args:
            options: Launch options object.
            platform_handler: Platform handler instance.
            console: Console instance.
        """

        # Save fields.
        self._options = options
        self._platform_handler = platform_handler
        self._console = console

        # Initialize server.
        self._sio: AsyncServer = AsyncServer()

        self._app = Application()
        self._sio.attach(self._app)  # pyright: ignore [reportUnknownMemberType]

        # Bind connection events.
        _ = self._sio.on("connect", self.connect)  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        _ = self._sio.on("disconnect", self.disconnect)  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]

        # Store connected client.
        self._client_sid: str = ""

        # Bind events.
        _ = self._sio.on("*", self.platform_event_handler)  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]

    def launch(self) -> None:
        """Launch the server."""

        # List platform and available manipulators.
        self._console.info_print("PLATFORM", self._platform_handler.get_display_name())

        # Create a temporary event loop for getting manipulators
        loop = new_event_loop()
        try:
            self._console.info_print(
                "MANIPULATORS",
                str(loop.run_until_complete(self._platform_handler.get_manipulators()).manipulators),
            )
        finally:
            loop.close()

        # Launch server
        run_app(self._app, port=PORT)

    # Helper functions.
    def _malformed_request_response(self, request: str, data: tuple[tuple[Any], ...]) -> str:  # pyright: ignore [reportExplicitAny]
        """Return a response for a malformed request.

        Args:
            request: Original request.
            data: Request data.

        Returns:
            Response for a malformed request.
        """
        self._console.error_print("MALFORMED REQUEST", f"{request}: {data}")
        return dumps(MALFORMED_REQUEST_ERROR)

    async def _run_if_data_available(
        self,
        function: Callable[[str], Coroutine[Any, Any, VBLBaseModel]],  # pyright: ignore [reportExplicitAny]
        event: str,
        data: Any,  # pyright: ignore [reportAny, reportExplicitAny]
    ) -> str:
        """Run a function if data is available.

        Args:
            function: Function to run.
            event: Event name.
            data: Event data.

        Returns:
            Response data from function.
        """
        if data:
            return str((await function(str(data))).to_json_string())  # pyright: ignore[reportAny]
        return self._malformed_request_response(event, data)  # pyright: ignore[reportAny]

    async def _run_if_data_parses(
        self,
        function: Callable[[INPUT_TYPE], Coroutine[Any, Any, OUTPUT_TYPE]],  # pyright: ignore [reportExplicitAny]
        data_type: type[INPUT_TYPE],
        event: str,
        data: Any,  # pyright: ignore [reportAny, reportExplicitAny]
    ) -> str:
        """Run a function if data parses.

        Args:
            function: Function to run.
            data_type: Data type to parse.
            event: Event name.
            data: Event data.

        Returns:
            Response data from function.
        """
        if data:
            try:
                parsed_data = data_type(**loads(str(data)))  # pyright: ignore[reportAny]
            except JSONDecodeError:
                return self._malformed_request_response(event, data)  # pyright: ignore[reportAny]
            except ValidationError as e:
                self._console.exception_error_print(event, e)
                return self._malformed_request_response(event, data)  # pyright: ignore[reportAny]
            else:
                return str((await function(parsed_data)).to_json_string())
        return self._malformed_request_response(event, data)  # pyright: ignore[reportAny]

    # Event Handlers.

    async def connect(self, sid: str, _: str) -> bool:
        """Handle connections to the server.

        Args:
            sid: Socket session ID.
            _: Extra connection data (unused).

        Returns:
            False on error to refuse connection, True otherwise.
        """
        self._console.info_print("CONNECTION REQUEST", sid)

        if self._client_sid == "":
            self._client_sid = sid
            self._console.info_print("CONNECTION GRANTED", sid)
            return True

        self._console.error_print(
            "CONNECTION REFUSED", cannot_connect_as_client_is_already_connected_error(sid, self._client_sid)
        )
        return False

    async def disconnect(self, sid: str) -> None:
        """Handle disconnections from the server.

        Args:
            sid: Socket session ID.
        """
        self._console.info_print("DISCONNECTION REQUEST", sid)

        # Reset client SID if it matches.
        if self._client_sid == sid:
            self._client_sid = ""
            self._console.info_print("DISCONNECTED", sid)
        else:
            self._console.error_print("DISCONNECTION", client_disconnected_without_being_connected_error(sid))

    async def platform_event_handler(self, event: str, _: str, data: Any) -> str:  # pyright: ignore [reportAny, reportExplicitAny]
        """Handle events from the server.

        Matches incoming events based on the Socket.IO API.

        Args:
            event: Event name.
            _: Socket session ID (unused).
            data: Event data.

        Returns:
            Response data.
        """

        # Log event.
        self._console.debug_print("EVENT", event)

        # Handle event.
        match event:
            # Server metadata.
            case "get_version":
                return __version__
            case "get_platform_info":
                return (await self._platform_handler.get_platform_info()).to_json_string()

            # Manipulator commands.
            case "get_manipulators":
                return str((await self._platform_handler.get_manipulators()).to_json_string())
            case "get_position":
                return await self._run_if_data_available(self._platform_handler.get_position, event, data)
            case "get_angles":
                return await self._run_if_data_available(self._platform_handler.get_angles, event, data)
            case "get_shank_count":
                return await self._run_if_data_available(self._platform_handler.get_shank_count, event, data)
            case "set_position":
                return await self._run_if_data_parses(
                    self._platform_handler.set_position, SetPositionRequest, event, data
                )
            case "set_depth":
                return await self._run_if_data_parses(self._platform_handler.set_depth, SetDepthRequest, event, data)
            case "set_inside_brain":
                return await self._run_if_data_parses(
                    self._platform_handler.set_inside_brain, SetInsideBrainRequest, event, data
                )
            case "jackhammer":
                if data:
                    try:
                        parsed = loads(str(data))
                        return (
                            await self._platform_handler.jackhammer(
                                manipulator_id=parsed.get("manipulator_id", parsed.get("ManipulatorId", "")),
                                axis=parsed.get("axis", parsed.get("Axis", 3)),
                                iterations=parsed.get("iterations", parsed.get("Iterations", 10)),
                                phase1_steps=parsed.get("phase1_steps", parsed.get("Phase1Steps", 10)),
                                phase1_pulses=parsed.get("phase1_pulses", parsed.get("Phase1Pulses", 15)),
                                phase2_steps=parsed.get("phase2_steps", parsed.get("Phase2Steps", 5)),
                                phase2_pulses=parsed.get("phase2_pulses", parsed.get("Phase2Pulses", -15)),
                            )
                        ).to_json_string()
                    except JSONDecodeError:
                        return self._malformed_request_response(event, data)
                return self._malformed_request_response(event, data)
            case "stop":
                if data:
                    return await self._platform_handler.stop(str(data))  # pyright: ignore[reportAny]
                return self._malformed_request_response(event, data)  # pyright: ignore[reportAny]
            case "stop_all":
                return await self._platform_handler.stop_all()
            case _:
                self._console.error_print("EVENT", f"Unknown event: {event}.")
                return dumps(UNKNOWN_EVENT_ERROR)
