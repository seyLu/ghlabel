import logging
import os
import platform
import subprocess
import sys
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
Path("logs").mkdir(exist_ok=True)
fileConfig(os.path.join(os.path.dirname(__file__), "../logging.ini"))

STATUS_OK: int = 200


def validate_env(env: str) -> str:
    _env: str | None = os.getenv(env)
    if not _env:
        logging.error(f"{env} environment variable not set.")
        sys.exit()
    return _env


def clear_screen() -> None:
    if platform.system() == "Windows":
        subprocess.run("cls", shell=True, check=False)  # noqa: S607, S602
    else:
        subprocess.run("clear", shell=True, check=False)  # noqa: S607, S602
