#!/usr/bin/env python

"""Frontend CLI for scripts."""

__author__ = "seyLu"
__github__ = "github.com/seyLu"

__licence__ = "MIT"
__maintainer__ = "seyLu"
__status__ = "Prototype"

import json
import logging
import os
import time
from enum import Enum
from typing import Annotated, Optional

import rich
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from ghlabel.__about__ import __version__
from ghlabel.utils.dump_label import DumpLabel
from ghlabel.utils.github_api import GithubApi
from ghlabel.utils.github_api_types import GithubLabel
from ghlabel.utils.helpers import clear_screen, validate_env
from ghlabel.utils.setup_github_label import SetupGithubLabel


def parse_remove_labels(label_names: str | None) -> set[str] | None:
    if not label_names:
        return None
    return set(map(str.strip, label_names.split(",")))


def parse_add_labels(labels: str | None) -> list[GithubLabel] | None:
    if not labels:
        return None
    return list(json.loads(labels))


def version_callback(show_version: bool) -> None:
    if show_version:
        rich.print(
            f"\n[green]{os.path.basename(os.path.dirname(__file__))}[/green] {__version__}\n"
        )
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


app = typer.Typer(
    add_completion=False,
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)


@app.command("setup", help="Add/Remove Github labels from config files.")  # type: ignore[misc]
def setup_labels(  # noqa: PLR0913
    token: Annotated[
        Optional[str],
        typer.Argument(
            envvar="TOKEN",
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
    labels_dir: Annotated[
        str,
        typer.Option(
            "--directory",
            "-d",
            help="Specify the directory where to find labels.",
        ),
    ] = "labels",
    preview: Annotated[
        bool,
        typer.Option(
            "--preview/--no-preview",
            "-p/-P",
            help="Dry run and preview result before adding/removing labels from repo.",
        ),
    ] = False,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict/--no-strict",
            "-s/-S",
            help="Strictly mirror Github labels from labels config.",
        ),
    ] = False,
    add_labels: Annotated[
        Optional[str],
        typer.Option(
            "--add-labels",
            "-a",
            help="Add more Github labels.",
        ),
    ] = None,
    remove_labels: Annotated[
        Optional[str],
        typer.Option(
            "--remove-labels",
            "-r",
            help="Remove more Github labels.",
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
    force: Annotated[
        bool,
        typer.Option(
            "--force-remove/--safe-remove",
            "-f/-F",
            help="Forcefully remove GitHub labels, even if they are currently in use on issues or pull requests.",
        ),
    ] = False,
) -> None:
    if not token:
        token = validate_env("GITHUB_TOKEN")
    if not repo_owner:
        repo_owner = validate_env("GITHUB_REPO_OWNER")
    if not repo_name:
        repo_name = validate_env("GITHUB_REPO_NAME")
    gh_api: GithubApi = GithubApi(token, repo_owner, repo_name)

    clear_screen()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[green]Fetching...", total=None)

        gh_label = SetupGithubLabel(gh_api, labels_dir=labels_dir)

    if preview:
        rich.print(
            f"\n  [bold green]Preview [[/bold green]{repo_owner}/{repo_name}[bold green]][/bold green]"
        )
        rich.print()

    if remove_all.value == "enable":
        gh_label.remove_all_labels(preview=preview, force=force)
    elif remove_all.value == "silent":
        gh_label.remove_all_labels(silent=True, preview=preview, force=force)
    elif remove_all.value == "disable":
        gh_label.remove_labels(
            strict=strict,
            label_names=parse_remove_labels(remove_labels),
            preview=preview,
            force=force,
        )

    gh_label.add_labels(labels=parse_add_labels(add_labels), preview=preview)

    if gh_label.labels_unsafe_to_remove:
        if not preview:
            rich.print()
        rich.print("  The following labels are not [red]removed[/red]:")
        for label_name in gh_label.labels_unsafe_to_remove:
            rich.print(
                f'    - {label_name} \[{", ".join(url for url in gh_label.label_name_urls_map[label_name])}]'
            )
        rich.print()

    if not preview:
        rich.print(
            f"[green]Successfully[/green] setup github labels from config to repo `{repo_owner}/{repo_name}`."
        )


@app.command("dump", help="Generate starter labels config files.")  # type: ignore[misc]
def app_dump(
    new: Annotated[
        bool,
        typer.Option(
            "--new/--keep-old-labels",
            "-n/-N",
            help="Deletes all files in labels dir.",
        ),
    ] = True,
    labels_dir: Annotated[
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
    clear_screen()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Dumping...", total=None)
        time.sleep(0.5)
        DumpLabel.dump(labels_dir=labels_dir, new=new, ext=ext.value, app=app.value)
        time.sleep(0.5)

    rich.print(f"[green]Successfully[/green] dumped labels config to `{labels_dir}`.")


@app.callback()  # type: ignore[misc]
def app_callback(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-D",
            help="Enable debug mode and show logs.",
        ),
    ] = False,
) -> None:
    """Setup Github Labels from a yaml/json config file."""

    if not debug:
        logger = logging.getLogger("root")
        logger.setLevel(logging.ERROR)


if __name__ == "__main__":
    app()
