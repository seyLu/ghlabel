import logging
import os
from logging import Logger
from logging.config import fileConfig

import rich

from ghlabel.config import is_ghlabel_debug_mode

GHLABEL_LOGS_DIR: str = os.path.join("logs")


class GhlabelLogger:
    def __init__(self) -> None:
        if not os.path.isdir(GHLABEL_LOGS_DIR):
            os.makedirs(GHLABEL_LOGS_DIR)
        fileConfig(os.path.join(os.path.dirname(__file__), "logging.ini"))

    def init(self, module_name: str) -> Logger:
        """NOTE: pass in __name__ as module name"""
        logger: Logger = logging.getLogger(module_name)

        if is_ghlabel_debug_mode():
            logger.setLevel(level=logging.DEBUG)
        else:
            logger.setLevel(level=logging.ERROR)

        return logger

    def exception(self, ex: Exception) -> None:
        rich.print(
            f"\nSomething went wrong. See logs ([blue underline]{GHLABEL_LOGS_DIR}[/blue underline]) for more details.\n"
        )
        rich.print("  [[red]Exception[/red]]:", str(ex))
        self.logger.exception(ex)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def info(self, message: str) -> None:
        self.logger.info(message)


ghlabel_logger: GhlabelLogger = GhlabelLogger()
