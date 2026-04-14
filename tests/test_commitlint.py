import pytest
from git_assist.commands.commitlint import validate_commit

def test_validate_commit_valid_feat():
    result = validate_commit("feat: add user login")
    assert result["valid"] is True
    assert result["type"] == "feat"
    assert result["description"] == "add user login"

def test_validate_commit_valid_fix_with_scope():
    result = validate_commit("fix(api): resolve null pointer")
    assert result["valid"] is True
    assert result["type"] == "fix"
    assert result["scope"] == "api"
    assert result["description"] == "resolve null pointer"

def test_validate_commit_breaking_change():
    result = validate_commit("feat!: drop support for python 2")
    assert result["valid"] is True
    assert result["type"] == "feat"
    assert result["breaking"] is True

def test_validate_commit_invalid_type():
    result = validate_commit("unknown: message")
    assert result["valid"] is False
    assert result["error"] == "Invalid format"

def test_validate_commit_missing_colon():
    result = validate_commit("feat message")
    assert result["valid"] is False
    assert result["error"] == "Missing type prefix"

def test_validate_commit_uppercase_type():
    result = validate_commit("Feat: message")
    assert result["valid"] is False
    assert result["error"] == "Type should be lowercase"

def test_validate_commit_strict_period():
    result = validate_commit("feat: message.", strict=True)
    assert result["valid"] is False
    assert result["error"] == "No period at end"

def test_validate_commit_strict_description_length():
    result = validate_commit("feat: abc", strict=True)
    assert result["valid"] is False
    assert result["error"] == "Description too short"
