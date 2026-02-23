"""E2E tests for create-files feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_create_files_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    first = workspace / "a.txt"
    second = workspace / "b.txt"

    cli_result = invoke_cli(
        [
            "create-files",
            "--item",
            f"{first}::hello",
            "--item",
            f"{second}::world",
        ]
    )
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert all(item["success"] for item in cli_payload)

    mcp_payload = mcp_call(
        "create_files",
        {"files": [[str(workspace / "c.txt"), "mcp"]], "overwrite": False},
    )
    assert mcp_payload[0]["success"] is True
    assert (workspace / "c.txt").read_text(encoding="utf-8") == "mcp"


def test_create_files_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    existing = workspace / "exists.txt"
    existing.write_text("original", encoding="utf-8")

    malformed = invoke_cli(["create-files", "--item", str(existing)])
    assert malformed.exit_code != 0

    cli_result = invoke_cli(["create-files", "--item", f"{existing}::new"])
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is False

    mcp_payload = mcp_call(
        "create_files", {"files": [[str(existing), "new"]], "overwrite": False}
    )
    assert mcp_payload[0]["success"] is False
    assert existing.read_text(encoding="utf-8") == "original"
