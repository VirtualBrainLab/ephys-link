"""Console class for printing messages to the console.

Configure the console to print error and debug messages.

Usage:
    Create a Console object and call the appropriate method to print messages.
"""

from logging import DEBUG, ERROR, INFO, basicConfig, getLogger
from typing import final

from rich.logging import RichHandler
from rich.traceback import install


@final
class Console:
    def __init__(self, *, enable_debug: bool = False) -> None:
        """Initialize console properties.

        Args:
            enable_debug: Enable debug mode.
        """
        # Repeat message fields.
        self._last_message = (0, "", "")
        self._repeat_counter = 0

        # Config logger.
        basicConfig(
            format="%(message)s",
            datefmt="[%I:%M:%S %p]",
            handlers=[RichHandler(rich_tracebacks=True, markup=True)],
        )
        self._log = getLogger("rich")
        self._log.setLevel(DEBUG if enable_debug else INFO)

        # Install Rich traceback.
        _ = install()

    def debug_print(self, label: str, msg: str) -> None:
        """Print a debug message to the console.

        Args:
            label: Label for the debug message.
            msg: Debug message to print.
        """
        self._repeatable_log(DEBUG, f"[b green]{label}", f"[green]{msg}")

    def info_print(self, label: str, msg: str) -> None:
        """Print info to console.

        Args:
            label: Label for the message.
            msg: Message to print.
        """
        self._repeatable_log(INFO, f"[b blue]{label}", msg)

    def error_print(self, label: str, msg: str) -> None:
        """Print an error message to the console.

        Args:
            label: Label for the error message.
            msg: Error message to print.
        """
        self._repeatable_log(ERROR, f"[b red]{label}", f"[red]{msg}")

    def critical_print(self, msg: str) -> None:
        """Print a critical message to the console.

        Args:
            msg: Critical message to print.
        """
        self._log.critical(f"[b i red]{msg}")

    @staticmethod
    def pretty_exception(exception: Exception) -> str:
        """Pretty print an exception.

        Args:
            exception: Exception to pretty print.

        Returns:
            Pretty printed exception.
        """
        return f"{type(exception).__name__}: {exception}"

    def exception_error_print(self, label: str, exception: Exception) -> None:
        """Print an error message with exception details to the console.

        Args:
            label: Label for the error message.
            exception: Exception to print.
        """
        self._log.exception(f"[b magenta]{label}:[/] [magenta]{Console.pretty_exception(exception)}")

    # Helper methods.
    def _repeatable_log(self, log_type: int, label: str, message: str) -> None:
        """Add a row to the output table.

        Args:
            log_type: Type of log.
            label: Label for the message.
            message: Message.
        """

        # Compute if this is a repeated message.
        message_set = (log_type, label, message)
        if message_set == self._last_message:
            # Handle repeat.
            self._repeat_counter += 1

            # Add an ellipsis row for first repeat.
            if self._repeat_counter == 1:
                self._log.log(log_type, "...")
        else:
            # Handle novel message.
            if self._repeat_counter > 0:
                # Complete previous repeat.
                self._log.log(
                    self._last_message[0],
                    f"{self._last_message[1]}:[/] {self._last_message[2]}[/] x {self._repeat_counter}",
                )
                self._repeat_counter = 0

            # Log new message.
            self._log.log(log_type, f"{label}:[/] {message}")
            self._last_message = message_set
