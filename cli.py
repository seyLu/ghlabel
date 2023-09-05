#!/usr/bin/env python

"""Frontend CLI for scripts."""

__author__ = "seyLu"
__github__ = "github.com/seyLu"

__licence__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "seyLu"
__status__ = "Prototype"


import typer


def main(name: str, lastname: str = "", formal: bool = False) -> None:
    """
    Say hi to NAME, optionally with a --lastname.

    If --formal is used, say hi very formally.
    """

    if formal:
        print(f"Good day Ms. {name} {lastname}")
    else:
        print(f"Hello {name} {lastname}")


if __name__ == "__main__":
    typer.run(main)
