"""E2E tests for whitelist/blacklist path access control."""

import json
from pathlib import Path

import pytest

from tests.helpers import parse_cli_json


def test_access_control_whitelist_blacklist_precedence_cli(invoke_cli, workspace: Path, monkeypatch) -> None:
    allowed_public = workspace / "allowed" / "public"
    denied_private = workspace / "allowed" / "private"
    allowed_public.mkdir(parents=True)
    denied_private.mkdir(parents=True)

    public_file = allowed_public / "ok.txt"
    private_file = denied_private / "secret.txt"
    public_file.write_text("ok", encoding="utf-8")
    private_file.write_text("secret", encoding="utf-8")

    monkeypatch.setenv(
        "PATHWRIGHT__PATH_WHITELIST",
        json.dumps([f"{workspace}/allowed/**"]),
    )
    monkeypatch.setenv(
        "PATHWRIGHT__PATH_BLACKLIST",
        json.dumps([f"{workspace}/allowed/private/**"]),
    )

    allowed_result = invoke_cli(["read-files", "--path", str(public_file)])
    allowed_payload = parse_cli_json(allowed_result.stdout)
    assert allowed_result.exit_code == 0
    assert allowed_payload[0]["success"] is True
    assert allowed_payload[0]["content"] == "ok"

    denied_result = invoke_cli(["read-files", "--path", str(private_file)])
    denied_payload = parse_cli_json(denied_result.stdout)
    assert denied_result.exit_code == 0
    assert denied_payload[0]["success"] is False
    assert "blacklist pattern" in denied_payload[0]["message"]


def test_access_control_search_denial_message_cli(invoke_cli, workspace: Path, monkeypatch) -> None:
    allowed_base = workspace / "allowed"
    denied_base = workspace / "denied"
    allowed_base.mkdir()
    denied_base.mkdir()

    monkeypatch.setenv("PATHWRIGHT__PATH_WHITELIST", json.dumps([str(allowed_base)]))
    monkeypatch.setenv("PATHWRIGHT__PATH_BLACKLIST", json.dumps([]))

    result = invoke_cli(["search-files", "--base-path", str(denied_base)])
    stderr = getattr(result, "stderr", "")
    details = f"{result.stdout}\n{stderr}\n{result.exception}"
    assert result.exit_code != 0
    assert "Access denied" in details
    assert "whitelist" in details


def test_access_control_whitelist_blacklist_precedence_mcp(mcp_call, workspace: Path, monkeypatch) -> None:
    allowed_public = workspace / "allowed" / "public"
    denied_private = workspace / "allowed" / "private"
    allowed_public.mkdir(parents=True)
    denied_private.mkdir(parents=True)

    public_file = allowed_public / "ok.txt"
    private_file = denied_private / "secret.txt"
    public_file.write_text("ok", encoding="utf-8")
    private_file.write_text("secret", encoding="utf-8")

    monkeypatch.setenv(
        "PATHWRIGHT__PATH_WHITELIST",
        json.dumps([f"{workspace}/allowed/**"]),
    )
    monkeypatch.setenv(
        "PATHWRIGHT__PATH_BLACKLIST",
        json.dumps([f"{workspace}/allowed/private/**"]),
    )

    allowed_payload = mcp_call("read_files", {"paths": [str(public_file)]})
    assert allowed_payload[0]["success"] is True

    denied_payload = mcp_call("read_files", {"paths": [str(private_file)]})
    assert denied_payload[0]["success"] is False
    assert "blacklist pattern" in denied_payload[0]["message"]


def test_access_control_denied_tool_error_mcp(mcp_call, workspace: Path, monkeypatch) -> None:
    allowed_base = workspace / "allowed"
    denied_base = workspace / "denied"
    allowed_base.mkdir()
    denied_base.mkdir()

    monkeypatch.setenv("PATHWRIGHT__PATH_WHITELIST", json.dumps([str(allowed_base)]))
    monkeypatch.setenv("PATHWRIGHT__PATH_BLACKLIST", json.dumps([]))

    with pytest.raises(Exception, match="Access denied"):
        mcp_call("search_files", {"base_path": str(denied_base)})
