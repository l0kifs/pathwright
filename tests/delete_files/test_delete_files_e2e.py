"""E2E tests for delete-files feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_delete_files_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    cli_file = workspace / "cli.txt"
    mcp_file = workspace / "mcp.txt"
    cli_file.write_text("x", encoding="utf-8")
    mcp_file.write_text("x", encoding="utf-8")

    cli_result = invoke_cli(["delete-files", "--path", str(cli_file)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is True
    assert not cli_file.exists()

    mcp_payload = mcp_call("delete_files", {"paths": [str(mcp_file)]})
    assert mcp_payload[0]["success"] is True
    assert not mcp_file.exists()


def test_delete_files_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    missing = workspace / "missing.txt"

    cli_result = invoke_cli(["delete-files", "--path", str(missing)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is False

    mcp_payload = mcp_call("delete_files", {"paths": [str(missing)]})
    assert mcp_payload[0]["success"] is False
