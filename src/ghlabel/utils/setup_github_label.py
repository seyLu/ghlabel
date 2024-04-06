#!/usr/bin/env python

"""
CLI tool to help setup Github Issue labels
from a yaml/json config file.
"""

__author__ = "seyLu"
__github__ = "github.com/seyLu"

__licence__ = "MIT"
__maintainer__ = "seyLu"
__status__ = "Prototype"

import json
import logging
import os
import sys
from logging.config import fileConfig
from pathlib import Path

import rich
import yaml
from dotenv import load_dotenv
from rich.progress import Progress
from rich.prompt import Confirm

from ghlabel.utils.github_api import GithubApi
from ghlabel.utils.github_api_types import GithubIssue, GithubLabel
from ghlabel.utils.helpers import (
    STATUS_OK,
    clear_screen,
    validate_env,
)

load_dotenv()
Path("logs").mkdir(exist_ok=True)
fileConfig(os.path.join(os.path.dirname(__file__), "../logging.ini"))


class SetupGithubLabel:
    def __init__(
        self,
        gh_api: GithubApi,
        labels_dir: str = "labels",
    ) -> None:
        self._labels_dir = labels_dir
        self._gh_api = gh_api

        self._github_labels: list[GithubLabel] = self._fetch_formatted_github_labels()
        self._github_label_names: list[str] = [
            # requires index, so using list instead of set
            github_label["name"]
            for github_label in self.github_labels
        ]
        self._labels: list[GithubLabel] = self._load_labels_from_config() or []
        self._label_name_urls_map: dict[str, set[str]] = {}
        self._labels_unsafe_to_remove: set[str] = set()
        self._labels_force_remove: set[str] = set()

    @property
    def labels_dir(self) -> str:
        return self._labels_dir

    @property
    def github_labels(self) -> list[GithubLabel]:
        return self._github_labels

    @property
    def github_label_names(self) -> list[str]:
        # requires index, so using list instead of set
        return self._github_label_names

    @property
    def labels(self) -> list[GithubLabel]:
        return self._labels

    @property
    def label_name_urls_map(self) -> dict[str, set[str]]:
        return self._label_name_urls_map

    @property
    def labels_unsafe_to_remove(self) -> set[str]:
        return self._labels_unsafe_to_remove

    @property
    def labels_force_remove(self) -> set[str]:
        return self._labels_force_remove

    @property
    def gh_api(self) -> GithubApi:
        return self._gh_api

    def set_labels_force_remove(self, label_names: set[str]) -> None:
        return self._labels_force_remove.update(label_names)

    def _fetch_formatted_github_labels(self) -> list[GithubLabel]:
        github_labels, status_code = self.gh_api.list_labels()
        if status_code != STATUS_OK:
            sys.exit()
        return list(map(self._format_github_label, github_labels))

    def _format_github_label(self, github_label: GithubLabel) -> GithubLabel:
        return {  # type: ignore[return-value]
            key: val
            for key, val in github_label.items()
            if key not in ["id", "node_id", "url", "default"]
        }

    def _list_labels_safe_to_remove(
        self, label_names: set[str] | None = None
    ) -> set[str]:
        all_labels_to_remove: set[str] = self._load_labels_to_remove_from_config()
        if label_names:
            all_labels_to_remove.update(label_names)
        labels_unsafe_to_remove: set[str] = set()

        gh_issues: list[GithubIssue]
        gh_issues, status_code = self.gh_api.list_issues()
        if status_code != STATUS_OK:
            sys.exit()
        for issue in gh_issues:
            url = issue["html_url"]
            if "pull_request" in issue:
                url = issue["pull_request"]["html_url"]

            for label in issue["labels"]:
                labels_unsafe_to_remove.add(label["name"])
                if label["name"] not in self._label_name_urls_map:
                    self._label_name_urls_map[label["name"]] = set([url])
                else:
                    self._label_name_urls_map[label["name"]].add(url)

        self._labels_unsafe_to_remove = labels_unsafe_to_remove
        return all_labels_to_remove - labels_unsafe_to_remove

    def _load_labels_from_config(self) -> list[GithubLabel]:
        use_labels: list[GithubLabel] = []
        labels: list[GithubLabel] = []
        files_in_labels_dir: list[str] = []

        try:
            files_in_labels_dir = os.listdir(self.labels_dir)
        except FileNotFoundError:
            logging.error(
                f"No {self.labels_dir} dir found. To solve this issue, first run `ghlabel dump`."
            )
            sys.exit()

        yaml_filenames: list[str] = list(
            filter(
                lambda f: (f.endswith(".yaml") or f.endswith(".yml"))
                and not f.startswith("_remove"),
                files_in_labels_dir,
            )
        )
        json_filenames: list[str] = list(
            filter(
                lambda f: f.endswith(".json") and not f.startswith("_remove"),
                files_in_labels_dir,
            )
        )

        label_filenames: list[str] = []
        label_ext: str = ""

        if yaml_filenames:
            logging.info("Found YAML files. Loading labels from YAML config.")
            label_filenames.extend(yaml_filenames)
            label_ext = "yaml"
        elif json_filenames:
            logging.info("Found JSON files. Loading labels from JSON config.")
            label_filenames.extend(json_filenames)
            label_ext = "json"
        else:
            logging.error(
                "No Yaml or JSON config file found for labels. To solve this issue, first run `ghlabel dump`."
            )
            sys.exit()

        for label_filename in label_filenames:
            logging.info(f"Loading labels from {label_filename}.")
            label_file: str = os.path.join(self.labels_dir, label_filename)

            with open(label_file, "r") as f:
                if label_ext == "yaml":
                    use_labels = yaml.safe_load(f)
                elif label_ext == "json":
                    use_labels = json.load(f)

                for i, label in enumerate(use_labels, start=1):
                    if not label.get("name"):
                        logging.error(
                            f"Error on {label_filename}. Name not found on `Label #{i}` with color `{label.get('color')}` and description `{label.get('description')}`."
                        )
                        sys.exit()

                    labels.append(
                        {
                            "name": label["name"],
                            "color": label.get("color", "").replace("#", ""),
                            "description": label.get("description", ""),
                        }
                    )

        return labels

    def _load_labels_to_remove_from_config(self) -> set[str]:
        labels_to_remove: list[str] = []

        files_in_labels_dir: list[str] = os.listdir(self.labels_dir)

        label_to_remove_yaml: list[str] = list(
            filter(
                lambda f: (f.endswith(".yaml") or f.endswith("yml"))
                and f.startswith("_remove"),
                files_in_labels_dir,
            )
        )
        label_to_remove_json: list[str] = list(
            filter(
                lambda f: f.endswith(".json") and f.startswith("_remove"),
                files_in_labels_dir,
            )
        )

        label_to_remove_file: str = ""
        label_to_remove_ext: str = ""

        if label_to_remove_yaml:
            label_to_remove_file = os.path.join(
                self.labels_dir, label_to_remove_yaml[0]
            )
            label_to_remove_ext = "yaml"
        elif label_to_remove_json:
            label_to_remove_file = os.path.join(
                self.labels_dir, label_to_remove_json[0]
            )
            label_to_remove_ext = "json"

        logging.info(f"Deleting labels from {label_to_remove_file}")
        with open(label_to_remove_file) as f:
            if label_to_remove_ext == "yaml":
                labels_to_remove = yaml.safe_load(f)
            elif label_to_remove_ext == "json":
                labels_to_remove = json.load(f)

        return set(labels_to_remove)

    def remove_all_labels(
        self, silent: bool = False, preview: bool = False, force: bool = False
    ) -> None:
        confirmation: bool = False

        if silent is False and not preview:
            rich.print(
                "[[yellow]WARNING[/yellow]] This action will [red]remove[/red] all labels in the repository."
            )
            confirmation = Confirm.ask("Are you sure you want to continue?")
        else:
            confirmation = True

        if confirmation:
            self.remove_labels(
                label_names=set(self.github_label_names), preview=preview, force=force
            )

    def remove_labels(
        self,
        label_names: set[str] | None = None,
        strict: bool = False,
        preview: bool = False,
        force: bool = False,
    ) -> None:
        labels_to_remove: set[str] = set()
        labels_safe_to_remove: set[str]

        if strict:
            labels_to_remove.update(
                set(self.github_label_names)
                - set([label["name"] for label in self.labels])
            )

        if label_names:
            labels_to_remove.update(label_names)

        if not force:
            labels_safe_to_remove = self._list_labels_safe_to_remove(
                label_names=labels_to_remove
            )
        else:
            labels_safe_to_remove = labels_to_remove

        if preview:
            rich.print("  will [red]remove[/red] the following labels:")
            is_remove_label: bool = False

            for label in labels_to_remove:
                if label in self.github_label_names:
                    is_remove_label = True
                    rich.print(f"    - {label}")

            if not is_remove_label:
                rich.print("    None")

            rich.print()
            return

        clear_screen()
        with Progress(transient=True) as progress:
            task_id = progress.add_task(
                "[red]Removing...[/red]", total=len(labels_safe_to_remove)
            )

            for label_name in labels_safe_to_remove:
                if label_name in self.github_label_names:
                    self.gh_api.delete_label(label_name)
                    progress.update(
                        task_id,
                        advance=1,
                        description=f"[red]Removed[/red] Label `{label_name}`",
                    )

    def update_labels(self, labels: list[GithubLabel], preview: bool = False) -> None:
        if preview and labels:
            rich.print("  will [yellow]update[/yellow] the following labels:")
            is_update_label: bool = False

            for label in labels:
                if label["name"] in self.github_label_names:
                    i: int = self.github_label_names.index(label["name"])

                    is_update_label = True
                    rich.print(f"    [red]- {self.github_labels[i]}[/red]")
                    rich.print(f"    [green]+ {label}[/green]")

            if not is_update_label:
                rich.print("    None")

            rich.print()
            return

        if preview and labels:
            clear_screen()
        with Progress(transient=True) as progress:
            task_id = progress.add_task(
                "[yellow]Updating...[/yellow]", total=len(labels)
            )

            for label in labels:
                self.gh_api.update_label(label)
                progress.update(
                    task_id,
                    advance=1,
                    description=f'[yellow]Updated[/yellow] Label `{label["new_name"]}`',
                )

    def add_labels(
        self, labels: list[GithubLabel] | None = None, preview: bool = False
    ) -> None:
        pre_labels_to_add: list[GithubLabel] = self.labels
        labels_to_add: list[GithubLabel] = []
        labels_to_update: list[GithubLabel] = []

        if labels:
            for _i, label in enumerate(labels, start=1):
                if not label.get("name"):
                    logging.error(
                        f"Error on argument label. Name not found on `Label #{_i}` with color `{label.get('color')}` and description `{label.get('description')}`."
                    )
                    sys.exit()

                pre_labels_to_add.append(
                    {
                        "name": label["name"],
                        "color": label.get("color", "").replace("#", ""),
                        "description": label.get("description", ""),
                    }
                )

        for label in pre_labels_to_add:
            if label["name"] in self.github_label_names:
                i: int = self.github_label_names.index(label["name"])

                if (
                    label["color"] != self.github_labels[i]["color"]
                    or label["description"] != self.github_labels[i]["description"]
                ):
                    labels_to_update.append(label)
            else:
                labels_to_add.append(label)

        if preview:
            rich.print("  will [cyan]add[/cyan] the following labels:")
            is_add_label: bool = False

            for label in labels_to_add:
                is_add_label = True
                rich.print(f"    - {label}")

            if not is_add_label:
                rich.print("    None")

            rich.print()
            self.update_labels(labels_to_update, preview=preview)
            return

        clear_screen()
        with Progress(transient=True) as progress:
            task_id = progress.add_task(
                "[cyan]Adding...[/cyan]", total=len(labels_to_add)
            )

            for label in labels_to_add:
                self.gh_api.create_label(label)
                progress.update(
                    task_id,
                    advance=1,
                    description=f'[cyan]Added[/cyan] Label `{label["name"]}`',
                )

        self.update_labels(labels_to_update, preview=preview)
        logging.info("Label creation process completed.")


if __name__ == "__main__":
    gh_api = GithubApi(
        validate_env("GITHUB_TOKEN"),
        validate_env("GITHUB_REPO_OWNER"),
        validate_env("GITHUB_REPO_NAME"),
    )
    gh_label = SetupGithubLabel(gh_api)
    gh_label.remove_labels()
    gh_label.add_labels()
