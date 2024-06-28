"""Ephys Link entry point.

Responsible for gathering launch options, instantiating the appropriate interface, and starting the application.

Usage: call main() to start.
"""

from sys import argv

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.back_end.server import Server
from ephys_link.front_end.cli import CLI
from ephys_link.front_end.gui import GUI
from ephys_link.util import common
from ephys_link.util.console import Console


def main() -> None:
    """Ephys Link entry point.

    1. Get options via CLI or GUI.
    2. Instantiate the Console and make it globally accessible.
    3. Instantiate the Platform Handler with the appropriate platform bindings.
    4. Instantiate the Emergency Stop service.
    5. Start the server.
    """

    # 1. Get options via CLI or GUI (if no CLI options are provided).
    options = CLI().parse_args() if len(argv) > 1 else GUI().get_options()

    # 2. Instantiate the Console and make it globally accessible.
    common.console = Console(enable_debug=options.debug)

    # 3. Instantiate the Platform Handler with the appropriate platform bindings.
    platform_handler = PlatformHandler(options.type)

    # 4. Instantiate the Emergency Stop service.

    # 5. Start the server.
    server = Server(options, platform_handler)
    server.launch()


if __name__ == "__main__":
    main()
