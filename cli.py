#!/usr/bin/env python

"""Frontend CLI for scripts."""

__author__ = "seyLu"
__github__ = "github.com/seyLu"

__licence__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "seyLu"
__status__ = "Prototype"


import typer


def main(name: str) -> None:
    typer.secho(f"Welcome here {name}.", fg=typer.colors.CYAN)


if __name__ == "__main__":
    typer.run(main)
