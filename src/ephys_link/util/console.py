"""Console class for printing messages to the console.

Configure the console to print error and debug messages.

Usage: Create a Console object and call the appropriate method to print messages.
"""

from colorama import Back, Fore, Style, init


class Console:
    def __init__(self, enable_debug: bool) -> None:
        """Initialize console properties.

        :param enable_debug: Enable debug mode.
        :type enable_debug: bool
        """
        self._enable_debug = enable_debug

        # Initialize colorama.
        init(autoreset=True)

    @staticmethod
    def err_print(msg: str) -> None:
        """Print an error message to the console.

        :param msg: Error message to print.
        :type msg: str
        """
        print(f"{Back.RED}{Style.BRIGHT} ERROR {Style.RESET_ALL}\t\t{Fore.RED}{msg}")

    def debug_print(self, msg: str) -> None:
        """Print a debug message to the console.

        :param msg: Debug message to print.
        :type msg: str
        """
        if self._enable_debug:
            print(f"{Back.BLUE}{Style.BRIGHT} DEBUG {Style.RESET_ALL}\t\t{Fore.BLUE}{msg}")
