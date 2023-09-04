#!/usr/bin/env python

"""
CLI tool to help setup Github Issue labels
from a yaml/json config file.
"""

__author__ = "seyLu"
__github__ = "github.com/seyLu"

__licence__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "seyLu"
__status__ = "Prototype"

import json
import logging
import os
import sys
from dataclasses import dataclass
from logging.config import fileConfig
from typing import Any, Iterator

import requests
import yaml
from dotenv import load_dotenv
from requests.models import Response

load_dotenv()
fileConfig("logging.ini")


def validate_env(env: str) -> str:
    _env: str | None = os.getenv(env)
    if not _env:
        logging.error(f"{env} environment variable not set.")
        sys.exit()
    return _env


@dataclass(frozen=True)
class BasePath:
    CWD: str = os.path.dirname(__file__)
    LABELS: str = "labels"


@dataclass(frozen=True)
class LabelFile:
    _BASE_FILE: str = os.path.join(BasePath.CWD, "..", BasePath.LABELS, "labels")
    YAML: str = f"{_BASE_FILE}.yaml"
    JSON: str = f"{_BASE_FILE}.json"


@dataclass(frozen=True)
class GithubConfig:
    PERSONAL_ACCESS_TOKEN: str = validate_env("GITHUB_PERSONAL_ACCESS_TOKEN")
    REPO_OWNER: str = validate_env("GITHUB_REPO_OWNER")
    REPO_NAME: str = validate_env("GITHUB_REPO_NAME")


class GithubIssueLabel:
    def __init__(self, github_config: GithubConfig | None = None) -> None:
        if github_config is None:
            github_config = GithubConfig()

        self._url: str = f"https://api.github.com/repos/{github_config.REPO_OWNER}/{github_config.REPO_NAME}/labels"
        self._headers: dict[str, str] = {
            "Authorization": f"Bearer {github_config.PERSONAL_ACCESS_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self._github_labels: list[dict[str, str]] = self._fetch_github_labels()
        self._github_label_names: list[str] = [
            github_label["name"] for github_label in self.github_labels
        ]
        self._labels: list[dict[str, str]] = self._load_labels_from_config()

    @property
    def url(self) -> str:
        return self._url

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @property
    def github_labels(self) -> list[dict[str, str]]:
        return self._github_labels

    @property
    def github_label_names(self) -> list[str]:
        return self._github_label_names

    @property
    def labels(self) -> list[dict[str, str]]:
        return self._labels

    def _fetch_github_labels(self) -> list[dict[str, str]]:
        page: int = 1
        per_page: int = 100

        logging.info("Fetching list of github labels.")
        github_labels: list[Any] = []
        while True:
            params: dict[str, int] = {"page": page, "per_page": per_page}
            logging.info(f"Fetching page {page}.")
            res: Response = requests.get(
                self.url,
                headers=self.headers,
                params=params,
            )

            if res.status_code != 200:
                logging.error(
                    f"Status {res.status_code}. Failed to fetch list of github labels"
                )
                sys.exit()

            if not res.json():
                break

            github_labels.extend(res.json())
            page += 1

        return [
            {
                "name": github_label["name"],
                "color": github_label["color"],
                "description": github_label["description"],
            }
            for github_label in github_labels
        ]

    def _load_labels_from_config(self) -> list[dict[str, str]]:
        use_labels: list[dict[str, str]] = []
        labels: list[dict[str, str]] = []

        label_dir: str = "labels"
        files_in_label_dir: list[str] = os.listdir(label_dir)

        yaml_filenames: list[str] = list(
            filter(
                lambda f: (f.endswith(".yaml") or f.endswith(".yml"))
                and not f.startswith("_remove"),
                files_in_label_dir,
            )
        )
        json_filenames: list[str] = list(
            filter(
                lambda f: f.endswith(".json") and not f.startswith("_remove"),
                files_in_label_dir,
            )
        )

        label_filenames: list[str] = []
        label_ext: str | None = None

        if yaml_filenames:
            logging.info("Found YAML files. Loading labels from YAML config.")
            label_filenames.extend(yaml_filenames)
            label_ext = "yaml"
        elif json_filenames:
            logging.info("Found JSON files. Loading labels from JSON config.")
            label_filenames.extend(json_filenames)
            label_ext = "json"
        else:
            logging.error("No Yaml or JSON config file for labels.")
            sys.exit()

        for label_filename in label_filenames:
            logging.info(f"Loading labels from {label_filename}.")
            label_file: str = os.path.join(label_dir, label_filename)

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

    def _update_label(self, label: dict[str, str]) -> None:
        url: str = f"{self.url}/{label['name']}"
        label["new_name"] = label.pop("name")

        res: Response = requests.patch(url, headers=self.headers, json=label)

        if res.status_code != 200:
            logging.error(
                f"Status {res.status_code}. Failed to update label `{label['new_name']}`."
            )
        else:
            logging.info(f"Label `{label['new_name']}` updated successfully.")

    def remove_labels(self, labels: list[str] | None = None) -> None:
        label_dir: str = "labels"
        files_in_label_dir: list[str] = os.listdir(label_dir)
        remove_labels_yaml_filter: Iterator[str] = filter(
            lambda f: f.endswith(".yaml") and f.startswith("_remove"),
            files_in_label_dir,
        )
        remove_labels_json_filter: Iterator[str] = filter(
            lambda f: f.endswith(".json") and f.startswith("_remove"),
            files_in_label_dir,
        )

        remove_labels_yaml: str = next(remove_labels_yaml_filter, "")
        remove_labels_json: str = next(remove_labels_json_filter, "")

        label_file: str = ""
        label_ext: str = ""

        if remove_labels_yaml:
            label_file = os.path.join(label_dir, remove_labels_yaml)
            label_ext = "yaml"
        elif remove_labels_json:
            label_file = os.path.join(label_dir, remove_labels_json)
            label_ext = "json"

        remove_labels: list[str] = []

        with open(label_file) as f:
            if label_ext == "yaml":
                remove_labels = yaml.safe_load(f)
            elif label_ext == "json":
                remove_labels = json.load(f)

        logging.info(f"Deleting labels from {label_file}")
        for remove_label in remove_labels:
            if remove_label in self.github_label_names:
                url: str = f"{self.url}/{remove_label}"

                res: Response = requests.delete(
                    url,
                    headers=self.headers,
                )

                if res.status_code != 204:
                    logging.error(
                        f"Status {res.status_code}. Failed to delete label `{remove_label}`."
                    )
                else:
                    logging.info(f"Label `{remove_label}` deleted successfully.")

    def create_labels(self) -> None:
        for label in self.labels:
            if label["name"] in self.github_label_names:
                i: int = self.github_label_names.index(label["name"])

                if (
                    label["color"] != self.github_labels[i]["color"]
                    or label["description"] != self.github_labels[i]["description"]
                ):
                    self._update_label(label)

            else:
                res: Response = requests.post(
                    self.url,
                    headers=self.headers,
                    json=label,
                )

                if res.status_code != 201:
                    logging.error(
                        f"Status {res.status_code}. Failed to create label `{label['name']}`."
                    )
                else:
                    logging.info(f"Label `{label['name']}` created successfully.")


def main() -> None:
    github_issue_label = GithubIssueLabel()
    github_issue_label.remove_labels()
    github_issue_label.create_labels()
    logging.info("Label creation process completed.")


if __name__ == "__main__":
    main()
