"""Domain models for filesystem operations."""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class FileResult:
    """Represents a file-level operation result."""

    path: str
    success: bool
    message: str | None = None
    content: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a serializable dictionary."""
        return asdict(self)


@dataclass(slots=True)
class DirectoryEntry:
    """Represents a directory listing item."""

    name: str
    path: str
    entry_type: str
    size: int
    modified_at: str

    @classmethod
    def from_values(
        cls,
        *,
        name: str,
        path: str,
        entry_type: str,
        size: int,
        modified_at: datetime,
    ) -> "DirectoryEntry":
        """Create from raw values."""
        return cls(
            name=name,
            path=path,
            entry_type=entry_type,
            size=size,
            modified_at=modified_at.isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a serializable dictionary."""
        return asdict(self)


@dataclass(slots=True)
class FilesystemOutlineNode:
    """Represents one node in the filesystem outline tree."""

    name: str
    path: str
    node_type: str
    size: int
    modified_at: str
    children: list["FilesystemOutlineNode"]

    def to_dict(self) -> dict[str, Any]:
        """Convert to a serializable dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "node_type": self.node_type,
            "size": self.size,
            "modified_at": self.modified_at,
            "children": [child.to_dict() for child in self.children],
        }


@dataclass(slots=True)
class DocumentSection:
    """Represents an outline section for a source file."""

    kind: str
    name: str
    start_line: int
    end_line: int
    level: int | None = None
    doc: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a serializable dictionary."""
        return asdict(self)
