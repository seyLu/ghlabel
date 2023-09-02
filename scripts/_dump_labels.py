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
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from logging.config import fileConfig

import yaml

fileConfig("logging.ini")


@dataclass(frozen=True)
class LABELS:
    _REMOVE: tuple[str, ...] = (
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
            "color": "#ff8597",
        },
        {
            "name": "Priority: Low",
            "color": "#ffccc9",
        },
    )
    TYPE: tuple[dict[str, str], ...] = (
        {
            "name": "Type: Bug",
            "color": "#ff9900",
            "description": "Something isn't working.",
        },
        {
            "name": "Type: Documentation",
            "color": "#ff9900",
            "description": "Improvements or additions to documentation.",
        },
        {
            "name": "Type: Feature Request",
            "color": "#ff9900",
            "description": "Issue describes a feature or enhancement we'd like to implement.",
        },
        {
            "name": "Type: Question",
            "color": "#ff9900",
            "description": "This issue doesn't require code. A question needs an answer.",
        },
        {
            "name": "Type: Refactor/Clean-up",
            "color": "#ff9900",
            "description": "Issues related to reorganization/clean-up of data or code (e.g. for maintainability).",
        },
        {
            "name": "Type: Suggestion",
            "color": "#ff9900",
        },
    )
    STATE: tuple[dict[str, str], ...] = (
        {
            "name": "State: Blocked",
            "color": "#e07bf9",
            "description": "Work has stopped, waiting for something (Info, Dependent fix, etc. See comments).",
        },
        {
            "name": "State: In Review",
            "color": "#e07bf9",
            "description": "This issue is waiting for review to finish.",
        },
        {
            "name": "State: Work In Progress",
            "color": "#e07bf9",
            "description": "This issue is being actively worked on.",
        },
    )
    AFFECTS: tuple[dict[str, str], ...] = (
        {
            "name": "Affects: Game Assets",
            "color": "#fbbc9d",
            "description": "Issues relating directly to art and game assets.",
        },
        {
            "name": "Affects: Game Logic/Controls",
            "color": "#fbbc9d",
            "description": "Issues relating directly to game logic and controls.",
        },
        {
            "name": "Affects: Game Performance",
            "color": "#fbbc9d",
            "description": "Issues relating directly to squeezing game performance.",
        },
        {
            "name": "Affects: Game Rendering",
            "color": "#fbbc9d",
            "description": "Issues relating directly to game rendering.",
        },
        {
            "name": "Affects: Infra",
            "color": "#fbbc9d",
            "description": "Related to configuration, automation, CI, etc.",
        },
        {
            "name": "Affects: Player Experience",
            "color": "#fbbc9d",
            "description": "Issues relating directly to game design & player experience.",
        },
        {
            "name": "Affects: Project Management",
            "color": "#fbbc9d",
        },
    )


if __name__ == "__main__":
    LABELS_PATH: str = "labels"

    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--ext",
        "-e",
        choices=["json", "yaml"],
        help="Specify a file extension",
    )

    args: Namespace = parser.parse_args()

    EXT: str = args.ext or "yaml"

    logging.info(f"Initializing {LABELS_PATH} dir.")
    for filename in os.listdir(LABELS_PATH):
        file_path: str = os.path.join(LABELS_PATH, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # @TODO remove
    legacy_labels: tuple[dict[str, str], ...] = ()

    for field in LABELS.__dataclass_fields__:
        labels: tuple[dict[str, str], ...] | tuple[str, ...] = getattr(LABELS, field)
        labels_file: str = os.path.join(LABELS_PATH, f"{field.lower()}_labels.{EXT}")

        # @TODO remove
        if not (
            isinstance(labels, tuple)
            and all(isinstance(label, str) for label in labels)
        ):
            legacy_labels += labels  # type: ignore

        with open(labels_file, "w+") as f:
            logging.info(f"Dumping to {f.name}.")

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

    # backwards compatibility
    # @TODO remove
    legacy_labels_file: str = os.path.join(LABELS_PATH, f"labels.{EXT}")
    with open(legacy_labels_file, "w+") as f:
        logging.info(f"Dumping to {f.name}.")

        if EXT == "yaml":
            print(
                yaml.dump(
                    data=list(legacy_labels),
                    default_flow_style=False,
                    sort_keys=False,
                ),
                file=f,
            )
        elif EXT == "json":
            json.dump(legacy_labels, f, indent=2)

    logging.info("Finished dumping of labels.")
