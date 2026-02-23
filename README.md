<p align="center">
	<img src="https://capsule-render.vercel.app/api?type=waving&color=0:4F46E5,100:06B6D4&height=200&section=header&text=pathwright&fontSize=56&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Python%20filesystem%20toolkit%20for%20CLI%20and%20MCP&descAlignY=58&descSize=16" alt="pathwright banner" />
</p>

<p align="center">
	<a href="https://github.com/l0kifs/pathwright/actions/workflows/publish-to-pypi.yml"><img src="https://img.shields.io/github/actions/workflow/status/l0kifs/pathwright/publish-to-pypi.yml?branch=main&label=publish" alt="Publish workflow" /></a>
	<a href="https://pypi.org/project/pathwright/"><img src="https://img.shields.io/pypi/v/pathwright" alt="PyPI version" /></a>
	<a href="https://pypi.org/project/pathwright/"><img src="https://img.shields.io/pypi/pyversions/pathwright" alt="Python versions" /></a>
	<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT license" /></a>
</p>

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
uv run pathwright update-files --item "tmp/a.txt::patched\n" --interval "tmp/a.txt::2:4"
uv run pathwright search-files --base-path . --extension py --name-pattern "*.py"
uv run pathwright fs-outline --base-path . --depth 2
```

## MCP Server

Run with:

```bash
uv run pathwright-mcp
```

VS Code workspace MCP config example (`.vscode/mcp.json`):

```json
{
	"servers": {
		"pathwright": {
			"type": "stdio",
			"command": "uvx",
			"args": ["--from", "pathwright", "pathwright-mcp"]
		}
	}
}
```

For local testing from the current workspace (after `uv sync --all-groups`):

```json
{
	"servers": {
		"pathwrightLocal": {
			"type": "stdio",
			"command": "uv",
			"args": ["run", "pathwright-mcp"],
			"cwd": "${workspaceFolder}"
		}
	}
}
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
