"""E2E tests for search-dirs feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_search_dirs_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    alpha = workspace / "alpha"
    beta = workspace / "beta"
    alpha.mkdir()
    beta.mkdir()

    cli_result = invoke_cli(["search-dirs", "--base-path", str(workspace), "--name-pattern", "a*"])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert str(alpha) in cli_payload
    assert str(beta) not in cli_payload

    mcp_payload = mcp_call("search_directories", {"base_path": str(workspace), "name_pattern": "a*"})
    assert str(alpha) in mcp_payload
    assert str(beta) not in mcp_payload


def test_search_dirs_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    cli_result = invoke_cli(["search-dirs", "--base-path", str(workspace), "--name-pattern", "zzz*"])
    assert cli_result.exit_code == 0
    assert parse_cli_json(cli_result.stdout) == []

    mcp_payload = mcp_call("search_directories", {"base_path": str(workspace), "name_pattern": "zzz*"})
    assert mcp_payload == []
