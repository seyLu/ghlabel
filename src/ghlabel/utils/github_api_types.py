from typing import NotRequired, TypedDict

StatusCode = int


class GithubParams(TypedDict):
    page: NotRequired[int]
    per_page: NotRequired[int]


class GithubLabel(TypedDict):
    name: str
    new_name: NotRequired[str]
    description: str
    color: str


class GithubIssue(TypedDict):
    html_url: str
    pull_request: NotRequired[dict[str, str]]
    labels: list[GithubLabel]


class GithubIssueParams(GithubParams):
    labels: NotRequired[str]
    state: NotRequired[str]


class GithubPullRequest(TypedDict):
    labels: list[GithubLabel]
