# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-12-30

### 🎯 Interactive Model Selection

**Major UX Improvement**: Terminal-based interactive model selection - no more config file editing!

### Added
- **Interactive Model Selection Command**: `agentix models select [provider]`
  - Terminal-based interactive model picker
  - Browse available models with descriptions
  - See current model before changing
  - Automatic configuration saving
- **Dynamic Model Fetching**: All providers now fetch available models dynamically
  - Claude API/CLI: Comprehensive list of Claude 4.5, 4.0, and 3.x models
  - OpenAI API/CLI: Fetches models via API (GPT-4, Codex, O1, O3 series)
  - Gemini API/CLI: Fetches models via API (Gemini 3.0, 2.0, 1.5 series)
  - Fallback to known models if API fetch fails
- **Model Listing Command**: `agentix models list [provider]`
  - View all available models for a provider
  - Shows model IDs and descriptions
  - Interactive provider selection if not specified

### Enhanced
- **ModelCommands Class**: Added `select_model()` method with full interactive flow
- **Provider Base**: All providers now implement `get_available_models()`
  - Claude providers: 7 models (Opus 4.5, Sonnet 4.5, Haiku 4.5, etc.)
  - OpenAI providers: Dynamic API fetch + 6 fallback models
  - Gemini providers: Dynamic API fetch + 5 fallback models
- **CLI Help**: Updated welcome message to highlight new feature
- **Documentation**: Comprehensive section in README with examples

### Benefits
- **No File Editing**: Everything happens in the terminal
- **Up-to-Date Models**: Automatically fetches latest models from providers
- **Better UX**: See all options before selecting
- **Safe**: Preview current model before changing
- **Fast**: Immediate configuration with automatic saving

### Example Usage
```bash
# Interactive model selection
agentix models select

# Select model for specific provider
agentix models select claude
agentix models select openai

# List available models
agentix models list gemini
```

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
