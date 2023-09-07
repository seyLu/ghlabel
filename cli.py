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
from scripts.setup_github_label import GithubConfig, GithubLabel

CTX_MAP_Type = TypedDict(
    "CTX_MAP_Type",
    {
        "github_config": GithubConfig | None,
        "github_label": GithubLabel | None,
    },
)

CTX_MAP: CTX_MAP_Type = {
    "github_config": None,
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
    new: Annotated[
        bool,
        typer.Option(
            "--new/--keep-old-labels",
            "-n/-k",
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
    DumpLabel.dump(dir=dir, new=new, ext=ext.value, app=app.value)


@app.callback()  # type: ignore[misc]
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
    token: Annotated[
        str,
        typer.Option(
            "--personal-access-token",
            "-t",
            help="Github Personal Access Token.",
        ),
    ]
    | None = None,
    repo_owner: Annotated[
        str,
        typer.Option(
            "--repo-owner",
            "-o",
            help="Target Github Repo Owner.",
        ),
    ]
    | None = None,
    repo_name: Annotated[
        str,
        typer.Option(
            "--repo",
            "-r",
            help="Target Github Repo.",
        ),
    ]
    | None = None,
) -> None:
    CTX_MAP["github_config"] = GithubConfig(
        token=token, repo_owner=repo_owner, repo_name=repo_name
    )


if __name__ == "__main__":
    app(obj={})
