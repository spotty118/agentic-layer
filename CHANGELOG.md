# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-01-15

### Added
- **Configuration System**: Added `config.py` with YAML-based configuration
  - Customizable AI model selection
  - Custom system prompts
  - Temperature and token limits
  - Logging preferences
  - Confirmation and auto-commit settings
- **Validation Framework**: Added `validators.py` with comprehensive validation
  - Spec, plan, and task validation
  - Task execution validation
  - File content validation
  - Safe file operation wrappers
- **Logging and History**: Added `logger.py` with structured logging
  - JSON-based operation history
  - Task execution tracking
  - Colored console output
  - History review capabilities
- **New Commands**:
  - `agent review` - Review recent changes
  - `agent history` - View execution history
  - `agent rollback` - Show available backups
- **Enhanced Task Execution**:
  - Automatic backup before modifications
  - Support for `run_command` action
  - File deletion support
  - Interactive confirmation prompts
  - Better error handling and validation
- **Testing Infrastructure**:
  - Comprehensive test suite
  - pytest configuration
  - Tests for config, validators, and logger
- **Documentation**:
  - Comprehensive README with examples
  - EXAMPLES.md with real-world workflows
  - CONTRIBUTING.md with development guidelines
  - Improved code documentation

### Changed
- Enhanced CLI with better help text and error handling
- Improved status command with detailed progress tracking
- Better error messages with colored output
- Updated setup.py with proper metadata and dependencies

### Fixed
- Better handling of LLM output (markdown code block stripping)
- Improved YAML parsing for tasks
- More robust file operations

## [0.1.0] - 2024-01-01

### Added
- Initial release
- Basic workflow: init → specify → plan → tasks → work
- OpenAI integration for AI-assisted development
- Simple file tree context gathering
- Basic task execution
- YAML-based task tracking
- Status command for progress tracking

[0.2.0]: https://github.com/yourusername/agentic-layer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/agentic-layer/releases/tag/v0.1.0
