# Changelog

All notable changes to KaliVibe will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- MCP server with three tools: `execute_command`, `read_file`, `write_file`
- Persistent bash session using pexpect
- OpenAI LLM integration with tool calling
- ANSI escape code sanitization
- Command timeout protection (30s default)
- Environment-based configuration

---

## [0.1.0] - 2025-02-26

### Added
- Initial release
- Core agent loop with OpenAI integration
- MCP server exposing terminal tools
- Persistent bash session management
- File read/write operations
- Command execution with timeout handling

---

[Unreleased]: https://github.com/AimanMadan/KaliVibe/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/AimanMadan/KaliVibe/releases/tag/v0.1.0
