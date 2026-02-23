"""MCP server entry point for Pathwright filesystem tools."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Annotated, Any, Sequence

from fastmcp import FastMCP
from pydantic import Field

from pathwright.config.settings import get_settings
from pathwright.domains.filesystem.services import FilesystemService
from pathwright.infrastructure.storage.local_filesystem_gateway import (
    LocalFilesystemGateway,
)


def _to_serializable(value: Any) -> Any:
    if isinstance(value, list):
        return [_to_serializable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_serializable(item) for key, item in value.items()}
    if is_dataclass(value):
        return _to_serializable(asdict(value))
    return value


mcp = FastMCP(
    name="pathwright",
    instructions=(
        "Filesystem operations server. Always use absolute or workspace-relative paths, "
        "and avoid destructive actions unless explicitly requested."
    ),
    version=get_settings().app_version,
    on_duplicate="error",
    mask_error_details=False,
)


def build_service() -> FilesystemService:
    """Build service with current access-control settings."""
    settings = get_settings()
    return FilesystemService(
        gateway=LocalFilesystemGateway(
            whitelist_patterns=settings.path_whitelist,
            blacklist_patterns=settings.path_blacklist,
        )
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
def create_files(
    files: Annotated[
        list[tuple[str, str]],
        Field(description="Files to create as (path, content) tuples."),
    ],
    overwrite: Annotated[
        bool,
        Field(description="Whether to overwrite existing files (default: false)."),
    ] = False,
) -> list[dict[str, Any]]:
    """Create one or more files. Each tuple is (path, content)."""
    return _to_serializable(
        build_service().create_files(files=files, overwrite=overwrite)
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def read_files(
    paths: Annotated[
        list[str],
        Field(description="File paths to read."),
    ],
    line_intervals: Annotated[
        dict[str, Sequence[tuple[int, int]]] | None,
        Field(
            description="Optional map of path -> inclusive (start_line, end_line) intervals (default: null)."
        ),
    ] = None,
) -> list[dict[str, Any]]:
    """Read one or more files by path, optionally by line intervals."""
    return _to_serializable(
        build_service().read_files(paths=paths, line_intervals=line_intervals)
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": False,
    }
)
def update_files(
    files: Annotated[
        list[tuple[str, str]],
        Field(description="Files to update as (path, content) tuples."),
    ],
) -> list[dict[str, Any]]:
    """Update one or more files. Each tuple is (path, content)."""
    return _to_serializable(build_service().update_files(files=files))


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": False,
    }
)
def delete_files(
    paths: Annotated[
        list[str],
        Field(description="File paths to delete."),
    ],
) -> list[dict[str, Any]]:
    """Delete one or more files by path."""
    return _to_serializable(build_service().delete_files(paths=paths))


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def search_files(
    base_path: Annotated[
        str,
        Field(description="Base directory where file search starts."),
    ],
    name_pattern: Annotated[
        str | None,
        Field(description="Optional filename pattern to match (default: null)."),
    ] = None,
    extension: Annotated[
        str | None,
        Field(
            description="Optional file extension filter (e.g., .py, .md) (default: null)."
        ),
    ] = None,
    content_query: Annotated[
        str | None,
        Field(
            description="Optional text query to search inside file contents (default: null)."
        ),
    ] = None,
) -> list[str]:
    """Search files by name, extension, or content."""
    return build_service().search_files(
        base_path=base_path,
        name_pattern=name_pattern,
        extension=extension,
        content_query=content_query,
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": False,
    }
)
def copy_or_move_files(
    paths: Annotated[
        list[str],
        Field(description="Source file paths to copy or move."),
    ],
    destination: Annotated[
        str,
        Field(description="Destination directory path."),
    ],
    move: Annotated[
        bool,
        Field(
            description="If true, move files instead of copying them (default: false)."
        ),
    ] = False,
) -> list[dict[str, Any]]:
    """Copy or move files to destination."""
    return _to_serializable(
        build_service().copy_or_move_files(
            paths=paths, destination=destination, move=move
        )
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
def create_directories(
    paths: Annotated[
        list[str],
        Field(description="Directory paths to create."),
    ],
    exist_ok: Annotated[
        bool,
        Field(
            description="If true, do not fail when a directory already exists (default: true)."
        ),
    ] = True,
) -> list[dict[str, Any]]:
    """Create one or more directories."""
    return _to_serializable(
        build_service().create_directories(paths=paths, exist_ok=exist_ok)
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def read_directories(
    paths: Annotated[
        list[str],
        Field(description="Directory paths to list."),
    ],
) -> dict[str, list[dict[str, Any]]]:
    """List directory entries for one or more directories."""
    return _to_serializable(build_service().read_directories(paths=paths))


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": False,
    }
)
def update_directories(
    paths: Annotated[
        list[str],
        Field(description="Source directory paths to move or copy."),
    ],
    destination: Annotated[
        str,
        Field(description="Destination parent directory path."),
    ],
    move: Annotated[
        bool,
        Field(
            description="If true, move directories; otherwise copy them (default: true)."
        ),
    ] = True,
) -> list[dict[str, Any]]:
    """Move or copy directories to destination."""
    return _to_serializable(
        build_service().update_directories(
            sources=paths, destination=destination, move=move
        )
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": False,
    }
)
def delete_directories(
    paths: Annotated[
        list[str],
        Field(description="Directory paths to delete."),
    ],
    recursive: Annotated[
        bool,
        Field(description="If true, delete directories recursively (default: true)."),
    ] = True,
) -> list[dict[str, Any]]:
    """Delete one or more directories."""
    return _to_serializable(
        build_service().delete_directories(paths=paths, recursive=recursive)
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def search_directories(
    base_path: Annotated[
        str,
        Field(description="Base directory where directory search starts."),
    ],
    name_pattern: Annotated[
        str | None,
        Field(description="Optional directory name pattern to match (default: null)."),
    ] = None,
) -> list[str]:
    """Search directories by name pattern."""
    return build_service().search_directories(
        base_path=base_path, name_pattern=name_pattern
    )


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": False,
    }
)
def copy_or_move_directories(
    paths: Annotated[
        list[str],
        Field(description="Source directory paths to copy or move."),
    ],
    destination: Annotated[
        str,
        Field(description="Destination parent directory path."),
    ],
    move: Annotated[
        bool,
        Field(
            description="If true, move directories instead of copying them (default: false)."
        ),
    ] = False,
) -> list[dict[str, Any]]:
    """Copy or move directories to destination."""
    return _to_serializable(
        build_service().copy_or_move_directories(
            paths=paths, destination=destination, move=move
        )
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def filesystem_outline(
    base_path: Annotated[
        str,
        Field(description="Base directory to outline."),
    ],
    depth: Annotated[
        int,
        Field(description="Maximum traversal depth for the outline (default: 3)."),
    ] = 3,
) -> dict[str, Any]:
    """Build a hierarchical outline of the filesystem."""
    return _to_serializable(
        build_service().filesystem_outline(base_path=base_path, depth=depth)
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def files_outline(
    paths: Annotated[
        list[str],
        Field(
            description="File paths to outline (markdown, python, and go are supported)."
        ),
    ],
) -> dict[str, list[dict[str, Any]]]:
    """Build outlines for markdown, python, and go files."""
    return _to_serializable(build_service().files_outline(paths=paths))


def run() -> None:
    """Run MCP server."""
    mcp.run()
