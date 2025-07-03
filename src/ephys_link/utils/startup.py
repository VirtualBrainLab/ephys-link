"""Program startup helper functions."""

from importlib import import_module
from inspect import getmembers, isclass
from pkgutil import iter_modules

from packaging.version import parse
from requests import ConnectionError, ConnectTimeout, get
from vbl_aquarium.models.ephys_link import EphysLinkOptions

from ephys_link.__about__ import __version__
from ephys_link.bindings.mpm_binding import MPMBinding
from ephys_link.front_end.console import Console
from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.constants import ASCII, BINDINGS_DIRECTORY, ump_4_3_deprecation_error, \
    unrecognized_platform_type_error


def preamble() -> None:
    """Print the server startup preamble."""
    print(ASCII)  # noqa: T201
    print(__version__)  # noqa: T201
    print()  # noqa: T201
    print("This is the Ephys Link server window.")  # noqa: T201
    print("You may safely leave it running in the background.")  # noqa: T201
    print("To stop it, close this window or press CTRL + Pause/Break.")  # noqa: T201
    print()  # noqa: T201


def check_for_updates(console: Console) -> None:
    """Check for updates to the Ephys Link.

    Args:
        console: Console instance for printing messages.
    """
    try:
        response = get("https://api.github.com/repos/VirtualBrainLab/ephys-link/tags", timeout=10)
        latest_version = str(response.json()[0]["name"])  # pyright: ignore [reportAny]
        if parse(latest_version) > parse(__version__):
            console.critical_print(f"Update available: {latest_version} (current: {__version__})")
            console.critical_print("Download at: https://github.com/VirtualBrainLab/ephys-link/releases/latest")
    except (ConnectionError, ConnectTimeout):
        console.error_print(
            "UPDATE", "Unable to check for updates. Ignore updates or use the the -i flag to disable checks.\n"
        )


def get_bindings() -> list[type[BaseBinding]]:
    """Get all binding classes from the bindings directory.

    Returns:
        List of binding classes.
    """
    return [
        binding_type
        for module in iter_modules([BINDINGS_DIRECTORY])
        for _, binding_type in getmembers(import_module(f"ephys_link.bindings.{module.name}"), isclass)
        if issubclass(binding_type, BaseBinding) and binding_type != BaseBinding
    ]


def get_binding_instance(options: EphysLinkOptions, console: Console) -> BaseBinding:
    """Get an instance of the requested binding class.

    Args:
        options: Ephys Link options.
        console: Console instance for printing messages.

    Raises:
        ValueError: If the platform type is not recognized.

    Returns:
        Instance of a platform binding class.
    """
    selected_type = options.type

    for binding_type in get_bindings():
        binding_cli_name = binding_type.get_cli_name()

        # Notify deprecation of "ump-4" and "ump-3" CLI options and fix.
        if selected_type in ("ump-4", "ump-3"):
            console.error_print(
                "DEPRECATION",
                ump_4_3_deprecation_error(selected_type),
            )
            selected_type = "ump"

        if binding_cli_name == selected_type:
            # Pass in HTTP port for Pathfinder MPM.
            if binding_cli_name == "pathfinder-mpm":
                return MPMBinding(options.mpm_port)

            # Otherwise just return the binding.
            return binding_type()

    # Raise an error if the platform type is not recognized.
    error_message = unrecognized_platform_type_error(selected_type)
    console.critical_print(error_message)
    raise ValueError(error_message)


def get_binding_display_to_cli_name() -> dict[str, str]:
    """Get mapping of display to CLI option names of the available platform bindings.

    Returns:
        Dictionary of platform binding display name to CLI option name.
    """
    return {binding_type.get_display_name(): binding_type.get_cli_name() for binding_type in get_bindings()}
