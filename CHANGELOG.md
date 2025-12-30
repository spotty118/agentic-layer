# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-15

### 🚀 Major Release: Multi-AI Integration

**Agentix** - Renamed from "Agentic Layer" with complete multi-AI provider integration.

### Added
- **Multi-AI Provider System**: Integrated Claude, OpenAI Codex, and Gemini
  - Provider abstraction layer (`providers/base.py`)
  - Claude provider with 200K context support
  - OpenAI/Codex provider with GPT-4 integration
  - Gemini provider with 2M context support
- **Intelligent Provider Routing**: Automatically selects optimal AI for each task
  - Task-based routing (specs→Claude, code→OpenAI, etc.)
  - Context-size aware routing
  - Capability-based provider selection
  - Configurable routing preferences
- **Provider Configuration**: Complete multi-provider config system
  - Per-provider enable/disable
  - Custom model selection per provider
  - Task-to-provider routing rules
  - Fallback handling
- **CLI Rebranding**: Updated to `agentix` command
- **Enhanced Status**: Shows active AI providers and their capabilities

### Changed
- **Project Name**: Agentic Layer → **Agentix**
- **Package Name**: `agentic_layer` → `agentix`
- **CLI Command**: `agent` → `agentix`
- **Version**: 0.2.0 → 1.0.0 (major release)
- **Architecture**: Refactored to use provider router pattern
- **All AI calls**: Now routed through intelligent provider selection

### Dependencies
- Added: `anthropic>=0.18.0` (Claude SDK)
- Added: `google-generativeai>=0.3.0` (Gemini SDK)
- Updated: `openai>=1.0.0` (maintained)

### Documentation
- **README**: Complete rewrite showcasing multi-AI capabilities
- Added provider comparison tables
- Added routing strategy documentation
- Added real-world examples with multi-AI workflows

### Migration Guide from 0.2.0

```bash
# 1. Uninstall old version
pip uninstall agentic-layer

# 2. Install Agentix
pip install agentix

# 3. Update command usage
# Old: agent init
# New: agentix init

# 4. Set up AI provider keys
export ANTHROPIC_API_KEY='your-key'  # For Claude
export OPENAI_API_KEY='your-key'      # For OpenAI
export GOOGLE_API_KEY='your-key'      # For Gemini

# 5. Optional: Configure provider routing in .agent/config.yaml
```

## [0.2.0] - 2024-01-15

### Added
- Configuration system with YAML-based settings
- Validation framework for specs, plans, and tasks
- Logging and history tracking
- New commands: review, history, rollback
- Enhanced task execution with backups
- Testing infrastructure
- Comprehensive documentation

### Changed
- Enhanced CLI with better help text
- Improved status command
- Better error messages with colored output

### Fixed
- Better handling of LLM output
- Improved YAML parsing
- More robust file operations

## [0.1.0] - 2024-01-01

### Added
- Initial release
- Basic workflow: init → specify → plan → tasks → work
- OpenAI integration
- Simple file tree context
- Basic task execution
- YAML-based task tracking
- Status command

[1.0.0]: https://github.com/yourusername/agentix/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/yourusername/agentix/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/agentix/releases/tag/v0.1.0
