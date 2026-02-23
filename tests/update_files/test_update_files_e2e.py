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


def test_update_files_with_line_intervals_happy_path(
    invoke_cli, mcp_call, workspace: Path
) -> None:
    cli_file = workspace / "cli-interval.txt"
    mcp_file = workspace / "mcp-interval.txt"
    original_content = "A\nB\nC\nD\nE\n"
    cli_file.write_text(original_content, encoding="utf-8")
    mcp_file.write_text(original_content, encoding="utf-8")

    cli_result = invoke_cli(
        [
            "update-files",
            "--item",
            f"{cli_file}::X\n",
            "--interval",
            f"{cli_file}::2:3",
        ]
    )
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is True
    assert cli_file.read_text(encoding="utf-8") == "A\nX\nD\nE\n"

    mcp_payload = mcp_call(
        "update_files",
        {
            "files": [[str(mcp_file), "X\n"]],
            "line_intervals": {str(mcp_file): [[2, 3]]},
        },
    )
    assert mcp_payload[0]["success"] is True
    assert mcp_file.read_text(encoding="utf-8") == "A\nX\nD\nE\n"


def test_update_files_line_interval_edge_cases(
    invoke_cli, mcp_call, workspace: Path
) -> None:
    target = workspace / "update-edge.txt"
    target.write_text("1\n2\n3\n", encoding="utf-8")

    out_of_range_cli = invoke_cli(
        [
            "update-files",
            "--item",
            f"{target}::X\n",
            "--interval",
            f"{target}::10:20",
        ]
    )
    assert out_of_range_cli.exit_code == 0
    out_of_range_cli_payload = parse_cli_json(out_of_range_cli.stdout)
    assert out_of_range_cli_payload[0]["success"] is True
    assert target.read_text(encoding="utf-8") == "1\n2\n3\n"

    out_of_range_mcp = mcp_call(
        "update_files",
        {
            "files": [[str(target), "X\n"]],
            "line_intervals": {str(target): [[10, 20]]},
        },
    )
    assert out_of_range_mcp[0]["success"] is True
    assert target.read_text(encoding="utf-8") == "1\n2\n3\n"

    invalid_cli = invoke_cli(
        ["update-files", "--item", f"{target}::X\n", "--interval", f"{target}::0:1"]
    )
    assert invalid_cli.exit_code == 0
    invalid_cli_payload = parse_cli_json(invalid_cli.stdout)
    assert invalid_cli_payload[0]["success"] is False
    assert "line interval" in invalid_cli_payload[0]["message"]

    invalid_mcp = mcp_call(
        "update_files",
        {
            "files": [[str(target), "X\n"]],
            "line_intervals": {str(target): [[0, 1]]},
        },
    )
    assert invalid_mcp[0]["success"] is False
    assert "line interval" in invalid_mcp[0]["message"]
