"""E2E tests for read-files feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_read_files_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    target = workspace / "a.txt"
    target.write_text("line-1\nline-2\nline-3\nline-4\n", encoding="utf-8")

    cli_result = invoke_cli(["read-files", "--path", str(target)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["content"] == "line-1\nline-2\nline-3\nline-4\n"

    mcp_payload = mcp_call("read_files", {"paths": [str(target)]})
    assert mcp_payload[0]["success"] is True
    assert mcp_payload[0]["content"] == "line-1\nline-2\nline-3\nline-4\n"


def test_read_files_with_line_intervals_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    target = workspace / "interval.txt"
    target.write_text("A\nB\nC\nD\nE\n", encoding="utf-8")

    cli_result = invoke_cli(
        [
            "read-files",
            "--path",
            str(target),
            "--interval",
            f"{target}::2:3",
            "--interval",
            f"{target}::5:5",
        ]
    )
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["content"] == "B\nC\nE\n"

    mcp_payload = mcp_call(
        "read_files",
        {"paths": [str(target)], "line_intervals": {str(target): [(2, 3), (5, 5)]}},
    )
    assert mcp_payload[0]["success"] is True
    assert mcp_payload[0]["content"] == "B\nC\nE\n"


def test_read_files_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    missing = workspace / "missing.txt"

    cli_result = invoke_cli(["read-files", "--path", str(missing)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[0]["success"] is False
    assert cli_payload[0]["message"]

    mcp_payload = mcp_call("read_files", {"paths": [str(missing)]})
    assert mcp_payload[0]["success"] is False
    assert mcp_payload[0]["message"]


def test_read_files_line_interval_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    target = workspace / "edge.txt"
    target.write_text("1\n2\n3\n", encoding="utf-8")

    out_of_range_cli = invoke_cli(
        [
            "read-files",
            "--path",
            str(target),
            "--interval",
            f"{target}::10:20",
        ]
    )
    assert out_of_range_cli.exit_code == 0
    out_of_range_cli_payload = parse_cli_json(out_of_range_cli.stdout)
    assert out_of_range_cli_payload[0]["success"] is True
    assert out_of_range_cli_payload[0]["content"] == ""

    out_of_range_mcp = mcp_call(
        "read_files",
        {"paths": [str(target)], "line_intervals": {str(target): [(10, 20)]}},
    )
    assert out_of_range_mcp[0]["success"] is True
    assert out_of_range_mcp[0]["content"] == ""

    invalid_cli = invoke_cli(["read-files", "--path", str(target), "--interval", f"{target}::0:1"])
    assert invalid_cli.exit_code == 0
    invalid_cli_payload = parse_cli_json(invalid_cli.stdout)
    assert invalid_cli_payload[0]["success"] is False
    assert "line interval" in invalid_cli_payload[0]["message"]

    invalid_mcp = mcp_call(
        "read_files",
        {"paths": [str(target)], "line_intervals": {str(target): [(0, 1)]}},
    )
    assert invalid_mcp[0]["success"] is False
    assert "line interval" in invalid_mcp[0]["message"]
