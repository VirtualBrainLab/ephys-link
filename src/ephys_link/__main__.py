"""Ephys Link entry point.

Responsible for gathering launch options, instantiating the appropriate interface, and starting the application.

Usage:
    ```python
    main()
    ```
"""

from asyncio import run
from sys import argv

from keyboard import add_hotkey

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.back_end.server import Server
from ephys_link.front_end.cli import CLI
from ephys_link.front_end.gui import GUI
from ephys_link.utils.console import Console
from ephys_link.utils.startup import check_for_updates, preamble


def main() -> None:
    """Ephys Link entry point."""

    # 0. Print the startup preamble.
    preamble()

    # 1. Get options via CLI or GUI (if no CLI options are provided).
    options = CLI().parse_args() if len(argv) > 1 else GUI().get_options()

    # 2. Instantiate the Console and make it globally accessible.
    console = Console(enable_debug=options.debug)

    # 3. Check for updates if not disabled.
    if not options.ignore_updates:
        check_for_updates(console)

    # 4. Instantiate the Platform Handler with the appropriate platform bindings.
    platform_handler = PlatformHandler(options, console)

    # 5. Instantiate the Emergency Stop service.
    _ = add_hotkey("ctrl+alt+shift+q", lambda: run(platform_handler.emergency_stop()))

    # 6. Start the server.
    Server(options, platform_handler, console).launch()


if __name__ == "__main__":
    main()
