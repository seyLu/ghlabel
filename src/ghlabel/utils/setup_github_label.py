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
from typing import Any

import requests
import yaml
from dotenv import load_dotenv
from requests.exceptions import Timeout
from requests.models import Response

load_dotenv()
Path("logs").mkdir(exist_ok=True)
fileConfig(os.path.join(os.path.dirname(__file__), "../logging.ini"))


def validate_env(env: str) -> str:
    _env: str | None = os.getenv(env)
    if not _env:
        logging.error(f"{env} environment variable not set.")
        sys.exit()
    return _env


class GithubConfig:
    _TOKEN: str = validate_env("GITHUB_TOKEN")
    _REPO_OWNER: str = validate_env("GITHUB_REPO_OWNER")
    _REPO_NAME: str = validate_env("GITHUB_REPO_NAME")

    @property
    def TOKEN(self) -> str:
        return GithubConfig._TOKEN

    @property
    def REPO_OWNER(self) -> str:
        return GithubConfig._REPO_OWNER

    @property
    def REPO_NAME(self) -> str:
        return GithubConfig._REPO_NAME

    @staticmethod
    def set_TOKEN(token: str) -> None:
        GithubConfig._TOKEN = token

    @staticmethod
    def set_REPO_OWNER(repo_owner: str) -> None:
        GithubConfig._REPO_OWNER = repo_owner

    @staticmethod
    def set_REPO_NAME(repo_name: str) -> None:
        GithubConfig._REPO_NAME = repo_name


class GithubLabel:
    def __init__(
        self,
        github_config: GithubConfig | None = None,
        dir: str = "labels",
    ) -> None:
        if github_config is None:
            github_config = GithubConfig()

        self._url: str = f"https://api.github.com/repos/{github_config.REPO_OWNER}/{github_config.REPO_NAME}/labels"
        self._headers: dict[str, str] = {
            "Authorization": f"Bearer {github_config.TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self._dir: str = dir
        self._github_labels: list[dict[str, str]] = self._fetch_github_labels(
            github_config
        )
        self._github_label_names: list[str] = [
            github_label["name"] for github_label in self.github_labels
        ]
        self._labels: list[dict[str, str]] = self._load_labels_from_config() or []
        self._labels_to_remove: list[str] = (
            self._load_labels_to_remove_from_config() or []
        )

    @property
    def dir(self) -> str:
        return self._dir

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

    @property
    def labels_to_remove(self) -> list[str]:
        return self._labels_to_remove

    def _fetch_github_labels(self, github_config: GithubConfig) -> list[dict[str, str]]:
        page: int = 1
        per_page: int = 100

        logging.info(
            f"Fetching list of github labels from `{github_config.REPO_OWNER}/{github_config.REPO_NAME}`."
        )
        github_labels: list[Any] = []
        while True:
            params: dict[str, int] = {"page": page, "per_page": per_page}
            logging.info(f"Fetching page {page}.")
            try:
                res: Response = requests.get(
                    self.url,
                    headers=self.headers,
                    params=params,
                    timeout=10,
                )
            except Timeout:
                logging.error(
                    "The site can't be reached, `github.com` took to long to respond. Try checking the connection."
                )
                sys.exit()

            if res.status_code != 200:
                logging.error(
                    f"Status {res.status_code}. Failed to fetch list of github labels. Supplied token might not have permission to access `{github_config.REPO_OWNER}/{github_config.REPO_NAME}`."
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
        files_in_dir: list[str] = []

        try:
            files_in_dir = os.listdir(self.dir)
        except FileNotFoundError:
            logging.error(
                f"No {self.dir} dir found. To solve this issue, first run `ghlabel dump`."
            )
            sys.exit()

        yaml_filenames: list[str] = list(
            filter(
                lambda f: (f.endswith(".yaml") or f.endswith(".yml"))
                and not f.startswith("_remove"),
                files_in_dir,
            )
        )
        json_filenames: list[str] = list(
            filter(
                lambda f: f.endswith(".json") and not f.startswith("_remove"),
                files_in_dir,
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
            label_file: str = os.path.join(self.dir, label_filename)

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

    def _load_labels_to_remove_from_config(self) -> list[str]:
        labels_to_remove: list[str] = []

        files_in_dir: list[str] = os.listdir(self.dir)

        label_to_remove_yaml: list[str] = list(
            filter(
                lambda f: (f.endswith(".yaml") or f.endswith("yml"))
                and f.startswith("_remove"),
                files_in_dir,
            )
        )
        label_to_remove_json: list[str] = list(
            filter(
                lambda f: f.endswith(".json") and f.startswith("_remove"),
                files_in_dir,
            )
        )

        label_to_remove_file: str = ""
        label_to_remove_ext: str = ""

        if label_to_remove_yaml:
            label_to_remove_file = os.path.join(self.dir, label_to_remove_yaml[0])
            label_to_remove_ext = "yaml"
        elif label_to_remove_json:
            label_to_remove_file = os.path.join(self.dir, label_to_remove_json[0])
            label_to_remove_ext = "json"

        logging.info(f"Deleting labels from {label_to_remove_file}")
        with open(label_to_remove_file) as f:
            if label_to_remove_ext == "yaml":
                labels_to_remove = yaml.safe_load(f)
            elif label_to_remove_ext == "json":
                labels_to_remove = json.load(f)

        return labels_to_remove

    def _update_label(self, label: dict[str, str]) -> None:
        url: str = f"{self.url}/{label['name']}"
        label["new_name"] = label.pop("name")

        try:
            res: Response = requests.patch(
                url,
                headers=self.headers,
                json=label,
                timeout=10,
            )
        except Timeout:
            logging.error(
                "The site can't be reached, `github.com` took to long to respond. Try checking the connection."
            )
            sys.exit()

        if res.status_code != 200:
            logging.error(
                f"Status {res.status_code}. Failed to update label `{label['new_name']}`."
            )
        else:
            logging.info(f"Label `{label['new_name']}` updated successfully.")

    def remove_all_labels(self, silent: bool = False) -> None:
        confirmation: bool = False

        if silent is False:
            confirmation = input(
                "WARNING: This action will delete all labels in the repository.\n"
                "Are you sure you want to continue? (yes/no): "
            ).strip().lower() in ("y", "yes")
        else:
            confirmation = True

        if confirmation:
            self.remove_labels(labels=self.github_label_names)

    def remove_labels(
        self, labels: list[str] | None = None, strict: bool = False
    ) -> None:
        remove_labels: list[str] = self.labels_to_remove

        if strict:
            remove_labels.extend(
                list(
                    set(self.github_label_names)
                    - set([label["name"] for label in self.labels])
                )
            )

        if labels:
            remove_labels.extend(labels)

        for remove_label in remove_labels:
            if remove_label in self.github_label_names:
                url: str = f"{self.url}/{remove_label}"

                try:
                    res: Response = requests.delete(
                        url,
                        headers=self.headers,
                        timeout=10,
                    )
                except Timeout:
                    logging.error(
                        "The site can't be reached, `github.com` took to long to respond. Try checking the connection."
                    )
                    sys.exit()

                if res.status_code != 204:
                    logging.error(
                        f"Status {res.status_code}. Failed to delete label `{remove_label}`."
                    )
                else:
                    logging.info(f"Label `{remove_label}` deleted successfully.")

    def add_labels(self, labels: list[dict[str, str]] | None = None) -> None:
        add_labels: list[dict[str, str]] = self.labels

        if labels:
            for _i, label in enumerate(labels, start=1):
                if not label.get("name"):
                    logging.error(
                        f"Error on argument label. Name not found on `Label #{_i}` with color `{label.get('color')}` and description `{label.get('description')}`."
                    )
                    sys.exit()

                add_labels.append(
                    {
                        "name": label["name"],
                        "color": label.get("color", "").replace("#", ""),
                        "description": label.get("description", ""),
                    }
                )

        for label in add_labels:
            if label["name"] not in self.labels_to_remove:
                if label["name"] in self.github_label_names:
                    i: int = self.github_label_names.index(label["name"])

                    if (
                        label["color"] != self.github_labels[i]["color"]
                        or label["description"] != self.github_labels[i]["description"]
                    ):
                        self._update_label(label)

                else:
                    try:
                        res: Response = requests.post(
                            self.url,
                            headers=self.headers,
                            json=label,
                            timeout=10,
                        )
                    except Timeout:
                        logging.error(
                            "The site can't be reached, `github.com` took to long to respond. Try checking the connection."
                        )
                        sys.exit()

                    if res.status_code != 201:
                        logging.error(
                            f"Status {res.status_code}. Failed to add label `{label['name']}`."
                        )
                    else:
                        logging.info(f"Label `{label['name']}` added successfully.")

        logging.info("Label creation process completed.")


def main() -> None:
    github_label = GithubLabel()
    github_label.remove_labels()
    github_label.add_labels()


if __name__ == "__main__":
    main()
