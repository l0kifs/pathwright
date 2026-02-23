"""Schema regression tests for MCP tool argument schemas."""

from __future__ import annotations

import asyncio

from pathwright.entry_points.mcp_server import mcp


def test_read_files_line_intervals_schema_has_items() -> None:
    async def _get_line_intervals_schema() -> dict:
        tool = await mcp.get_tool("read_files")
        return tool.parameters["properties"]["line_intervals"]

    line_intervals_schema = asyncio.run(_get_line_intervals_schema())
    object_branch = next(
        option
        for option in line_intervals_schema["anyOf"]
        if option.get("type") == "object"
    )

    top_level_items = object_branch["additionalProperties"]["items"]
    assert top_level_items["type"] == "array"
    assert "items" in top_level_items

    inner_items = top_level_items["items"]
    assert inner_items["type"] == "integer"


def test_create_files_schema_has_items() -> None:
    async def _get_files_schema() -> dict:
        tool = await mcp.get_tool("create_files")
        return tool.parameters["properties"]["files"]

    files_schema = asyncio.run(_get_files_schema())
    outer_items = files_schema["items"]
    assert outer_items["type"] == "array"
    assert "items" in outer_items

    inner_items = outer_items["items"]
    assert inner_items["type"] == "string"


def test_update_files_schema_has_items() -> None:
    async def _get_files_schema() -> dict:
        tool = await mcp.get_tool("update_files")
        return tool.parameters["properties"]["files"]

    files_schema = asyncio.run(_get_files_schema())
    outer_items = files_schema["items"]
    assert outer_items["type"] == "array"
    assert "items" in outer_items

    inner_items = outer_items["items"]
    assert inner_items["type"] == "string"
