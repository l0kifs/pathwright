"""E2E tests for update-dirs feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_update_dirs_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    cli_source = workspace / "cli-source"
    mcp_source = workspace / "mcp-source"
    cli_source.mkdir()
    mcp_source.mkdir()
    (cli_source / "x.txt").write_text("x", encoding="utf-8")
    (mcp_source / "x.txt").write_text("x", encoding="utf-8")
    destination = workspace / "dest"

    cli_result = invoke_cli(["update-dirs", "--path", str(cli_source), "--destination", str(destination)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is True
    assert not cli_source.exists()
    assert (destination / "cli-source" / "x.txt").exists()

    mcp_payload = mcp_call(
        "update_directories",
        {"paths": [str(mcp_source)], "destination": str(destination), "move": False},
    )
    assert mcp_payload[0]["success"] is True
    assert mcp_source.exists()
    assert (destination / "mcp-source" / "x.txt").exists()


def test_update_dirs_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    missing = workspace / "missing-dir"
    destination = workspace / "dest"

    cli_result = invoke_cli(["update-dirs", "--path", str(missing), "--destination", str(destination)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is False

    mcp_payload = mcp_call(
        "update_directories",
        {"paths": [str(missing)], "destination": str(destination), "move": True},
    )
    assert mcp_payload[0]["success"] is False
