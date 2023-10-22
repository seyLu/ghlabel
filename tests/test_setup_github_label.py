from typing import Any
from unittest.mock import Mock

import pytest

from scripts.setup_github_label import GithubLabel


@pytest.fixture
def mock_github_config(mocker: Any) -> Any:
    github_config = Mock()
    github_config.REPO_OWNER = "owner"
    github_config.REPO_NAME = "repo"
    github_config.PERSONAL_ACCESS_TOKEN = "token"
    return github_config


@pytest.fixture
def mock_requests(mocker: Any) -> Any:
    mock_requests = Mock()
    mock_requests.Response.status_code = 200
    return mock_requests


def test_init(mock_github_config: Any, mocker: Any) -> None:
    mocker.patch("requests.get", return_value=MockResponse)

    github_label = GithubLabel(github_config=mock_github_config)
    assert github_label.url == "https://api.github.com/repos/owner/repo/labels"
    assert github_label.headers["Authorization"] == "token"


class MockResponse:
    def json(self) -> list[dict[str, str]]:
        return [
            {"name": "label1", "color": "#FF0000", "description": "Description 1."},
        ]

    @property
    def status_code(self) -> int:
        return 200
