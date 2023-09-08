#!/usr/bin/env python

"""Frontend CLI for scripts."""

__author__ = "seyLu"
__github__ = "github.com/seyLu"

__licence__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "seyLu"
__status__ = "Prototype"


import json
import logging
import os
import time
from enum import Enum
from typing import Annotated, Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from scripts.dump_label import DumpLabel
from scripts.setup_github_label import GithubConfig, GithubLabel


def parse_remove_labels(labels: str | None) -> list[str] | None:
    if not labels:
        return None
    return list(map(str.strip, labels.split(",")))


def parse_add_labels(labels: str | None) -> list[dict[str, str]] | None:
    if not labels:
        return None
    return list(json.loads(labels))


def version_callback(show_version: bool) -> None:
    if show_version:
        print(f"{os.path.basename(__file__)} {__version__}")
        raise typer.Exit()


class AppChoices(str, Enum):
    app = "app"
    game = "game"
    web = "web"


class ExtChoices(str, Enum):
    json = "json"
    yaml = "yaml"


class RemoveAllChoices(str, Enum):
    disable = "disable"
    enable = "enable"
    silent = "silent"


app = typer.Typer()


@app.command("setup")  # type: ignore[misc]
def setup_labels(
    token: Annotated[
        Optional[str],
        typer.Argument(
            envvar="PERSONAL_ACCESS_TOKEN",
            show_default=False,
        ),
    ] = None,
    repo_owner: Annotated[
        Optional[str],
        typer.Argument(
            envvar="REPO_OWNER",
            show_default=False,
        ),
    ] = None,
    repo_name: Annotated[
        Optional[str],
        typer.Argument(
            envvar="REPO_NAME",
            show_default=False,
        ),
    ] = None,
    dir: Annotated[
        str,
        typer.Option(
            "--dir",
            "-d",
            help="Specify the dir where to find labels.",
        ),
    ] = "labels",
    strict: Annotated[
        bool,
        typer.Option(
            "--strict/--no-strict",
            "-s/-S",
            help="Strictly mirror Github labels from labels config.",
        ),
    ] = True,
    add_labels: Annotated[
        Optional[str],
        typer.Option(
            "--add-labels",
            "-a",
            help="Add more labels.",
        ),
    ] = None,
    remove_labels: Annotated[
        Optional[str],
        typer.Option(
            "--remove-labels",
            "-r",
            help="Remove more labels.",
        ),
    ] = None,
    remove_all: Annotated[
        RemoveAllChoices,
        typer.Option(
            "--remove-all",
            "-R",
            help="Remove all Github labels.",
        ),
    ] = RemoveAllChoices.disable.value,  # type: ignore[assignment]
) -> None:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[green]Fetching...", total=None)
        if token:
            GithubConfig.set_PERSONAL_ACCESS_TOKEN(token)
        if repo_owner:
            GithubConfig.set_REPO_OWNER(repo_owner)
        if repo_name:
            GithubConfig.set_REPO_NAME(repo_name)
        github_config = GithubConfig()
        github_label = GithubLabel(github_config=github_config, dir=dir)

    with Progress(
        SpinnerColumn(style="[magenta]"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[magenta]Removing...", total=None)
        if remove_all.value == "enable":
            github_label.remove_all_labels()
        elif remove_all.value == "silent":
            github_label.remove_all_labels(silent=True)
        elif remove_all.value == "disable":
            github_label.remove_labels(
                strict=strict, labels=parse_remove_labels(remove_labels)
            )

    with Progress(
        SpinnerColumn(style="[cyan]"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[cyan]Adding...", total=None)
        github_label.add_labels(labels=parse_add_labels(add_labels))


@app.command("dump")  # type: ignore[misc]
def app_dump(
    new: Annotated[
        bool,
        typer.Option(
            "--new/--keep-old-labels",
            "-n/-N",
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
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Dumping...", total=None)
        time.sleep(0.5)
        DumpLabel.dump(dir=dir, new=new, ext=ext.value, app=app.value)
        time.sleep(0.5)


@app.callback()  # type: ignore[misc]
def app_callback(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-D",
        ),
    ] = False,
) -> None:
    if not debug:
        logger = logging.getLogger("root")
        logger.setLevel(logging.ERROR)


if __name__ == "__main__":
    app()
