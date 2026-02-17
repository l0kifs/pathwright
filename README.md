# pathwright

Pathwright is a Python filesystem operations toolkit with two entry points:
- CLI for terminal workflows
- MCP server for AI model integrations

Detailed usage reference: [docs/REFERENCE.md](docs/REFERENCE.md)

## Installation

```bash
uv sync --all-groups
```

## CLI

Run with:

```bash
uv run pathwright --help
```

Supported command groups:
- `create-files`, `read-files`, `update-files`, `delete-files`
- `search-files`, `transfer-files`
- `create-dirs`, `read-dirs`, `update-dirs`, `delete-dirs`
- `search-dirs`, `transfer-dirs`
- `fs-outline`, `files-outline`

Examples:

```bash
uv run pathwright create-files --item "tmp/a.txt::hello"
uv run pathwright read-files --path "tmp/a.txt"
uv run pathwright search-files --base-path . --extension py --name-pattern "*.py"
uv run pathwright fs-outline --base-path . --depth 2
```

## MCP Server

Run with:

```bash
uv run pathwright-mcp
```

Exposed tools map to the same filesystem operations as CLI:
- `create_files`, `read_files`, `update_files`, `delete_files`
- `search_files`, `copy_or_move_files`
- `create_directories`, `read_directories`, `update_directories`, `delete_directories`
- `search_directories`, `copy_or_move_directories`
- `filesystem_outline`, `files_outline`

## Testing

Run feature-organized end-to-end suites:

```bash
uv run pytest --maxfail=1 --tb=short
```
