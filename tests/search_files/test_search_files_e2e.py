"""E2E tests for search-files feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_search_files_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    target = workspace / "match.py"
    target.write_text("TOKEN = 'x'", encoding="utf-8")
    (workspace / "skip.txt").write_text("TOKEN = 'x'", encoding="utf-8")

    cli_result = invoke_cli(
        [
            "search-files",
            "--base-path",
            str(workspace),
            "--extension",
            "py",
            "--content-query",
            "TOKEN",
        ]
    )
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert str(target) in cli_payload

    mcp_payload = mcp_call(
        "search_files",
        {"base_path": str(workspace), "extension": "py", "content_query": "TOKEN"},
    )
    assert str(target) in mcp_payload


def test_search_files_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    missing_base = workspace / "nope"

    cli_result = invoke_cli(["search-files", "--base-path", str(missing_base), "--extension", "py"])
    assert cli_result.exit_code == 0
    assert parse_cli_json(cli_result.stdout) == []

    mcp_payload = mcp_call("search_files", {"base_path": str(missing_base), "extension": "py"})
    assert mcp_payload == []
