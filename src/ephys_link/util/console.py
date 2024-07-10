# ruff: noqa: T201
"""Console class for printing messages to the console.

Configure the console to print error and debug messages.

Usage: Create a Console object and call the appropriate method to print messages.
"""

from datetime import datetime

from rich import console
from rich.box import SIMPLE_HEAVY
from rich.table import Table
from rich.traceback import install

# Constants.
TAB_BLOCK = "\t\t"


class Console:
    def __init__(self, *, enable_debug: bool) -> None:
        """Initialize console properties.

        :param enable_debug: Enable debug mode.
        :type enable_debug: bool
        """
        self._enable_debug = enable_debug

        # Repeat message fields.
        self._last_message = ("", "", "")
        self._repeat_counter = 0

        # Output table.
        self._table = Table(box=SIMPLE_HEAVY, highlight=True)
        self._table.add_column("Time")
        self._table.add_column("Type")
        self._table.add_column("Label")
        self._table.add_column("Message")
        self._table.add_column("Count")

        # Rich console object.
        self._console = console.Console()

        # Install Rich traceback handler.
        install(show_locals=True)

    def error_print(self, msg: str) -> None:
        """Print an error message to the console.

        :param msg: Error message to print.
        :type msg: str
        """
        self.labeled_error_print("", msg)

    def labeled_error_print(self, label: str, msg: str) -> None:
        """Print an error message with a label to the console.

        :param label: Label for the error message.
        :type label: str
        :param msg: Error message to print.
        :type msg: str
        """
        self._add_row("[bright_white on red] ERROR ", f"[red]{label}", f"[red]{msg}")

    @staticmethod
    def pretty_exception(exception: Exception) -> str:
        """Pretty print an exception.

        :param exception: Exception to pretty print.
        :type exception: Exception
        :return: Pretty printed exception.
        :rtype: str
        """
        return f"{type(exception).__name__}: {exception}"

    def exception_error_print(self, label: str, exception: Exception) -> None:
        """Print an error message with exception details to the console.

        :param label: Label for the error message.
        :type label: str
        :param exception: Exception to print.
        :type exception: Exception
        """
        self._add_row(
            "[bright_white on magenta] EXCEPTION ",
            f"[magenta]{label}",
            f"[magenta]{Console.pretty_exception(exception)}",
        )

        # Also print out the exception in debug mode.
        if self._enable_debug:
            self._console.print_exception(show_locals=True)

    def debug_print(self, label: str, msg: str) -> None:
        """Print a debug message to the console.

        :param label: Label for the debug message.
        :type label: str
        :param msg: Debug message to print.
        :type msg: str
        """
        if self._enable_debug:
            self._add_row("[bright_white on blue] DEBUG", f"[blue]{label}", msg)

    def info_print(self, label: str, msg: str) -> None:
        """Print info to console.

        :param label: Label for the message.
        :type label: str
        :param msg: Message to print.
        :type msg: str
        """
        self._add_row("[bright_white on green] INFO ", f"[green]{label}", msg)

    # Helper methods.
    def _add_row(self, log_type: str, label: str, message: str) -> None:
        """Add a row to the output table.

        :param log_type: Type of log.
        :type log_type: str
        :param label: Label for the message.
        :type label: str
        :param message: Message.
        :type message: str
        """

        # Compute if this is a repeated message.
        message_set = (log_type, label, message)
        if message_set == self._last_message:
            # Handle repeat.
            self._repeat_counter += 1

            # Add an ellipsis row for first repeat.
            if self._repeat_counter == 1:
                self._table.add_row("", "", "...", "...", "")
        else:
            # Handle novel message.
            time_stamp = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

            # Complete previous repeat.
            if self._repeat_counter > 0:
                self._table.add_row(
                    time_stamp,
                    self._last_message[0],
                    self._last_message[1],
                    self._last_message[2],
                    f"x {self._repeat_counter}",
                )
                self._repeat_counter = 0

            self._table.add_row(time_stamp, log_type, label, message, "")
            self._last_message = message_set

    # Getters.
    def get_table(self) -> Table:
        """Return the output table.

        :return: Output table.
        :rtype: Table
        """
        return self._table
