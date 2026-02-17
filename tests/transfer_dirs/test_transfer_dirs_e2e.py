"""E2E tests for transfer-dirs feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_transfer_dirs_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    cli_source = workspace / "cli-source"
    mcp_source = workspace / "mcp-source"
    (cli_source / "inner").mkdir(parents=True)
    (mcp_source / "inner").mkdir(parents=True)
    destination = workspace / "dest"

    cli_result = invoke_cli(["transfer-dirs", "--path", str(cli_source), "--destination", str(destination)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is True
    assert (destination / "cli-source" / "inner").exists()
    assert cli_source.exists()

    mcp_payload = mcp_call(
        "copy_or_move_directories",
        {"paths": [str(mcp_source)], "destination": str(destination), "move": True},
    )
    assert mcp_payload[0]["success"] is True
    assert (destination / "mcp-source" / "inner").exists()
    assert not mcp_source.exists()


def test_transfer_dirs_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    missing = workspace / "missing-dir"
    destination = workspace / "dest"

    cli_result = invoke_cli(["transfer-dirs", "--path", str(missing), "--destination", str(destination)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is False

    mcp_payload = mcp_call(
        "copy_or_move_directories",
        {"paths": [str(missing)], "destination": str(destination), "move": False},
    )
    assert mcp_payload[0]["success"] is False
