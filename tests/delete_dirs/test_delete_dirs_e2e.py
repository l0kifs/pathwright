"""E2E tests for delete-dirs feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_delete_dirs_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    cli_target = workspace / "cli-dir"
    mcp_target = workspace / "mcp-dir"
    (cli_target / "inner").mkdir(parents=True)
    (mcp_target / "inner").mkdir(parents=True)

    cli_result = invoke_cli(["delete-dirs", "--path", str(cli_target)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is True
    assert not cli_target.exists()

    mcp_payload = mcp_call("delete_directories", {"paths": [str(mcp_target)], "recursive": True})
    assert mcp_payload[0]["success"] is True
    assert not mcp_target.exists()


def test_delete_dirs_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    cli_target = workspace / "cli-non-empty"
    mcp_target = workspace / "mcp-non-empty"
    (cli_target / "inner").mkdir(parents=True)
    (mcp_target / "inner").mkdir(parents=True)

    cli_result = invoke_cli(["delete-dirs", "--path", str(cli_target), "--non-recursive"])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is False
    assert cli_target.exists()

    mcp_payload = mcp_call("delete_directories", {"paths": [str(mcp_target)], "recursive": False})
    assert mcp_payload[0]["success"] is False
    assert mcp_target.exists()
