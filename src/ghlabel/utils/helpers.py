import os
import platform
import subprocess
import sys

from dotenv import find_dotenv, load_dotenv

from ghlabel.__logger__ import GhlabelLogger, ghlabel_logger
from ghlabel.config import is_ghlabel_debug_mode

logger: GhlabelLogger = ghlabel_logger.init(__name__)
load_dotenv(find_dotenv(usecwd=True))

STATUS_OK: int = 200


def validate_env(env: str) -> str:
    _env: str | None = os.getenv(env)
    if not _env:
        logger.error(f"{env} environment variable not set.")
        sys.exit()
    return _env


def clear_screen() -> None:
    if not is_ghlabel_debug_mode():
        if platform.system() == "Windows":
            subprocess.run("cls", shell=True, check=False)  # noqa: S607, S602
        else:
            subprocess.run("clear", shell=True, check=False)  # noqa: S607, S602
