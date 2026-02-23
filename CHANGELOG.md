# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-23

### Added
- `update-files` command: update files with support for line intervals (CLI and MCP server)
- Schema regression tests for MCP tool argument schemas
- VS Code MCP config examples in documentation

### Changed
- CLI and MCP server: normalized file and line interval input formats for consistency
- Enhanced documentation for new command usage and parameters

### Fixed
- Improved edge case handling for file update and read operations with line intervals

## [0.1.0] - 2026-02-23

### Added
- Initial public release of `pathwright` on PyPI.
- CLI entry point for filesystem operations.
- MCP server entry point for AI integrations.
- Core filesystem domain services, models, and exceptions.
- Local filesystem gateway implementation.
- End-to-end test suite covering filesystem operations and access control.
- Documentation for usage, reference, and publishing.
