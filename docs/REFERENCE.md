# Pathwright Reference

Updated: 2026-02-23

## Entry Points

- CLI: `uv run pathwright --help`
- MCP server: `uv run pathwright-mcp`

## Access Control Settings

Pathwright supports configurable path allow/deny rules via environment variables:

- `PATHWRIGHT__PATH_WHITELIST`: JSON list of allowed path patterns.
- `PATHWRIGHT__PATH_BLACKLIST`: JSON list of denied path patterns.

Rules:
- Blacklist is evaluated first.
- If whitelist is empty, all non-blacklisted paths are allowed.
- If whitelist is not empty, path must match whitelist and must not match blacklist.

Pattern support:
- Exact path: `/data/file.txt`
- Wildcards: `/data/*.txt`, `/data/*/report-?.md`
- Include subdirectories: `/data/project/**` (matches directory and all descendants)

Example:

```bash
export PATHWRIGHT__PATH_WHITELIST='["/workspace/allowed/**"]'
export PATHWRIGHT__PATH_BLACKLIST='["/workspace/allowed/private/**"]'
```

When denied, operations return clear errors such as:
- `Access denied for file '/path': matched blacklist pattern '...'.`
- `Access denied for path '/path': not matched by whitelist patterns.`

## Abilities

### Files

#### Create Files

**CLI Command**: `create-files --item "path::content" [--item "path2::content2"] [--overwrite]`  
**MCP Tool**: `create_files(files: list[list[str]], overwrite: bool = False)`

**Arguments**:
- `item` / `files`: File definitions. Each entry is `[path, content]`; CLI uses `path::content`.
- `overwrite`: Allow replacing existing files.

**Examples**:
- CLI: `uv run pathwright create-files --item "tmp/a.txt::hello" --item "tmp/b.txt::world"`
- MCP: `create_files(files=[["tmp/a.txt", "hello"]], overwrite=False)`

#### Read Files

**CLI Command**: `read-files --path "file1" [--path "file2"] [--interval "path::start:end"]`  
**MCP Tool**: `read_files(paths: list[str], line_intervals: dict[str, list[list[int]]] | None = None)`

**Arguments**:
- `path` / `paths`: One or more file paths.
- `interval`: Optional line intervals per file in `path::start:end` format. Repeat flag to pass multiple intervals.
- `line_intervals`: Optional map from file path to one or more `[start, end]` line intervals (1-based, inclusive).

**Behavior**:
- If no intervals are provided, returns full file content.
- If intervals are provided, returns only requested line ranges in provided order.
- Out-of-range intervals are handled gracefully and return only available lines.
- Invalid intervals (`start < 1`, `end < 1`, `start > end`) return an error result for that file.

**Examples**:
- CLI: `uv run pathwright read-files --path "tmp/a.txt"`
- CLI: `uv run pathwright read-files --path "tmp/a.txt" --interval "tmp/a.txt::10:20"`
- MCP: `read_files(paths=["tmp/a.txt", "tmp/b.txt"], line_intervals={"tmp/a.txt": [[1, 50], [120, 150]]})`

#### Update Files

**CLI Command**: `update-files --item "path::new content" [--item "path2::new content"] [--interval "path::start:end"]`  
**MCP Tool**: `update_files(files: list[list[str]], line_intervals: dict[str, list[list[int]]] | None = None)`

**Arguments**:
- `item` / `files`: Updated file content definitions.
- `interval`: Optional line intervals per file in `path::start:end` format. Repeat flag to pass multiple intervals.
- `line_intervals`: Optional map from file path to one or more `[start, end]` line intervals (1-based, inclusive).

**Behavior**:
- If no intervals are provided, replaces full file content.
- If intervals are provided, replaces each requested line range with the provided content.
- Out-of-range intervals are handled gracefully and leave file content unchanged for those ranges.
- Invalid intervals (`start < 1`, `end < 1`, `start > end`) return an error result for that file.

**Examples**:
- CLI: `uv run pathwright update-files --item "tmp/a.txt::updated"`
- CLI: `uv run pathwright update-files --item "tmp/a.txt::replacement\n" --interval "tmp/a.txt::10:20"`
- MCP: `update_files(files=[["tmp/a.txt", "updated"]])`
- MCP: `update_files(files=[["tmp/a.txt", "replacement\n"]], line_intervals={"tmp/a.txt": [[10, 20]]})`

#### Delete Files

**CLI Command**: `delete-files --path "file1" [--path "file2"]`  
**MCP Tool**: `delete_files(paths: list[str])`

**Arguments**:
- `path` / `paths`: One or more file paths.

**Examples**:
- CLI: `uv run pathwright delete-files --path "tmp/a.txt"`
- MCP: `delete_files(paths=["tmp/a.txt"])`

#### Search Files

**CLI Command**: `search-files --base-path . [--name-pattern "*.py"] [--extension py] [--content-query "text"]`  
**MCP Tool**: `search_files(base_path: str, name_pattern: str | None = None, extension: str | None = None, content_query: str | None = None)`

**Arguments**:
- `base_path`: Root directory for search.
- `name_pattern`: Optional glob pattern.
- `extension`: Optional file extension filter (`py` or `.py`).
- `content_query`: Optional substring to match in text files.

**Examples**:
- CLI: `uv run pathwright search-files --base-path . --name-pattern "*.md" --content-query "Pathwright"`
- MCP: `search_files(base_path=".", extension="py")`

#### Copy or Move Files

**CLI Command**: `transfer-files --path "a.txt" [--path "b.txt"] --destination "out" [--move]`  
**MCP Tool**: `copy_or_move_files(paths: list[str], destination: str, move: bool = False)`

**Arguments**:
- `path` / `paths`: Source file paths.
- `destination`: Target directory.
- `move`: Move instead of copy.

**Examples**:
- CLI: `uv run pathwright transfer-files --path "tmp/a.txt" --destination "tmp/out"`
- MCP: `copy_or_move_files(paths=["tmp/a.txt"], destination="tmp/out", move=True)`

### Directories

#### Create Directories

**CLI Command**: `create-dirs --path "dir1" [--path "dir2"] [--exist-ok]`  
**MCP Tool**: `create_directories(paths: list[str], exist_ok: bool = True)`

**Arguments**:
- `path` / `paths`: Directories to create.
- `exist_ok`: Do not fail if directory exists.

**Examples**:
- CLI: `uv run pathwright create-dirs --path "tmp/data" --exist-ok`
- MCP: `create_directories(paths=["tmp/data"], exist_ok=True)`

#### Read Directories

**CLI Command**: `read-dirs --path "." [--path "./docs"]`  
**MCP Tool**: `read_directories(paths: list[str])`

**Arguments**:
- `path` / `paths`: One or more directories to list.

**Examples**:
- CLI: `uv run pathwright read-dirs --path "."`
- MCP: `read_directories(paths=[".", "./docs"])`

#### Update Directories (Move/Copy)

**CLI Command**: `update-dirs --path "src_dir" [--path "src_dir2"] --destination "out" [--copy]`  
**MCP Tool**: `update_directories(paths: list[str], destination: str, move: bool = True)`

**Arguments**:
- `path` / `paths`: Source directories.
- `destination`: Target directory.
- `copy` (CLI): Copy instead of move.
- `move` (MCP): Move when `True`, copy when `False`.

**Examples**:
- CLI: `uv run pathwright update-dirs --path "tmp/src" --destination "tmp/out" --copy`
- MCP: `update_directories(paths=["tmp/src"], destination="tmp/out", move=False)`

#### Delete Directories

**CLI Command**: `delete-dirs --path "dir1" [--path "dir2"] [--non-recursive]`  
**MCP Tool**: `delete_directories(paths: list[str], recursive: bool = True)`

**Arguments**:
- `path` / `paths`: Directories to delete.
- `non-recursive` (CLI): Remove only empty directories.
- `recursive` (MCP): Remove directories recursively.

**Examples**:
- CLI: `uv run pathwright delete-dirs --path "tmp/out"`
- MCP: `delete_directories(paths=["tmp/out"], recursive=True)`

#### Search Directories

**CLI Command**: `search-dirs --base-path . [--name-pattern "build*"]`  
**MCP Tool**: `search_directories(base_path: str, name_pattern: str | None = None)`

**Arguments**:
- `base_path`: Root directory for search.
- `name_pattern`: Optional directory name glob.

**Examples**:
- CLI: `uv run pathwright search-dirs --base-path . --name-pattern "test*"`
- MCP: `search_directories(base_path=".", name_pattern="src*")`

#### Copy or Move Directories

**CLI Command**: `transfer-dirs --path "dir1" [--path "dir2"] --destination "out" [--move]`  
**MCP Tool**: `copy_or_move_directories(paths: list[str], destination: str, move: bool = False)`

**Arguments**:
- `path` / `paths`: Source directories.
- `destination`: Target directory.
- `move`: Move instead of copy.

**Examples**:
- CLI: `uv run pathwright transfer-dirs --path "tmp/src" --destination "tmp/out" --move`
- MCP: `copy_or_move_directories(paths=["tmp/src"], destination="tmp/out", move=True)`

### Outlines

#### Filesystem Outline

**CLI Command**: `fs-outline --base-path . [--depth 3]`  
**MCP Tool**: `filesystem_outline(base_path: str, depth: int = 3)`

**Arguments**:
- `base_path`: Root path to outline.
- `depth`: Maximum tree depth.

**Examples**:
- CLI: `uv run pathwright fs-outline --base-path . --depth 2`
- MCP: `filesystem_outline(base_path=".", depth=2)`

#### Files Outline

**CLI Command**: `files-outline --path "doc.md" --path "main.py" --path "app.go"`  
**MCP Tool**: `files_outline(paths: list[str])`

**Arguments**:
- `path` / `paths`: File paths to parse.

**Output by file type**:
- Markdown (`.md`): headings with level and line range.
- Python (`.py`): module docstring, classes, functions, line ranges, docstrings.
- Go (`.go`): top file comments and functions with nearby comments.

**Examples**:
- CLI: `uv run pathwright files-outline --path "README.md" --path "src/pathwright/entry_points/cli.py"`
- MCP: `files_outline(paths=["README.md", "src/pathwright/entry_points/cli.py"])`
