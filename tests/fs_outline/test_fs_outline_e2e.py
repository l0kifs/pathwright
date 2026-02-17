"""E2E tests for fs-outline feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_fs_outline_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    nested = workspace / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "f.txt").write_text("x", encoding="utf-8")

    cli_result = invoke_cli(["fs-outline", "--base-path", str(workspace), "--depth", "2"])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload["node_type"] == "directory"
    assert cli_payload["children"]

    mcp_payload = mcp_call("filesystem_outline", {"base_path": str(workspace), "depth": 2})
    assert mcp_payload["node_type"] == "directory"
    assert mcp_payload["children"]


def test_fs_outline_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    (workspace / "a").mkdir()

    cli_result = invoke_cli(["fs-outline", "--base-path", str(workspace), "--depth", "-1"])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload["children"] == []

    mcp_payload = mcp_call("filesystem_outline", {"base_path": str(workspace), "depth": -1})
    assert mcp_payload["children"] == []
