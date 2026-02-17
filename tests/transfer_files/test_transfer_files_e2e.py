"""E2E tests for transfer-files feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_transfer_files_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    cli_source = workspace / "cli.txt"
    mcp_source = workspace / "mcp.txt"
    cli_source.write_text("copy", encoding="utf-8")
    mcp_source.write_text("move", encoding="utf-8")
    cli_destination = workspace / "cli-out"
    mcp_destination = workspace / "mcp-out"

    cli_result = invoke_cli(
        [
            "transfer-files",
            "--path",
            str(cli_source),
            "--destination",
            str(cli_destination),
        ]
    )
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is True
    assert (cli_destination / "cli.txt").exists()
    assert cli_source.exists()

    mcp_payload = mcp_call(
        "copy_or_move_files",
        {"paths": [str(mcp_source)], "destination": str(mcp_destination), "move": True},
    )
    assert mcp_payload[0]["success"] is True
    assert (mcp_destination / "mcp.txt").exists()
    assert not mcp_source.exists()


def test_transfer_files_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    missing = workspace / "missing.txt"
    destination = workspace / "out"

    cli_result = invoke_cli(
        ["transfer-files", "--path", str(missing), "--destination", str(destination)]
    )
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is False

    mcp_payload = mcp_call(
        "copy_or_move_files",
        {"paths": [str(missing)], "destination": str(destination), "move": False},
    )
    assert mcp_payload[0]["success"] is False
