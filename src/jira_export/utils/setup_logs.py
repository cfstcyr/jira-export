import logging

from rich.console import Console
from rich.logging import RichHandler


def setup_logs(*, verbose: bool) -> None:
    console = Console(stderr=True)
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )
