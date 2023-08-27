#!/usr/bin/env python

"""Docstring for script."""

__author__ = "seyLu"
__github__ = "github.com/seyLu"

__licence__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "seyLu"
__status__ = "Prototype"

from logging.config import fileConfig
from typing import Any


def main() -> None:
    pass


def function(*args: Any, **kwargs: dict[str, Any]) -> None:
    """Docstring for function."""

    pass


if __name__ == "__main__":
    fileConfig("logging.ini")
    main()
