"""E2E tests for files-outline feature."""

from pathlib import Path

from tests.helpers import parse_cli_json


def test_files_outline_happy_path(invoke_cli, mcp_call, workspace: Path) -> None:
    markdown = workspace / "doc.md"
    python_file = workspace / "code.py"
    go_file = workspace / "code.go"

    markdown.write_text("# Title\n\n## Subtitle\n", encoding="utf-8")
    python_file.write_text(
        '"""Module docs"""\n\nclass A:\n    """Class docs"""\n\n\ndef f():\n    """Func docs"""\n    return 1\n',
        encoding="utf-8",
    )
    go_file.write_text(
        "// file comment\n\n// Add comment\nfunc Add(a int, b int) int {\n  return a+b\n}\n",
        encoding="utf-8",
    )

    cli_result = invoke_cli(
        [
            "files-outline",
            "--path",
            str(markdown),
            "--path",
            str(python_file),
            "--path",
            str(go_file),
        ]
    )
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)

    md_kinds = {item["kind"] for item in cli_payload[str(markdown)]}
    py_kinds = {item["kind"] for item in cli_payload[str(python_file)]}
    go_kinds = {item["kind"] for item in cli_payload[str(go_file)]}
    assert "heading" in md_kinds
    assert "class" in py_kinds and "function" in py_kinds
    assert "function" in go_kinds

    mcp_payload = mcp_call(
        "files_outline",
        {"paths": [str(markdown), str(python_file), str(go_file)]},
    )
    assert any(item["kind"] == "heading" for item in mcp_payload[str(markdown)])
    assert any(item["kind"] == "class" for item in mcp_payload[str(python_file)])
    assert any(item["kind"] == "function" for item in mcp_payload[str(go_file)])


def test_files_outline_edge_cases(invoke_cli, mcp_call, workspace: Path) -> None:
    unsupported = workspace / "file.txt"
    missing = workspace / "missing.md"
    unsupported.write_text("plain text", encoding="utf-8")

    cli_result = invoke_cli(["files-outline", "--path", str(unsupported), "--path", str(missing)])
    assert cli_result.exit_code == 0
    cli_payload = parse_cli_json(cli_result.stdout)
    assert cli_payload[str(unsupported)] == []
    assert cli_payload[str(missing)] == []

    mcp_payload = mcp_call("files_outline", {"paths": [str(unsupported), str(missing)]})
    assert mcp_payload[str(unsupported)] == []
    assert mcp_payload[str(missing)] == []
