#!/usr/bin/env python

"""Frontend CLI for scripts."""

__author__ = "seyLu"
__github__ = "github.com/seyLu"

__licence__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "seyLu"
__status__ = "Prototype"


import os
from enum import Enum
from typing import Annotated, TypedDict

import typer

from scripts.dump_label import DumpLabel
from scripts.setup_github_label import GithubLabel

CTX_MAP_Type = TypedDict(
    "CTX_MAP_Type",
    {
        "github_label": GithubLabel | None,
    },
)

CTX_MAP: CTX_MAP_Type = {
    "github_label": None,
}


class AppChoices(str, Enum):
    app = "app"
    game = "game"
    web = "web"


class ExtChoices(str, Enum):
    json = "json"
    yaml = "yaml"


def version_callback(show_version: bool) -> None:
    if show_version:
        print(f"{os.path.basename(__file__)} {__version__}")
        raise typer.Exit()


app = typer.Typer()
setup_app = typer.Typer()

app.add_typer(setup_app, name="setup")


@app.command("dump")  # type: ignore[misc]
def dump_main(
    init: Annotated[
        bool,
        typer.Option(
            "--init/--no-init",
            "-i/-n",
            help="Deletes all files in labels dir.",
        ),
    ] = True,
    dir: Annotated[
        str,
        typer.Option(
            "--dir",
            "-d",
            help="Specify the dir where to find labels.",
        ),
    ] = "labels",
    ext: Annotated[
        ExtChoices,
        typer.Option(
            "--ext",
            "-e",
            case_sensitive=False,
            help="Label file extension.",
        ),
    ] = ExtChoices.yaml.value,  # type: ignore[assignment]
    app: Annotated[
        AppChoices,
        typer.Option(
            "--app",
            "-a",
            case_sensitive=False,
            help="App to determine label template.",
        ),
    ] = AppChoices.app.value,  # type: ignore[assignment]
) -> None:
    DumpLabel.dump(init=init, dir=dir, ext=ext.value, app=app.value)


@app.callback()  # type: ignore[misc]
def main(
    version: Annotated[
        bool,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = False
) -> None:
    pass


if __name__ == "__main__":
    app(obj={})
