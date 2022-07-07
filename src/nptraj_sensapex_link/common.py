DEBUG = False


def set_debug(debug: bool) -> None:
    """
    Set debug flag
    :param debug: True to enable debug mode, False to disable
    :return: None
    """
    global DEBUG
    DEBUG = debug


def dprint(message: str) -> None:
    """
    Print message if debug is enabled
    :param message: Message to print
    :return: None
    """
    if DEBUG:
        print(message)
