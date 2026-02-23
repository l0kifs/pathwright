"""E2E tests for update-files feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_update_files_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    cli_file = workspace / "cli.txt"
    mcp_file = workspace / "mcp.txt"
    cli_file.write_text("before", encoding="utf-8")
    mcp_file.write_text("before", encoding="utf-8")

    cli_result = invoke_cli(["update-files", "--item", f"{cli_file}::after"])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is True
    assert cli_file.read_text(encoding="utf-8") == "after"

    mcp_payload = mcp_call("update_files", {"files": [[str(mcp_file), "after"]]})
    assert mcp_payload[0]["success"] is True
    assert mcp_file.read_text(encoding="utf-8") == "after"


def test_update_files_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    missing = workspace / "missing.txt"

    cli_result = invoke_cli(["update-files", "--item", f"{missing}::after"])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is False
    assert cli_payload[0]["message"] == "file does not exist"

    mcp_payload = mcp_call("update_files", {"files": [[str(missing), "after"]]})
    assert mcp_payload[0]["success"] is False
    assert mcp_payload[0]["message"] == "file does not exist"
