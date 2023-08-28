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

import logging
import os
import sys
from dataclasses import dataclass
from logging.config import fileConfig

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
    CONFIG: str = "config"


@dataclass(frozen=True)
class LabelFile:
    _BASE_FILE: str = os.path.join(BasePath.CWD, "..", BasePath.CONFIG, "labels")
    YAML: str = f"{_BASE_FILE}.yaml"
    JSON: str = f"{_BASE_FILE}.json"


@dataclass(frozen=True)
class GithubConfig:
    PERSONAL_ACCESS_TOKEN: str = validate_env("GITHUB_PERSONAL_ACCESS_TOKEN")
    USERNAME: str = validate_env("GITHUB_USERNAME")
    REPO_OWNER: str = validate_env("GITHUB_REPO_OWNER")
    REPO_NAME: str = validate_env("GITHUB_REPO_NAME")


class GithubIssueLabel:
    def __init__(self) -> None:
        self._url: str = f"https://api.github.com/repos/{GithubConfig.REPO_OWNER}/{GithubConfig.REPO_NAME}/labels"
        self._headers: dict[str, str] = {
            "Authorization": f"Bearer {GithubConfig.PERSONAL_ACCESS_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self._github_labels: list[dict[str, str]] = self._fetch_github_labels()
        self._github_label_names: list[str] = [
            github_label["name"] for github_label in self.github_labels
        ]
        self._labels: list[dict[str, str]] = self._load_labels()

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
        res: Response = requests.get(
            self.url,
            headers=self.headers,
        )

        return [
            {
                "name": github_label["name"],
                "color": github_label["color"],
                "description": github_label["description"],
            }
            for github_label in res.json()
        ]

    def _load_labels(self) -> list[dict[str, str]]:
        labels: list[dict[str, str]]
        label_file: str = ""

        if os.path.isfile(LabelFile.YAML):
            logging.info(
                f"Found {LabelFile.YAML.split('../')[1]}. Loading labels from yaml config."
            )
            label_file = LabelFile.YAML
        elif os.path.isfile(LabelFile.JSON):
            logging.info(
                f"Found {LabelFile.JSON.split('../')[1]}. Loading labels from json config."
            )
            label_file = LabelFile.JSON
        else:
            logging.error("No Yaml or JSON config file for labels.")
            sys.exit()

        with open(label_file, "r") as f:
            if label_file == LabelFile.YAML:
                labels = yaml.safe_load(f)

        return labels

    def delete_default_labels(self) -> None:
        DEFAULT_LABEL_NAMES: list[str] = [
            "bug",
            "dependencies",
            "documentation",
            "enhancement",
            "github_actions",
            "question",
        ]

        for default_label_name in DEFAULT_LABEL_NAMES:
            if default_label_name in self.github_label_names:
                url: str = f"{self.url}/{default_label_name}"

                res: Response = requests.delete(
                    url,
                    headers=self.headers,
                )

                if res.status_code == 204:
                    logging.info(f"Label `{default_label_name}` deleted successfully.")
                else:
                    logging.error(
                        f"Status {res.status_code}. Failed to delete label `{default_label_name}`."
                    )

    def create_labels(self) -> None:
        for label in self.labels:
            if label["name"] not in self.github_label_names:
                label["color"] = label["color"].replace("#", "")

                res: Response = requests.post(
                    self.url,
                    headers=self.headers,
                    json=label,
                )

                if res.status_code == 201:
                    logging.info(f"Label `{label['name']}` created successfully.")
                else:
                    logging.error(
                        f"Status {res.status_code}. Failed to create label `{label['name']}`."
                    )
            else:
                pass


def main() -> None:
    github_issue_label = GithubIssueLabel()
    github_issue_label.delete_default_labels()
    github_issue_label.create_labels()
    logging.info("Label creation process completed.")


if __name__ == "__main__":
    main()
