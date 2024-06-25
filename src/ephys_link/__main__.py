"""Ephys Link entry point

Responsible for gathering launch options, instantiating the appropriate interface, and starting the application.

Usage: call main() to start.
"""

from sys import argv

from ephys_link.front_end.cli import CLI


def main() -> None:
    """Ephys Link entry point

    1. Get options via CLI or GUI.
    2. Instantiate the Platform Handler with the appropriate platform bindings.
    3. Instantiate the Emergency Stop service.
    4. Start the server.
    """

    # 1. Get options via CLI or GUI (if no CLI options are provided).
    # TODO: add GUI options.
    options = CLI().parse_args() if len(argv) > 1 else None

    # 2. Instantiate the Platform Handler with the appropriate platform bindings.
    print(options)

if __name__ == "__main__":
    main()

