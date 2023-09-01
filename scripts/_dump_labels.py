#!/usr/bin/env python

"""
CLI helper script to create label config
in either json or yaml format
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
from dataclasses import dataclass
from logging.config import fileConfig

import yaml

fileConfig("logging.ini")


def initialize_dir(dir: str) -> None:
    logging.info(f"Initializing {dir} dir.")
    for filename in os.listdir(dir):
        file_path: str = os.path.join(dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


@dataclass(frozen=True)
class LABELS:
    REMOVE_DEFAULT: tuple[str, ...] = (
        "bug",
        "dependencies",
        "documentation",
        "enhancement",
        "github_actions",
        "question",
    )
    PRIORITY: tuple[dict[str, str], ...] = (
        {
            "name": "Priority: Critical",
            "color": "#7c0a02",
        },
        {
            "name": "Priority: High",
            "color": "#b22222",
        },
        {
            "name": "Priority: Medium",
            "color": "#e88a1a",
        },
        {
            "name": "Priority: Low",
            "color": "#f1bc31",
        },
    )
    TYPE: tuple[dict[str, str], ...] = (
        {
            "name": "Type: Bug",
            "color": "#d73a4a",
            "description": "Something isn't working.",
        },
        {
            "name": "Type: Documentation",
            "color": "#a2eeef",
            "description": "Improvements or additions to documentation.",
        },
        {
            "name": "Type: Feature Request",
            "color": "#e88a1a",
            "description": "Issue describes a feature or enhancement we'd like to implement.",
        },
        {
            "name": "Type: Question",
            "color": "#d876e3",
            "description": "This issue doesn't require code. A question needs an answer.",
        },
        {
            "name": "Type: Refactor/Clean-up",
            "color": "#a0855b",
            "description": "Issues related to reorganization/clean-up of data or code (e.g. for maintainability).",
        },
        {
            "name": "Type: Suggestion",
            "color": "#ac8daf",
        },
    )


def main() -> None:
    EXT: str = "yaml"
    LABELS_PATH: str = "labels"

    initialize_dir(LABELS_PATH)

    for field in LABELS.__dataclass_fields__:
        labels = getattr(LABELS, field)
        labels_file = os.path.join(LABELS_PATH, f"{field.lower()}_labels.{EXT}")

        with open(labels_file, "w+") as f:
            logging.info(f"Dumping to {labels_file}.")

            if EXT == "yaml":
                print(
                    yaml.dump(
                        data=list(labels),
                        default_flow_style=False,
                        sort_keys=False,
                    ),
                    file=f,
                )
            elif EXT == "json":
                json.dump(labels, f, indent=2)

    logging.info("Finished dumping of labels.")


if __name__ == "__main__":
    main()
