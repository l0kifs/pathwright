"""MCP server entry point for Pathwright filesystem tools."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from fastmcp import FastMCP

from pathwright.domains.filesystem.services import FilesystemService
from pathwright.infrastructure.storage.local_filesystem_gateway import LocalFilesystemGateway


def _to_serializable(value: Any) -> Any:
    if isinstance(value, list):
        return [_to_serializable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_serializable(item) for key, item in value.items()}
    if is_dataclass(value):
        return _to_serializable(asdict(value))
    return value


service = FilesystemService(gateway=LocalFilesystemGateway())
mcp = FastMCP("pathwright")


@mcp.tool
def create_files(files: list[tuple[str, str]], overwrite: bool = False) -> list[dict[str, Any]]:
    """Create one or more files. Each tuple is (path, content)."""
    return _to_serializable(service.create_files(files=files, overwrite=overwrite))


@mcp.tool
def read_files(
    paths: list[str],
    line_intervals: dict[str, list[tuple[int, int]]] | None = None,
) -> list[dict[str, Any]]:
    """Read one or more files by path, optionally by line intervals."""
    return _to_serializable(service.read_files(paths=paths, line_intervals=line_intervals))


@mcp.tool
def update_files(files: list[tuple[str, str]]) -> list[dict[str, Any]]:
    """Update one or more files. Each tuple is (path, content)."""
    return _to_serializable(service.update_files(files=files))


@mcp.tool
def delete_files(paths: list[str]) -> list[dict[str, Any]]:
    """Delete one or more files by path."""
    return _to_serializable(service.delete_files(paths=paths))


@mcp.tool
def search_files(
    base_path: str,
    name_pattern: str | None = None,
    extension: str | None = None,
    content_query: str | None = None,
) -> list[str]:
    """Search files by name, extension, or content."""
    return service.search_files(
        base_path=base_path,
        name_pattern=name_pattern,
        extension=extension,
        content_query=content_query,
    )


@mcp.tool
def copy_or_move_files(paths: list[str], destination: str, move: bool = False) -> list[dict[str, Any]]:
    """Copy or move files to destination."""
    return _to_serializable(service.copy_or_move_files(paths=paths, destination=destination, move=move))


@mcp.tool
def create_directories(paths: list[str], exist_ok: bool = True) -> list[dict[str, Any]]:
    """Create one or more directories."""
    return _to_serializable(service.create_directories(paths=paths, exist_ok=exist_ok))


@mcp.tool
def read_directories(paths: list[str]) -> dict[str, list[dict[str, Any]]]:
    """List directory entries for one or more directories."""
    return _to_serializable(service.read_directories(paths=paths))


@mcp.tool
def update_directories(paths: list[str], destination: str, move: bool = True) -> list[dict[str, Any]]:
    """Move or copy directories to destination."""
    return _to_serializable(service.update_directories(sources=paths, destination=destination, move=move))


@mcp.tool
def delete_directories(paths: list[str], recursive: bool = True) -> list[dict[str, Any]]:
    """Delete one or more directories."""
    return _to_serializable(service.delete_directories(paths=paths, recursive=recursive))


@mcp.tool
def search_directories(base_path: str, name_pattern: str | None = None) -> list[str]:
    """Search directories by name pattern."""
    return service.search_directories(base_path=base_path, name_pattern=name_pattern)


@mcp.tool
def copy_or_move_directories(paths: list[str], destination: str, move: bool = False) -> list[dict[str, Any]]:
    """Copy or move directories to destination."""
    return _to_serializable(service.copy_or_move_directories(paths=paths, destination=destination, move=move))


@mcp.tool
def filesystem_outline(base_path: str, depth: int = 3) -> dict[str, Any]:
    """Build a hierarchical outline of the filesystem."""
    return _to_serializable(service.filesystem_outline(base_path=base_path, depth=depth))


@mcp.tool
def files_outline(paths: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Build outlines for markdown, python, and go files."""
    return _to_serializable(service.files_outline(paths=paths))


def run() -> None:
    """Run MCP server."""
    mcp.run()
