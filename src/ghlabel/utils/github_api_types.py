from typing import TypedDict

StatusCode = int


class GithubLabel(TypedDict):
    id: int
    node_id: str
    url: str
    name: str
    description: str
    color: str
    default: bool


class GithubIssue(TypedDict):
    labels: list[GithubLabel]
