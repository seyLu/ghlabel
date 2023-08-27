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

import os
from logging.config import fileConfig

import yaml

CONFIG_PATH: str = "config"
LABELS_FILE: str = os.path.join(CONFIG_PATH, "labels")
LABELS_EXT: str = "yaml"
LABELS: list[dict[str, str]] = [
    # ----- Priority -----#
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
    # --------------------#
    # ------- Type -------#
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
    }
    # --------------------#
]


def main() -> None:
    labels_file: str = f"{LABELS_FILE}.{LABELS_EXT}"
    os.makedirs(os.path.dirname(labels_file), exist_ok=True)

    with open(labels_file, "w+") as f:
        print(
            yaml.dump(
                data=LABELS,
                default_flow_style=False,
                sort_keys=False,
            ),
            file=f,
        )


if __name__ == "__main__":
    fileConfig("logging.ini")
    main()
