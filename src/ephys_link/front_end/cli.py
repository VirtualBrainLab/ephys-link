"""Command-line interface for the Electrophysiology Manipulator Link.

Usage:
    Instantiate CLI and call `parse_args()` to get the parsed arguments.
    
    ```python
    CLI().parse_args()
    ```
"""

from argparse import ArgumentParser

from vbl_aquarium.models.ephys_link import EphysLinkOptions

from ephys_link.__about__ import __version__ as version


class CLI:
    """Command-line interface for the Electrophysiology Manipulator Link.

    Configures the CLI parser and options.
    """

    def __init__(self) -> None:
        """Initialize CLI parser."""

        self._parser = ArgumentParser(
            description="Electrophysiology Manipulator Link:"
            " a Socket.IO interface for manipulators in electrophysiology experiments.",
            prog="python -m ephys-link",
        )

        self._parser.add_argument(
            "-b", "--background", dest="background", action="store_true", help="Skip configuration window."
        )
        self._parser.add_argument(
            "-i",
            "--ignore-updates",
            dest="ignore_updates",
            action="store_true",
            help="Skip (ignore) checking for updates.",
        )
        self._parser.add_argument(
            "-t",
            "--type",
            type=str,
            dest="type",
            default="ump-4",
            help='Manipulator type (i.e. "ump-4", "ump-3", "pathfinder-mpm", "new-scale", "fake"). Default: "ump-4".',
        )
        self._parser.add_argument(
            "-d",
            "--debug",
            dest="debug",
            action="store_true",
            help="Enable debug mode.",
        )
        self._parser.add_argument(
            "-p",
            "--use-proxy",
            dest="use_proxy",
            action="store_true",
            help="Enable proxy mode.",
        )
        self._parser.add_argument(
            "-a",
            "--proxy-address",
            type=str,
            default="proxy2.virtualbrainlab.org",
            dest="proxy_address",
            help="Proxy IP address.",
        )
        self._parser.add_argument(
            "--mpm-port",
            type=int,
            default=8080,
            dest="mpm_port",
            help="Port New Scale Pathfinder MPM's server is on. Default: 8080.",
        )
        self._parser.add_argument(
            "-s",
            "--serial",
            type=str,
            default="no-e-stop",
            dest="serial",
            nargs="?",
            help="Emergency stop serial port (i.e. COM3). Default: disables emergency stop.",
        )
        self._parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"Electrophysiology Manipulator Link v{version}",
            help="Print version and exit.",
        )

    def parse_args(self) -> EphysLinkOptions:
        """Parse arguments and return them

        Returns:
            Parsed arguments
        """
        return EphysLinkOptions(**vars(self._parser.parse_args()))
