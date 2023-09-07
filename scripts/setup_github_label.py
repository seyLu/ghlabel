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
from logging.config import fileConfig
from typing import Any

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


class GithubConfig:
    def __init__(
        self,
        token: str | None = None,
        repo_owner: str | None = None,
        repo_name: str | None = None,
    ):
        if token is None:
            token = validate_env("GITHUB_PERSONAL_ACCESS_TOKEN")
        if repo_owner is None:
            repo_owner = validate_env("GITHUB_REPO_OWNER")
        if repo_name is None:
            repo_name = validate_env("GITHUB_REPO_NAME")

        self._PERSONAL_ACCESS_TOKEN: str = token
        self._REPO_OWNER: str = repo_owner
        self._REPO_NAME: str = repo_name

    @property
    def PERSONAL_ACCESS_TOKEN(self) -> str:
        return self._PERSONAL_ACCESS_TOKEN

    @property
    def REPO_OWNER(self) -> str:
        return self._REPO_OWNER

    @property
    def REPO_NAME(self) -> str:
        return self._REPO_NAME


class GithubLabel:
    def __init__(
        self,
        github_config: GithubConfig | None = None,
        label_dir: str = "labels",
    ) -> None:
        if github_config is None:
            github_config = GithubConfig()

        self._url: str = f"https://api.github.com/repos/{github_config.REPO_OWNER}/{github_config.REPO_NAME}/labels"
        self._headers: dict[str, str] = {
            "Authorization": f"Bearer {github_config.PERSONAL_ACCESS_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self._label_dir: str = label_dir
        self._github_labels: list[dict[str, str]] = self._fetch_github_labels()
        self._github_label_names: list[str] = [
            github_label["name"] for github_label in self.github_labels
        ]
        self._labels: list[dict[str, str]] = self._load_labels_from_config()
        self._labels_to_remove: list[str] = self._load_labels_to_remove_from_config()

    @property
    def label_dir(self) -> str:
        return self._label_dir

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

        files_in_label_dir: list[str] = os.listdir(self.label_dir)

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
            logging.error("No Yaml or JSON config file for labels.")
            sys.exit()

        for label_filename in label_filenames:
            logging.info(f"Loading labels from {label_filename}.")
            label_file: str = os.path.join(self.label_dir, label_filename)

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

        files_in_label_dir: list[str] = os.listdir(self.label_dir)

        label_to_remove_yaml: list[str] = list(
            filter(
                lambda f: (f.endswith(".yaml") or f.endswith("yml"))
                and f.startswith("_remove"),
                files_in_label_dir,
            )
        )
        label_to_remove_json: list[str] = list(
            filter(
                lambda f: f.endswith(".json") and f.startswith("_remove"),
                files_in_label_dir,
            )
        )

        label_to_remove_file: str = ""
        label_to_remove_ext: str = ""

        if label_to_remove_yaml:
            label_to_remove_file = os.path.join(self.label_dir, label_to_remove_yaml[0])
            label_to_remove_ext = "yaml"
        elif label_to_remove_json:
            label_to_remove_file = os.path.join(self.label_dir, label_to_remove_json[0])
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

        res: Response = requests.patch(url, headers=self.headers, json=label)

        if res.status_code != 200:
            logging.error(
                f"Status {res.status_code}. Failed to update label `{label['new_name']}`."
            )
        else:
            logging.info(f"Label `{label['new_name']}` updated successfully.")

    def remove_all_labels(self, override: bool = False) -> None:
        confirmation: bool = False

        if override is False:
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

    def create_labels(self, labels: list[dict[str, str]] | None = None) -> None:
        create_labels: list[dict[str, str]] = self.labels

        if labels:
            for _i, label in enumerate(labels, start=1):
                if not label.get("name"):
                    logging.error(
                        f"Error on argument label. Name not found on `Label #{_i}` with color `{label.get('color')}` and description `{label.get('description')}`."
                    )
                    sys.exit()

                create_labels.append(
                    {
                        "name": label["name"],
                        "color": label.get("color", "").replace("#", ""),
                        "description": label.get("description", ""),
                    }
                )

        for label in create_labels:
            if label["name"] not in self.labels_to_remove:
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

        logging.info("Label creation process completed.")


def main() -> None:
    github_label = GithubLabel()
    github_label.remove_labels(strict=True)
    github_label.create_labels()


if __name__ == "__main__":
    main()
