"""Local filesystem gateway implementation."""

from __future__ import annotations

import ast
import fnmatch
import re
import shutil
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from pathwright.domains.filesystem.models import (
    DirectoryEntry,
    DocumentSection,
    FileResult,
    FilesystemOutlineNode,
)


class LocalFilesystemGateway:
    """Implements filesystem operations using local OS files."""

    def __init__(
        self,
        whitelist_patterns: list[str] | None = None,
        blacklist_patterns: list[str] | None = None,
    ) -> None:
        self._whitelist_patterns = [
            self._normalize_pattern(pattern) for pattern in (whitelist_patterns or [])
        ]
        self._blacklist_patterns = [
            self._normalize_pattern(pattern) for pattern in (blacklist_patterns or [])
        ]

    def create_files(
        self, files: Sequence[tuple[str, str]], overwrite: bool = False
    ) -> list[FileResult]:
        results: list[FileResult] = []
        for path, content in files:
            file_path = Path(path)
            try:
                self._assert_allowed(str(file_path), kind="file")
                if file_path.exists() and not overwrite:
                    results.append(
                        FileResult(
                            path=path, success=False, message="file already exists"
                        )
                    )
                    continue
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding="utf-8")
                results.append(FileResult(path=path, success=True, message="created"))
            except OSError as error:
                results.append(FileResult(path=path, success=False, message=str(error)))
        return results

    def read_files(
        self,
        paths: Sequence[str],
        line_intervals: dict[str, Sequence[tuple[int, int]]] | None = None,
    ) -> list[FileResult]:
        results: list[FileResult] = []
        for path in paths:
            file_path = Path(path)
            try:
                self._assert_allowed(str(file_path), kind="file")
                content = file_path.read_text(encoding="utf-8")
                intervals = line_intervals.get(path) if line_intervals else None
                if intervals:
                    content = self._read_by_intervals(content, intervals)
                results.append(FileResult(path=path, success=True, content=content))
            except (OSError, ValueError) as error:
                results.append(FileResult(path=path, success=False, message=str(error)))
        return results

    def _read_by_intervals(
        self, content: str, intervals: Sequence[tuple[int, int]]
    ) -> str:
        lines = content.splitlines(keepends=True)
        chunks: list[str] = []

        for start_line, end_line in intervals:
            if start_line < 1 or end_line < 1 or start_line > end_line:
                raise ValueError("line interval must satisfy: 1 <= start <= end")

            start_index = start_line - 1
            end_index = min(end_line, len(lines))

            if start_index >= len(lines):
                continue

            chunks.append("".join(lines[start_index:end_index]))

        return "".join(chunks)

    def update_files(
        self,
        files: Sequence[tuple[str, str]],
        line_intervals: dict[str, Sequence[tuple[int, int]]] | None = None,
    ) -> list[FileResult]:
        results: list[FileResult] = []
        for path, content in files:
            file_path = Path(path)
            try:
                self._assert_allowed(str(file_path), kind="file")
                if not file_path.exists():
                    results.append(
                        FileResult(
                            path=path, success=False, message="file does not exist"
                        )
                    )
                    continue
                intervals = line_intervals.get(path) if line_intervals else None
                if intervals:
                    current_content = file_path.read_text(encoding="utf-8")
                    content = self._replace_by_intervals(
                        content=current_content,
                        intervals=intervals,
                        replacement=content,
                    )

                file_path.write_text(content, encoding="utf-8")
                results.append(FileResult(path=path, success=True, message="updated"))
            except (OSError, ValueError) as error:
                results.append(FileResult(path=path, success=False, message=str(error)))
        return results

    def _replace_by_intervals(
        self,
        content: str,
        intervals: Sequence[tuple[int, int]],
        replacement: str,
    ) -> str:
        lines = content.splitlines(keepends=True)
        normalized_intervals = sorted(
            intervals, key=lambda value: value[0], reverse=True
        )

        for start_line, end_line in normalized_intervals:
            if start_line < 1 or end_line < 1 or start_line > end_line:
                raise ValueError("line interval must satisfy: 1 <= start <= end")

            start_index = start_line - 1
            end_index = min(end_line, len(lines))

            if start_index >= len(lines):
                continue

            lines[start_index:end_index] = [replacement]

        return "".join(lines)

    def delete_files(self, paths: Sequence[str]) -> list[FileResult]:
        results: list[FileResult] = []
        for path in paths:
            file_path = Path(path)
            try:
                self._assert_allowed(str(file_path), kind="file")
                file_path.unlink()
                results.append(FileResult(path=path, success=True, message="deleted"))
            except OSError as error:
                results.append(FileResult(path=path, success=False, message=str(error)))
        return results

    def search_files(
        self,
        base_path: str,
        name_pattern: str | None = None,
        extension: str | None = None,
        content_query: str | None = None,
    ) -> list[str]:
        root = Path(base_path)
        self._assert_allowed(str(root), kind="path")
        matches: list[str] = []
        normalized_extension = None
        if extension:
            normalized_extension = (
                extension if extension.startswith(".") else f".{extension}"
            )

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if not self._is_allowed(str(file_path)):
                continue
            if name_pattern and not fnmatch.fnmatch(file_path.name, name_pattern):
                continue
            if normalized_extension and file_path.suffix != normalized_extension:
                continue
            if content_query:
                try:
                    text = file_path.read_text(encoding="utf-8")
                except OSError:
                    continue
                if content_query not in text:
                    continue
            matches.append(str(file_path))
        return matches

    def copy_or_move_files(
        self, paths: Sequence[str], destination: str, move: bool = False
    ) -> list[FileResult]:
        destination_path = Path(destination)
        self._assert_allowed(str(destination_path), kind="directory")
        destination_path.mkdir(parents=True, exist_ok=True)
        results: list[FileResult] = []

        for path in paths:
            source = Path(path)
            target = destination_path / source.name
            try:
                self._assert_allowed(str(source), kind="file")
                self._assert_allowed(str(target), kind="file")
                if move:
                    shutil.move(str(source), str(target))
                    action = "moved"
                else:
                    shutil.copy2(source, target)
                    action = "copied"
                results.append(
                    FileResult(path=path, success=True, message=f"{action} to {target}")
                )
            except OSError as error:
                results.append(FileResult(path=path, success=False, message=str(error)))
        return results

    def create_directories(
        self, paths: Sequence[str], exist_ok: bool = True
    ) -> list[FileResult]:
        results: list[FileResult] = []
        for path in paths:
            directory = Path(path)
            try:
                self._assert_allowed(str(directory), kind="directory")
                directory.mkdir(parents=True, exist_ok=exist_ok)
                results.append(FileResult(path=path, success=True, message="created"))
            except OSError as error:
                results.append(FileResult(path=path, success=False, message=str(error)))
        return results

    def read_directories(self, paths: Sequence[str]) -> dict[str, list[DirectoryEntry]]:
        data: dict[str, list[DirectoryEntry]] = {}
        for path in paths:
            directory = Path(path)
            entries: list[DirectoryEntry] = []
            if not self._is_allowed(str(directory)):
                data[path] = entries
                continue
            if not directory.is_dir():
                data[path] = entries
                continue

            for item in sorted(
                directory.iterdir(), key=lambda value: value.name.lower()
            ):
                if not self._is_allowed(str(item)):
                    continue
                stats = item.stat()
                entry = DirectoryEntry.from_values(
                    name=item.name,
                    path=str(item),
                    entry_type="directory" if item.is_dir() else "file",
                    size=stats.st_size,
                    modified_at=datetime.fromtimestamp(stats.st_mtime),
                )
                entries.append(entry)

            data[path] = entries
        return data

    def update_directories(
        self, sources: Sequence[str], destination: str, move: bool = True
    ) -> list[FileResult]:
        return self.copy_or_move_directories(
            paths=sources, destination=destination, move=move
        )

    def delete_directories(
        self, paths: Sequence[str], recursive: bool = True
    ) -> list[FileResult]:
        results: list[FileResult] = []
        for path in paths:
            directory = Path(path)
            try:
                self._assert_allowed(str(directory), kind="directory")
                if recursive:
                    shutil.rmtree(directory)
                else:
                    directory.rmdir()
                results.append(FileResult(path=path, success=True, message="deleted"))
            except OSError as error:
                results.append(FileResult(path=path, success=False, message=str(error)))
        return results

    def search_directories(
        self, base_path: str, name_pattern: str | None = None
    ) -> list[str]:
        root = Path(base_path)
        self._assert_allowed(str(root), kind="path")
        matches: list[str] = []
        for directory in root.rglob("*"):
            if not directory.is_dir():
                continue
            if not self._is_allowed(str(directory)):
                continue
            if name_pattern and not fnmatch.fnmatch(directory.name, name_pattern):
                continue
            matches.append(str(directory))
        return matches

    def copy_or_move_directories(
        self,
        paths: Sequence[str],
        destination: str,
        move: bool = False,
    ) -> list[FileResult]:
        destination_path = Path(destination)
        self._assert_allowed(str(destination_path), kind="directory")
        destination_path.mkdir(parents=True, exist_ok=True)
        results: list[FileResult] = []

        for path in paths:
            source = Path(path)
            target = destination_path / source.name
            try:
                self._assert_allowed(str(source), kind="directory")
                self._assert_allowed(str(target), kind="directory")
                if move:
                    shutil.move(str(source), str(target))
                    action = "moved"
                else:
                    shutil.copytree(source, target, dirs_exist_ok=True)
                    action = "copied"
                results.append(
                    FileResult(path=path, success=True, message=f"{action} to {target}")
                )
            except OSError as error:
                results.append(FileResult(path=path, success=False, message=str(error)))
        return results

    def filesystem_outline(
        self, base_path: str, depth: int = 3
    ) -> FilesystemOutlineNode:
        root = Path(base_path)
        self._assert_allowed(str(root), kind="path")
        return self._build_outline(root, max(depth, 0))

    def files_outline(self, paths: Sequence[str]) -> dict[str, list[DocumentSection]]:
        outlines: dict[str, list[DocumentSection]] = {}
        for path in paths:
            file_path = Path(path)
            if not self._is_allowed(str(file_path)):
                outlines[path] = []
                continue
            suffix = file_path.suffix.lower()
            try:
                content = file_path.read_text(encoding="utf-8")
            except OSError:
                outlines[path] = []
                continue

            if suffix == ".md":
                outlines[path] = self._markdown_outline(content)
            elif suffix == ".py":
                outlines[path] = self._python_outline(content)
            elif suffix == ".go":
                outlines[path] = self._go_outline(content)
            else:
                outlines[path] = []
        return outlines

    def _build_outline(self, path: Path, depth: int) -> FilesystemOutlineNode:
        stats = path.stat()
        children: list[FilesystemOutlineNode] = []
        if path.is_dir() and depth > 0:
            for child in sorted(path.iterdir(), key=lambda value: value.name.lower()):
                if not self._is_allowed(str(child)):
                    continue
                children.append(self._build_outline(child, depth - 1))
        return FilesystemOutlineNode(
            name=path.name or str(path),
            path=str(path),
            node_type="directory" if path.is_dir() else "file",
            size=stats.st_size,
            modified_at=datetime.fromtimestamp(stats.st_mtime).isoformat(),
            children=children,
        )

    def _markdown_outline(self, content: str) -> list[DocumentSection]:
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
        lines = content.splitlines()
        headings: list[tuple[int, int, str]] = []

        for index, line in enumerate(lines, start=1):
            match = heading_pattern.match(line.strip())
            if not match:
                continue
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append((index, level, title))

        sections: list[DocumentSection] = []
        for position, (start, level, title) in enumerate(headings):
            end = len(lines)
            for next_start, next_level, _ in headings[position + 1 :]:
                if next_level <= level:
                    end = next_start - 1
                    break
            sections.append(
                DocumentSection(
                    kind="heading",
                    name=title,
                    level=level,
                    start_line=start,
                    end_line=end,
                )
            )
        return sections

    def _python_outline(self, content: str) -> list[DocumentSection]:
        sections: list[DocumentSection] = []
        tree = ast.parse(content)
        module_doc = ast.get_docstring(tree)
        if module_doc:
            sections.append(
                DocumentSection(
                    kind="module_docstring",
                    name="module",
                    start_line=1,
                    end_line=1,
                    doc=module_doc,
                )
            )

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                sections.append(
                    DocumentSection(
                        kind="class",
                        name=node.name,
                        start_line=node.lineno,
                        end_line=getattr(node, "end_lineno", node.lineno),
                        doc=ast.get_docstring(node),
                    )
                )
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sections.append(
                    DocumentSection(
                        kind="function",
                        name=node.name,
                        start_line=node.lineno,
                        end_line=getattr(node, "end_lineno", node.lineno),
                        doc=ast.get_docstring(node),
                    )
                )
        return sections

    def _go_outline(self, content: str) -> list[DocumentSection]:
        lines = content.splitlines()
        sections: list[DocumentSection] = []
        function_pattern = re.compile(
            r"^func\s+(?:\([^)]+\)\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*\("
        )

        top_comments: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("//"):
                top_comments.append(stripped.removeprefix("//").strip())
                continue
            if stripped == "":
                continue
            break

        if top_comments:
            sections.append(
                DocumentSection(
                    kind="file_comment",
                    name="file",
                    start_line=1,
                    end_line=len(top_comments),
                    doc="\n".join(top_comments),
                )
            )

        for index, line in enumerate(lines, start=1):
            match = function_pattern.match(line.strip())
            if not match:
                continue
            name = match.group(1)
            comment = self._extract_go_function_comment(lines, index)
            sections.append(
                DocumentSection(
                    kind="function",
                    name=name,
                    start_line=index,
                    end_line=index,
                    doc=comment,
                )
            )
        return sections

    def _extract_go_function_comment(
        self, lines: list[str], start_line: int
    ) -> str | None:
        comments: list[str] = []
        cursor = start_line - 2
        while cursor >= 0:
            line = lines[cursor].strip()
            if line.startswith("//"):
                comments.append(line.removeprefix("//").strip())
                cursor -= 1
                continue
            if line == "":
                cursor -= 1
                continue
            break
        if not comments:
            return None
        return "\n".join(reversed(comments))

    def _normalize_path(self, path: str) -> str:
        return str(Path(path).expanduser().resolve(strict=False)).replace("\\", "/")

    def _normalize_pattern(self, pattern: str) -> str:
        pattern = pattern.strip()
        if not pattern:
            return pattern
        normalized = pattern.replace("\\", "/")
        wildcard_parts = ["*", "?", "[", "]"]
        if normalized.startswith("~/"):
            normalized = str(Path(normalized).expanduser()).replace("\\", "/")
        elif not Path(normalized).is_absolute():
            normalized = str((Path.cwd() / normalized).resolve(strict=False)).replace(
                "\\", "/"
            )
        if not any(part in normalized for part in wildcard_parts):
            normalized = self._normalize_path(normalized)
        return normalized

    def _matches_pattern(self, normalized_path: str, pattern: str) -> bool:
        if not pattern:
            return False
        if pattern.endswith("/**"):
            base = pattern[:-3].rstrip("/")
            return normalized_path == base or normalized_path.startswith(f"{base}/")
        return fnmatch.fnmatch(normalized_path, pattern)

    def _match_first(self, normalized_path: str, patterns: list[str]) -> str | None:
        for pattern in patterns:
            if self._matches_pattern(normalized_path, pattern):
                return pattern
        return None

    def _is_allowed(self, path: str) -> bool:
        normalized_path = self._normalize_path(path)
        blacklisted_by = self._match_first(normalized_path, self._blacklist_patterns)
        if blacklisted_by:
            return False
        if not self._whitelist_patterns:
            return True
        whitelisted_by = self._match_first(normalized_path, self._whitelist_patterns)
        return whitelisted_by is not None

    def _assert_allowed(self, path: str, *, kind: str) -> None:
        normalized_path = self._normalize_path(path)
        blacklisted_by = self._match_first(normalized_path, self._blacklist_patterns)
        if blacklisted_by:
            raise PermissionError(
                f"Access denied for {kind} '{path}': matched blacklist pattern '{blacklisted_by}'."
            )

        if self._whitelist_patterns:
            whitelisted_by = self._match_first(
                normalized_path, self._whitelist_patterns
            )
            if not whitelisted_by:
                raise PermissionError(
                    f"Access denied for {kind} '{path}': not matched by whitelist patterns."
                )
