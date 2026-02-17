"""E2E tests for create-dirs feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_create_dirs_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    cli_dir = workspace / "cli" / "nested"
    mcp_dir = workspace / "mcp" / "nested"

    cli_result = invoke_cli(["create-dirs", "--path", str(cli_dir)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is True
    assert cli_dir.exists()

    mcp_payload = mcp_call("create_directories", {"paths": [str(mcp_dir)], "exist_ok": True})
    assert mcp_payload[0]["success"] is True
    assert mcp_dir.exists()


def test_create_dirs_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    target = workspace / "already"
    target.mkdir()

    cli_result = invoke_cli(["create-dirs", "--path", str(target)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is False

    mcp_payload = mcp_call("create_directories", {"paths": [str(target)], "exist_ok": False})
    assert mcp_payload[0]["success"] is False
