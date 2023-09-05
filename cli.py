#!/usr/bin/env python

"""Frontend CLI for scripts."""

__author__ = "seyLu"
__github__ = "github.com/seyLu"

__licence__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "seyLu"
__status__ = "Prototype"


import random

import typer
from typing_extensions import Annotated


def get_name() -> str:
    return random.choice(["Deadpool", "Rick", "Morty", "Hiro"])


def main(name: Annotated[str, typer.Argument(default_factory=get_name)]) -> None:
    print(f"Hello {name}")


if __name__ == "__main__":
    typer.run(main)
