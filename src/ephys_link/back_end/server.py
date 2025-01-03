from asyncio import get_event_loop, run
from collections.abc import Callable, Coroutine
from json import JSONDecodeError, dumps, loads
from typing import Any

from aiohttp.web import Application, run_app
from pydantic import ValidationError
from socketio import AsyncClient, AsyncServer
from vbl_aquarium.models.ephys_link import (
    EphysLinkOptions,
    SetDepthRequest,
    SetInsideBrainRequest,
    SetPositionRequest,
)
from vbl_aquarium.utils.vbl_base_model import VBLBaseModel

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.utils.common import PORT, check_for_updates, server_preamble
from ephys_link.utils.console import Console


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

        # Initialize based on proxy usage.
        self._sio: AsyncServer | AsyncClient = AsyncClient() if self._options.use_proxy else AsyncServer()
        if not self._options.use_proxy:
            self._app = Application()
            self._sio.attach(self._app)

            # Bind connection events.
            self._sio.on("connect", self.connect)
            self._sio.on("disconnect", self.disconnect)

        # Store connected client.
        self._client_sid: str = ""

        # Bind events.
        self._sio.on("*", self.platform_event_handler)

    def launch(self) -> None:
        """Launch the server.
        
        Based on the options, either connect to a proxy or launch the server locally.
        """
        # Preamble.
        server_preamble()

        # Check for updates.
        if not self._options.ignore_updates:
            check_for_updates()

        # List platform and available manipulators.
        self._console.info_print("PLATFORM", self._platform_handler.get_platform_type())
        self._console.info_print(
            "MANIPULATORS",
            str(get_event_loop().run_until_complete(self._platform_handler.get_manipulators()).manipulators),
        )

        # Launch server
        if self._options.use_proxy:
            self._console.info_print("PINPOINT ID", self._platform_handler.get_pinpoint_id().pinpoint_id)

            async def connect_proxy() -> None:
                # noinspection HttpUrlsUsage
                await self._sio.connect(f"http://{self._options.proxy_address}:{PORT}")
                await self._sio.wait()

            run(connect_proxy())
        else:
            run_app(self._app, port=PORT)

    # Helper functions.
    def _malformed_request_response(self, request: str, data: tuple[tuple[Any], ...]) -> str:
        """Return a response for a malformed request.
        
        Args:
            request: Original request.
            data: Request data.
        
        Returns:
            Response for a malformed request.
        """
        self._console.error_print("MALFORMED REQUEST", f"{request}: {data}")
        return dumps({"error": "Malformed request."})

    async def _run_if_data_available(
        self, function: Callable[[str], Coroutine[Any, Any, VBLBaseModel]], event: str, data: tuple[tuple[Any], ...]
    ) -> str:
        """Run a function if data is available.
        
        Args:
            function: Function to run.
            event: Event name.
            data: Event data.
        
        Returns:
            Response data from function.
        """
        request_data = data[1]
        if request_data:
            return str((await function(str(request_data))).to_json_string())
        return self._malformed_request_response(event, request_data)

    async def _run_if_data_parses(
        self,
        function: Callable[[VBLBaseModel], Coroutine[Any, Any, VBLBaseModel]],
        data_type: type[VBLBaseModel],
        event: str,
        data: tuple[tuple[Any], ...],
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
        request_data = data[1]
        if request_data:
            try:
                parsed_data = data_type(**loads(str(request_data)))
            except JSONDecodeError:
                return self._malformed_request_response(event, request_data)
            except ValidationError as e:
                self._console.exception_error_print(event, e)
                return self._malformed_request_response(event, request_data)
            else:
                return str((await function(parsed_data)).to_json_string())
        return self._malformed_request_response(event, request_data)

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
            "CONNECTION REFUSED", f"Cannot connect {sid} as {self._client_sid} is already connected."
        )
        return False

    async def disconnect(self, sid: str) -> None:
        """Handle disconnections from the server.

        Args:
            sid: Socket session ID.
        """
        self._console.info_print("DISCONNECTED", sid)

        # Reset client SID if it matches.
        if self._client_sid == sid:
            self._client_sid = ""
        else:
            self._console.error_print("DISCONNECTION", f"Client {sid} disconnected without being connected.")

    # noinspection PyTypeChecker
    async def platform_event_handler(self, event: str, *args: tuple[Any]) -> str:
        """Handle events from the server.
        
        Matches incoming events based on the Socket.IO API.
        
        Args:
            event: Event name.
            args: Event arguments.
            
        Returns:
            Response data.
        """

        # Log event.
        self._console.debug_print("EVENT", event)

        # Handle event.
        match event:
            # Server metadata.
            case "get_version":
                return self._platform_handler.get_version()
            case "get_pinpoint_id":
                return str(self._platform_handler.get_pinpoint_id().to_json_string())
            case "get_platform_type":
                return self._platform_handler.get_platform_type()

            # Manipulator commands.
            case "get_manipulators":
                return str((await self._platform_handler.get_manipulators()).to_json_string())
            case "get_position":
                return await self._run_if_data_available(self._platform_handler.get_position, event, args)
            case "get_angles":
                return await self._run_if_data_available(self._platform_handler.get_angles, event, args)
            case "get_shank_count":
                return await self._run_if_data_available(self._platform_handler.get_shank_count, event, args)
            case "set_position":
                return await self._run_if_data_parses(
                    self._platform_handler.set_position, SetPositionRequest, event, args
                )
            case "set_depth":
                return await self._run_if_data_parses(self._platform_handler.set_depth, SetDepthRequest, event, args)
            case "set_inside_brain":
                return await self._run_if_data_parses(
                    self._platform_handler.set_inside_brain, SetInsideBrainRequest, event, args
                )
            case "stop":
                request_data = args[1]
                if request_data:
                    return await self._platform_handler.stop(str(request_data))
                return self._malformed_request_response(event, request_data)
            case "stop_all":
                return await self._platform_handler.stop_all()
            case _:
                self._console.error_print("EVENT", f"Unknown event: {event}.")
                return dumps({"error": "Unknown event."})
