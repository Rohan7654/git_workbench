import pytest
from click.testing import CliRunner
from git_assist.main import cli

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "Git Assist" in result.output
    assert "1.0.0" in result.output

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Git Assist Help" in result.output
    assert "basics" in result.output

def test_cli_h_alias():
    runner = CliRunner()
    result = runner.invoke(cli, ["-h"])
    assert result.exit_code == 0
    assert "Git Assist Help" in result.output
    assert "basics" in result.output
