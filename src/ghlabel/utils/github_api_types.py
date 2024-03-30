from typing import NotRequired, TypedDict

StatusCode = int


class GithubLabel(TypedDict):
    name: str
    new_name: NotRequired[str]
    description: str
    color: str


class GithubIssue(TypedDict):
    labels: list[GithubLabel]
