import logging
import os
import sys
from logging.config import fileConfig
from pathlib import Path

import requests
from requests.exceptions import HTTPError, Timeout
from requests.models import Response

from ghlabel.utils.github_api_types import (
    GithubIssue,
    GithubIssueParams,
    GithubLabel,
    GithubPullRequest,
    StatusCode,
)
from ghlabel.utils.helpers import STATUS_OK, validate_env

Path("logs").mkdir(exist_ok=True)
fileConfig(os.path.join(os.path.dirname(__file__), "../logging.ini"))


class GithubApi:
    VERSION: str = "2022-11-28"

    def __init__(self, token: str, repo_owner: str, repo_name: str) -> None:
        self._token = token
        self._repo_owner = repo_owner
        self._repo_name = repo_name
        self._base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": GithubApi.VERSION,
        }

    @property
    def token(self) -> str:
        return self._token

    @property
    def repo_owner(self) -> str:
        return self._repo_owner

    @property
    def repo_name(self) -> str:
        return self._repo_name

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    def list_labels(self) -> tuple[list[GithubLabel], StatusCode]:
        url: str = f"{self.base_url}/labels"

        page: int = 1
        per_page: int = 100
        res: Response

        logging.info(
            f"Fetching list of github labels from `{self.repo_owner}/{self.repo_name}`."
        )
        github_labels: list[GithubLabel] = []
        while True:
            params: dict[str, int] = {"page": page, "per_page": per_page}
            logging.info(f"Fetching page {page}.")
            try:
                res = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10,
                )
                res.raise_for_status()
            except Timeout:
                logging.error(
                    "The site can't be reached, `github.com` took to long to respond. Try checking the connection."
                )
                break
            except HTTPError:
                logging.error(
                    f"Failed to fetch list of github labels. Check if token has permission to access `{self.repo_owner}/{self.repo_name}`."
                )
                break

            if not res.json():
                break

            github_labels.extend(res.json())
            page += 1

        return github_labels, res.status_code

    def create_label(self, label: GithubLabel) -> tuple[GithubLabel, StatusCode]:
        url: str = f"{self.base_url}/labels"
        res: Response

        try:
            res = requests.post(
                url,
                headers=self.headers,
                json=label,
                timeout=10,
            )
            res.raise_for_status()
        except Timeout:
            logging.error(
                "The site can't be reached, `github.com` took to long to respond. Try checking the connection."
            )
            sys.exit()
        except HTTPError:
            logging.error(
                f"Failed to add label `{label['name']}`. Check the label format."
            )
        else:
            logging.info(f"Label `{label['name']}` added successfully.")

        return res.json(), res.status_code

    def update_label(self, label: GithubLabel) -> tuple[GithubLabel, StatusCode]:
        url: str = f"{self.base_url}/{label['name']}"
        label["new_name"] = label.pop("name")  # type: ignore[misc]
        res: Response

        try:
            res = requests.patch(
                url,
                headers=self.headers,
                json=label,
                timeout=10,
            )
            res.raise_for_status()
        except Timeout:
            logging.error(
                "The site can't be reached, `github.com` took to long to respond. Try checking the connection."
            )
            sys.exit()
        except HTTPError:
            logging.error(
                f"Failed to update label `{label['new_name']}`. Check the label format."
            )
        else:
            logging.info(f"Label `{label['new_name']}` updated successfully.")

        return res.json(), res.status_code

    def delete_label(self, label_name: str) -> tuple[None, StatusCode]:
        url: str = f"{self.base_url}/labels/{label_name}"
        res: Response

        try:
            res = requests.delete(
                url,
                headers=self.headers,
                timeout=10,
            )
            res.raise_for_status()
        except Timeout:
            logging.error(
                "The site can't be reached, `github.com` took to long to respond. Try checking the connection."
            )
            sys.exit()
        except HTTPError:
            logging.error(f"Failed to delete label `{label_name}`.")
        else:
            logging.info(f"Label `{label_name}` deleted successfully.")

        return None, res.status_code

    def list_issues(
        self, label_names: set[str] | None = None, state: str = "all"
    ) -> tuple[list[GithubIssue], StatusCode]:
        """
        Issue queried include PRs. PR has "pull_request" key.
        """

        url: str = f"{self.base_url}/issues"
        res: Response
        params: GithubIssueParams = {}

        if label_names:
            params["labels"] = ",".join(label_name for label_name in label_names)

        if state:
            params["state"] = state

        page: int = 1
        per_page: int = 100

        logging.info(
            f"Fetching list of github issues from `{self.repo_owner}/{self.repo_name}`."
        )
        github_issues: list[GithubIssue] = []
        while True:
            params["page"] = page
            params["per_page"] = per_page
            logging.info(f"Fetching page {page}.")
            try:
                res = requests.get(
                    url,
                    headers=self.headers,
                    params=params,  # type: ignore[arg-type]
                    timeout=10,
                )
                res.raise_for_status()
            except Timeout:
                logging.error(
                    "The site can't be reached, `github.com` took to long to respond. Try checking the connection."
                )
                sys.exit()
            except HTTPError:
                logging.error(
                    f"Failed to fetch list of github issues. Check if token has permission to access `{self.repo_owner}/{self.repo_name}`."
                )
                sys.exit()

            if not res.json():
                break

            github_issues.extend(res.json())
            page += 1

        return github_issues, res.status_code


if __name__ == "__main__":
    gh_api = GithubApi(
        validate_env("GITHUB_TOKEN"),
        validate_env("GITHUB_REPO_OWNER"),
        validate_env("GITHUB_REPO_NAME"),
    )
    gh_issues, status_code = gh_api.list_issues()
    if status_code != STATUS_OK:
        sys.exit()
    gh_pull_requests: list[GithubPullRequest] = []
    for issue in gh_issues:
        if "pull_request" in issue:
            gh_pull_requests.append(issue)
    print(gh_pull_requests)
