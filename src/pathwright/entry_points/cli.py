"""CLI entry point for Pathwright."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, is_dataclass
from typing import Any

import typer
from rich.console import Console

from pathwright.domains.filesystem.services import FilesystemService
from pathwright.infrastructure.storage.local_filesystem_gateway import LocalFilesystemGateway

app = typer.Typer(help="Filesystem operations CLI")
console = Console()


def build_service() -> FilesystemService:
    """Create service graph for CLI usage."""
    return FilesystemService(gateway=LocalFilesystemGateway())


def _parse_file_items(items: Iterable[str]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for item in items:
        if "::" not in item:
            raise typer.BadParameter("item must be in format 'path::content'")
        path, content = item.split("::", maxsplit=1)
        pairs.append((path, content))
    return pairs


def _parse_line_intervals(items: Iterable[str]) -> dict[str, list[tuple[int, int]]]:
    intervals_by_path: dict[str, list[tuple[int, int]]] = {}
    for item in items:
        try:
            path, range_spec = item.rsplit("::", maxsplit=1)
            start_raw, end_raw = range_spec.split(":", maxsplit=1)
            start = int(start_raw)
            end = int(end_raw)
        except ValueError as error:
            raise typer.BadParameter("interval must be in format 'path::start:end'") from error

        intervals_by_path.setdefault(path, []).append((start, end))
    return intervals_by_path


def _to_serializable(value: Any) -> Any:
    if isinstance(value, list):
        return [_to_serializable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_serializable(item) for key, item in value.items()}
    if is_dataclass(value):
        return _to_serializable(asdict(value))
    return value


def _print_json(value: Any) -> None:
    console.print_json(data=json.dumps(_to_serializable(value), ensure_ascii=False))


@app.command("create-files")
def create_files(item: list[str] = typer.Option(..., help="path::content"), overwrite: bool = False) -> None:
    result = build_service().create_files(_parse_file_items(item), overwrite=overwrite)
    _print_json(result)


@app.command("read-files")
def read_files(
    path: list[str] = typer.Option(...),
    interval: list[str] | None = typer.Option(None, help="path::start:end"),
) -> None:
    line_intervals = _parse_line_intervals(interval) if interval else None
    result = build_service().read_files(path, line_intervals=line_intervals)
    _print_json(result)


@app.command("update-files")
def update_files(item: list[str] = typer.Option(..., help="path::content")) -> None:
    result = build_service().update_files(_parse_file_items(item))
    _print_json(result)


@app.command("delete-files")
def delete_files(path: list[str] = typer.Option(...)) -> None:
    result = build_service().delete_files(path)
    _print_json(result)


@app.command("search-files")
def search_files(
    base_path: str = typer.Option(...),
    name_pattern: str | None = None,
    extension: str | None = None,
    content_query: str | None = None,
) -> None:
    result = build_service().search_files(
        base_path=base_path,
        name_pattern=name_pattern,
        extension=extension,
        content_query=content_query,
    )
    _print_json(result)


@app.command("transfer-files")
def transfer_files(path: list[str] = typer.Option(...), destination: str = typer.Option(...), move: bool = False) -> None:
    result = build_service().copy_or_move_files(path, destination=destination, move=move)
    _print_json(result)


@app.command("create-dirs")
def create_dirs(path: list[str] = typer.Option(...), exist_ok: bool = False) -> None:
    result = build_service().create_directories(path, exist_ok=exist_ok)
    _print_json(result)


@app.command("read-dirs")
def read_dirs(path: list[str] = typer.Option(...)) -> None:
    result = build_service().read_directories(path)
    _print_json(result)


@app.command("update-dirs")
def update_dirs(path: list[str] = typer.Option(...), destination: str = typer.Option(...), copy: bool = False) -> None:
    result = build_service().update_directories(path, destination=destination, move=not copy)
    _print_json(result)


@app.command("delete-dirs")
def delete_dirs(path: list[str] = typer.Option(...), non_recursive: bool = False) -> None:
    result = build_service().delete_directories(path, recursive=not non_recursive)
    _print_json(result)


@app.command("search-dirs")
def search_dirs(base_path: str = typer.Option(...), name_pattern: str | None = None) -> None:
    result = build_service().search_directories(base_path, name_pattern=name_pattern)
    _print_json(result)


@app.command("transfer-dirs")
def transfer_dirs(path: list[str] = typer.Option(...), destination: str = typer.Option(...), move: bool = False) -> None:
    result = build_service().copy_or_move_directories(path, destination=destination, move=move)
    _print_json(result)


@app.command("fs-outline")
def fs_outline(base_path: str = typer.Option(...), depth: int = 3) -> None:
    result = build_service().filesystem_outline(base_path=base_path, depth=depth)
    _print_json(result)


@app.command("files-outline")
def files_outline(path: list[str] = typer.Option(...)) -> None:
    result = build_service().files_outline(path)
    _print_json(result)


def main() -> None:
    """CLI executable entry point."""
    app()
