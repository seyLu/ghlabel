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

from logging.config import fileConfig
import requests
import os
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass(frozen=True)
class GithubConfig:
    PERSONAL_ACCESS_TOKEN: str = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    USERNAME: str = os.getenv("GITHUB_USERNAME")
    REPO_OWNER: str = os.getenv("GITHUB_REPO_OWNER")
    REPO_NAME: str = os.getenv("GITHUB_REPO_NAME")


class GithubIssueLabel:
    def __init__(self):
        self._url: str = f"https//api.github.com/repos/{GithubConfig.REPO_OWNER}/{GithubConfig.REPO_NAME}/labels"
        self._headers: dict = {
            "Authorization": f"Bearer {GithubConfig.PERSONAL_ACCESS_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self._labels: dict = self._load_labels()

    def _load_labels() -> dict:
        pass

    def create_labels():
        pass


def main() -> None:
    pass


if __name__ == "__main__":
    load_dotenv()
    fileConfig("logging.ini")
    main()
