# ruff: noqa: T201
"""Console class for printing messages to the console.

Configure the console to print error and debug messages.

Usage: Create a Console object and call the appropriate method to print messages.
"""

from colorama import Back, Fore, Style, init


class Console:
    def __init__(self, *, enable_debug: bool) -> None:
        """Initialize console properties.

        :param enable_debug: Enable debug mode.
        :type enable_debug: bool
        """
        self._enable_debug = enable_debug

        # Initialize colorama.
        init(autoreset=True)

    @staticmethod
    def error_print(msg: str) -> None:
        """Print an error message to the console.

        :param msg: Error message to print.
        :type msg: str
        """
        print(f"{Back.RED}{Style.BRIGHT} ERROR {Style.RESET_ALL}\t\t{Fore.RED}{msg}")

    @staticmethod
    def pretty_exception(exception: Exception) -> str:
        """Pretty print an exception.

        :param exception: Exception to pretty print.
        :type exception: Exception
        :return: Pretty printed exception.
        :rtype: str
        """
        return f"{type(exception).__name__}: {exception}"

    @staticmethod
    def exception_error_print(source_label: str, exception: Exception) -> None:
        """Print an error message with exception details to the console.

        :param source_label: Label for the error message.
        :type source_label: str
        :param exception: Exception to print.
        :type exception: Exception
        """
        Console.error_print(f"{source_label}: {Console.pretty_exception(exception)}")

    def debug_print(self, msg: str) -> None:
        """Print a debug message to the console.

        :param msg: Debug message to print.
        :type msg: str
        """
        if self._enable_debug:
            print(f"{Back.BLUE}{Style.BRIGHT} DEBUG {Style.RESET_ALL}\t\t{Fore.BLUE}{msg}")

    @staticmethod
    def info_print(label: str, msg: str) -> None:
        """Print info to console.

        :param label: Label for the message.
        :type label: str
        :param msg: Message to print.
        :type msg: str
        """
        print(f"{Back.GREEN}{Style.BRIGHT} {label} {Style.RESET_ALL}\t\t{Fore.GREEN}{msg}")
