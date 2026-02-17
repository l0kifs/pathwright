"""Application services for filesystem use-cases."""

from collections.abc import Sequence
from typing import Protocol

from pathwright.domains.filesystem.models import (
    DirectoryEntry,
    DocumentSection,
    FileResult,
    FilesystemOutlineNode,
)


class FilesystemGateway(Protocol):
    """Port for filesystem operations."""

    def create_files(self, files: Sequence[tuple[str, str]], overwrite: bool = False) -> list[FileResult]: ...

    def read_files(
        self,
        paths: Sequence[str],
        line_intervals: dict[str, Sequence[tuple[int, int]]] | None = None,
    ) -> list[FileResult]: ...

    def update_files(self, files: Sequence[tuple[str, str]]) -> list[FileResult]: ...

    def delete_files(self, paths: Sequence[str]) -> list[FileResult]: ...

    def search_files(
        self,
        base_path: str,
        name_pattern: str | None = None,
        extension: str | None = None,
        content_query: str | None = None,
    ) -> list[str]: ...

    def copy_or_move_files(self, paths: Sequence[str], destination: str, move: bool = False) -> list[FileResult]: ...

    def create_directories(self, paths: Sequence[str], exist_ok: bool = True) -> list[FileResult]: ...

    def read_directories(self, paths: Sequence[str]) -> dict[str, list[DirectoryEntry]]: ...

    def update_directories(self, sources: Sequence[str], destination: str, move: bool = True) -> list[FileResult]: ...

    def delete_directories(self, paths: Sequence[str], recursive: bool = True) -> list[FileResult]: ...

    def search_directories(self, base_path: str, name_pattern: str | None = None) -> list[str]: ...

    def copy_or_move_directories(
        self,
        paths: Sequence[str],
        destination: str,
        move: bool = False,
    ) -> list[FileResult]: ...

    def filesystem_outline(self, base_path: str, depth: int = 3) -> FilesystemOutlineNode: ...

    def files_outline(self, paths: Sequence[str]) -> dict[str, list[DocumentSection]]: ...


class FilesystemService:
    """Use-case service for all BRD filesystem operations."""

    def __init__(self, gateway: FilesystemGateway) -> None:
        self._gateway = gateway

    def create_files(self, files: Sequence[tuple[str, str]], overwrite: bool = False) -> list[FileResult]:
        return self._gateway.create_files(files, overwrite=overwrite)

    def read_files(
        self,
        paths: Sequence[str],
        line_intervals: dict[str, Sequence[tuple[int, int]]] | None = None,
    ) -> list[FileResult]:
        return self._gateway.read_files(paths, line_intervals=line_intervals)

    def update_files(self, files: Sequence[tuple[str, str]]) -> list[FileResult]:
        return self._gateway.update_files(files)

    def delete_files(self, paths: Sequence[str]) -> list[FileResult]:
        return self._gateway.delete_files(paths)

    def search_files(
        self,
        base_path: str,
        name_pattern: str | None = None,
        extension: str | None = None,
        content_query: str | None = None,
    ) -> list[str]:
        return self._gateway.search_files(
            base_path=base_path,
            name_pattern=name_pattern,
            extension=extension,
            content_query=content_query,
        )

    def copy_or_move_files(self, paths: Sequence[str], destination: str, move: bool = False) -> list[FileResult]:
        return self._gateway.copy_or_move_files(paths=paths, destination=destination, move=move)

    def create_directories(self, paths: Sequence[str], exist_ok: bool = True) -> list[FileResult]:
        return self._gateway.create_directories(paths=paths, exist_ok=exist_ok)

    def read_directories(self, paths: Sequence[str]) -> dict[str, list[DirectoryEntry]]:
        return self._gateway.read_directories(paths)

    def update_directories(self, sources: Sequence[str], destination: str, move: bool = True) -> list[FileResult]:
        return self._gateway.update_directories(sources=sources, destination=destination, move=move)

    def delete_directories(self, paths: Sequence[str], recursive: bool = True) -> list[FileResult]:
        return self._gateway.delete_directories(paths=paths, recursive=recursive)

    def search_directories(self, base_path: str, name_pattern: str | None = None) -> list[str]:
        return self._gateway.search_directories(base_path=base_path, name_pattern=name_pattern)

    def copy_or_move_directories(
        self,
        paths: Sequence[str],
        destination: str,
        move: bool = False,
    ) -> list[FileResult]:
        return self._gateway.copy_or_move_directories(paths=paths, destination=destination, move=move)

    def filesystem_outline(self, base_path: str, depth: int = 3) -> FilesystemOutlineNode:
        return self._gateway.filesystem_outline(base_path=base_path, depth=depth)

    def files_outline(self, paths: Sequence[str]) -> dict[str, list[DocumentSection]]:
        return self._gateway.files_outline(paths)
