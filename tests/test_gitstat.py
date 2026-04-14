import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from git_assist.utils.git_helpers import GitHelper, CommitInfo

@patch("git_assist.utils.git_helpers.GitHelper.run_command")
def test_is_git_repo_true(mock_run):
    mock_run.return_value = (True, ".git")
    assert GitHelper.is_git_repo() is True

@patch("git_assist.utils.git_helpers.GitHelper.run_command")
def test_is_git_repo_false(mock_run):
    mock_run.return_value = (False, "fatal: not a git repository")
    assert GitHelper.is_git_repo() is False

@patch("git_assist.utils.git_helpers.GitHelper.run_command")
def test_get_current_branch(mock_run):
    mock_run.return_value = (True, "main")
    assert GitHelper.get_current_branch() == "main"

@patch("git_assist.utils.git_helpers.GitHelper.get_commits")
@patch("git_assist.utils.git_helpers.GitHelper.get_contributors")
@patch("git_assist.utils.git_helpers.GitHelper.get_all_branches")
@patch("git_assist.utils.git_helpers.GitHelper.run_command")
def test_get_repo_stats(mock_run, mock_branches, mock_contributors, mock_commits):
    # Mock return values
    mock_run.side_effect = [
        (True, "100"), # rev-list --count HEAD
        (True, "file1.txt\nfile2.txt"), # ls-files
        (True, "2023-01-01T00:00:00") # first commit date
    ]
    mock_branches.return_value = [MagicMock(name="main"), MagicMock(name="dev")]
    mock_contributors.return_value = {"Author1": {"commits": 50}, "Author2": {"commits": 50}}
    mock_commits.return_value = [CommitInfo("hash", "short", "Author1", "email", datetime.fromisoformat("2023-01-02T00:00:00"), "msg")]
    
    stats = GitHelper.get_repo_stats()
    
    assert stats["total_commits"] == 100
    assert stats["total_contributors"] == 2
    assert stats["total_files"] == 2
    assert stats["total_branches"] == 2
    assert stats["last_commit_date"].year == 2023
    assert stats["first_commit_date"].year == 2023
