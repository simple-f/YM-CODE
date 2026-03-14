# Changelog

All notable changes to YM-CODE will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Web interface development
- VS Code extension
- Multi-agent workspace
- Enhanced MCP server integration

---

## [0.1.0] - 2026-03-14

### Added
- **Core Functionality**
  - Agent system with 18 built-in tools
  - 9 skills (Memory, Search, HTTP, Shell, Formatter, Code Analysis, Database, Docker, Self-Improvement)
  - MCP client integration
  - CLI interface with rich panels

- **Cross-Platform Support**
  - Windows 10/11 support
  - Linux support (Ubuntu, CentOS, Debian)
  - macOS support (11+)
  - Automatic shell command translation (ls→dir, cat→type, etc.)
  - Cross-platform emoji handling

- **Tools**
  - File operations (read, write, list)
  - Git integration (status, diff, commit, push, log)
  - Smart edit tools
  - Regex tools (replace, search, validate)
  - Test runner

- **Documentation**
  - README.md
  - CROSS_PLATFORM.md
  - TEST_REPORT.md
  - SETUP.md
  - INSTALL.md
  - QUICKSTART.md
  - MCP_GUIDE.md
  - SKILLS_MCP_INTEGRATION.md

### Fixed
- Log file locking issue on Windows
- Skills registry empty on initialization
- Shell skill asyncio import error
- CLI emoji encoding on Windows
- Duplicate code in app.py
- Platform-specific command handling

### Changed
- Unified UTF-8 encoding across all platforms
- Improved error messages
- Enhanced cross-platform compatibility

---

## [0.0.1] - 2026-03-01

### Added
- Initial project setup
- Basic agent loop
- MCP client prototype
- Skills system prototype

---

## Version Numbering

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)
