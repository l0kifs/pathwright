"""Shared fixtures for end-to-end tests."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from fastmcp import Client
from typer.testing import CliRunner

from pathwright.entry_points.cli import app
from pathwright.entry_points.mcp_server import mcp


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Create isolated filesystem workspace for each test."""
    root = tmp_path / "workspace"
    root.mkdir()
    return root


@pytest.fixture
def invoke_cli() -> Callable[[list[str]], Any]:
    """Invoke Typer CLI app and return Click result."""
    runner = CliRunner()

    def _invoke(args: list[str]) -> Any:
        return runner.invoke(app, args)

    return _invoke


@pytest.fixture
def mcp_call() -> Callable[[str, dict[str, Any]], Any]:
    """Call FastMCP tool using in-memory client transport."""

    def _call(tool_name: str, arguments: dict[str, Any]) -> Any:
        async def _run() -> Any:
            async with Client(mcp) as client:
                result = await client.call_tool(name=tool_name, arguments=arguments)
                if isinstance(result.structured_content, dict) and "result" in result.structured_content:
                    return result.structured_content["result"]
                return result.structured_content if result.structured_content is not None else result.data

        return asyncio.run(_run())

    return _call
