from typing import TypedDict

StatusCode = int


class GithubLabel(TypedDict):
    name: str
    description: str
    color: str
    default: bool


class GithubIssue(TypedDict):
    labels: list[GithubLabel]
