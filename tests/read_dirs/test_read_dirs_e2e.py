"""E2E tests for read-dirs feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_read_dirs_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    directory = workspace / "data"
    directory.mkdir()
    (directory / "alpha.txt").write_text("x", encoding="utf-8")
    (directory / "beta").mkdir()

    cli_result = invoke_cli(["read-dirs", "--path", str(directory)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    cli_names = {entry["name"] for entry in cli_payload[str(directory)]}
    assert {"alpha.txt", "beta"}.issubset(cli_names)

    mcp_payload = mcp_call("read_directories", {"paths": [str(directory)]})
    mcp_names = {entry["name"] for entry in mcp_payload[str(directory)]}
    assert {"alpha.txt", "beta"}.issubset(mcp_names)


def test_read_dirs_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    not_a_directory = workspace / "single.txt"
    not_a_directory.write_text("x", encoding="utf-8")

    cli_result = invoke_cli(["read-dirs", "--path", str(not_a_directory)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[str(not_a_directory)] == []

    mcp_payload = mcp_call("read_directories", {"paths": [str(not_a_directory)]})
    assert mcp_payload[str(not_a_directory)] == []
