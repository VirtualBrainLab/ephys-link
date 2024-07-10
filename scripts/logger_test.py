import logging

from rich.logging import RichHandler

logging.basicConfig(level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])

log = logging.getLogger("rich")
log.debug("This message should go to the log file")
log.info("So should this")
log.warning("And this, too")
log.error("And non-ASCII stuff, too, like Øresund and Malmö")
log.error("[bold red blink]Server is shutting down!", extra={"markup": True})
log.critical("Critical error! [b red]Server is shutting down!", extra={"markup": True})
try:
    print(1 / 0)
except Exception:
    log.exception("[b magenta]unable print![/] [i magenta]asdf", extra={"markup": True})
