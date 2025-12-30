# Agentix

**Multi-AI Spec-Driven Coding Agent**

Agentix intelligently combines the strengths of **Claude**, **OpenAI Codex**, and **Gemini** to deliver the best spec-driven development experience. Each AI provider is automatically selected for tasks where it excels.

```
┌─────────────────────────────────────────────────────────────┐
│  Agentix - Intelligent Multi-AI Coding Agent                │
│                                                              │
│  📋 Claude      → Specs, Planning, Code Analysis            │
│  ⚡ OpenAI      → Code Generation, Task Execution           │
│  🚀 Gemini      → Fast Iterations, Large Context            │
└─────────────────────────────────────────────────────────────┘
```

## Why Agentix?

Traditional AI coding tools lock you into a single provider. **Agentix** intelligently routes tasks to the optimal AI based on:

- **Task Type**: Specs routed to Claude, code generation to OpenAI Codex
- **Context Size**: Massive codebases automatically use Gemini's 2M token window
- **Speed Requirements**: Fast iterations leverage Gemini's low latency
- **Code Understanding**: Complex refactoring uses Claude's superior analysis

## Key Features

### 🎯 Intelligent Provider Routing
- **Automatic Selection**: Best AI chosen for each task type
- **Configurable**: Override routing preferences per project
- **Fallback Support**: Gracefully handles provider unavailability

### 🏗️ Spec-Driven Workflow
1. **Specify** - Generate functional specs (Claude-optimized)
2. **Plan** - Create technical implementation plans (Claude-optimized)
3. **Tasks** - Break into atomic tasks (Claude-optimized)
4. **Work** - Execute with optimal provider (Multi-AI)
5. **Review** - Validate changes with history tracking

### 🤖 Multi-AI Integration

| Provider | Latest Model (Dec 2025) | Strengths | Best For | Access Methods |
|----------|----------|-----------|----------|----------------|
| **Claude** | Sonnet 4 (claude-sonnet-4-20250514) | Long context, Superior reasoning, Precise instructions | Specifications, Planning, Refactoring, Code Review | API + CLI 🆕 |
| **OpenAI** | GPT-4o (gpt-4o) | Excellent code generation, Fast inference, Broad knowledge | Code Generation, Task Execution, Problem Solving | API + CLI 🆕 |
| **Gemini** | Gemini 2.0 (gemini-2.0-flash-exp) | Ultra-long context (2M tokens), Lightning fast, Multimodal | Large Codebases, Fast Iterations, Rapid Prototyping | API + CLI 🆕 |
| **Ollama** | Various local models | 100% local, Privacy-focused, No API costs | Offline work, Sensitive codebases | Local only |
| **OpenRouter** | 100+ models | Flexible pricing, Wide model selection | Access to many models | API only |

**🆕 CLI Provider Support:** Use authenticated CLI tools (like `claude`, `openai`, `gemini`) without API keys! Just run `<tool> login` once, then Agentix uses your authenticated session. See [CLI_PROVIDERS.md](CLI_PROVIDERS.md) for setup.

### 🛡️ Safety & Control
- **Diff Preview**: View changes before applying with unified or side-by-side diffs
- **Automatic Backups**: File backups created before modifications
- **Interactive Confirmation**: Review and approve changes with diff previews
- **Rollback Capabilities**: Restore from automatic backups
- **Comprehensive Logging**: Full history tracking and audit trail

## Installation

```bash
pip install agentix
```

## Quick Start

### Option 1: CLI Providers (No API Keys!) 🆕

Use authenticated CLI tools without API keys:

```bash
# 1. Install and authenticate CLI tools (once)
npm install -g @anthropic/claude-code
claude login

# 2. Enable CLI providers in .agent/config.yaml
# (See CLI_PROVIDERS.md for full setup)

# 3. Initialize and start building
cd my-project
agentix init
agentix specify "Add JWT authentication"
```

### Option 2: API Providers

```bash
# 1. Set up API keys (you need at least one)
export ANTHROPIC_API_KEY='your-claude-key'
export OPENAI_API_KEY='your-openai-key'
export GOOGLE_API_KEY='your-gemini-key'

# 2. Initialize in your project
cd my-project
agentix init

# 3. Specify what you want to build
agentix specify "Add JWT authentication to the API"

# 4. Generate technical plan
agentix plan

# 5. Break into tasks
agentix tasks

# 6. Execute tasks (automatically routes to best AI)
agentix work  # Task 1
agentix work  # Task 2
agentix work  # Task 3...

# 7. Review changes
agentix review

# 8. Check status
agentix status
```

## Configuration

Create `.agent/config.yaml` to customize AI provider usage:

```yaml
providers:
  # Enable/disable providers
  claude:
    enabled: true
    default_model: claude-sonnet-4-20250514  # Latest Sonnet 4 (Dec 2025)

  openai:
    enabled: true
    default_model: gpt-4o  # Latest GPT-4o (Dec 2025)

  gemini:
    enabled: true
    default_model: gemini-2.0-flash-exp  # Gemini 2.0 (Dec 2025)

  routing:
    strategy: intelligent  # intelligent | preferred | round_robin

    # Override routing for specific tasks
    task_routing:
      specification: claude     # Claude best for specs
      planning: claude          # Claude best for planning
      tasks: claude             # Claude best for task breakdown
      code_generation: openai   # Codex excellent for code
      task_execution: gemini    # Gemini fastest
      refactoring: claude       # Claude understands code best
      review: claude            # Claude best for analysis

# General settings
temperature: 0.7
max_tokens: 4096
require_confirmation: true
auto_commit: false

logging:
  enabled: true
  level: INFO
  save_history: true
```

## Provider Selection Strategy

Agentix uses intelligent routing to select the optimal AI:

### 1. **Task-Based Routing** (Default)
```bash
# Specification → Claude (superior reasoning)
agentix specify "Add rate limiting"

# Planning → Claude (architectural thinking)
agentix plan

# Code Generation → OpenAI Codex (code expertise)
agentix work

# Large Context → Gemini (2M token window)
agentix specify "Refactor entire microservices architecture"
```

### 2. **Manual Override**
```yaml
# Force all tasks to use Claude
providers:
  routing:
    preferred_provider: claude
```

### 3. **Per-Task Override**
```yaml
providers:
  routing:
    task_routing:
      code_generation: gemini  # Use Gemini for speed
```

## Commands

| Command | Description | Default AI |
|---------|-------------|-----------|
| `agentix init` | Initialize Agentix | - |
| `agentix specify <goal>` | Generate specification | Claude |
| `agentix plan` | Create implementation plan | Claude |
| `agentix tasks` | Break into executable tasks | Claude |
| `agentix work` | Execute next task | Intelligent |
| `agentix status` | Show progress | - |
| `agentix review` | Review recent changes | - |
| `agentix history` | View execution history | - |
| `agentix rollback` | Show available backups | - |
| `agentix diff [file]` | View file diffs | - |

## Diff Viewing & Editing

Agentix includes powerful diff capabilities to review changes before and after they're applied:

### Interactive Diff Preview (During Work)
When `require_confirmation: true` in config, you'll automatically see diffs before file changes:

```bash
agentix work

# Output:
📊 Preview of changes to src/api/auth.py:

--- a/src/api/auth.py
+++ b/src/api/auth.py
@@ -10,7 +10,10 @@
 def authenticate(username, password):
-    # TODO: Implement authentication
-    pass
+    user = User.query.filter_by(username=username).first()
+    if user and user.check_password(password):
+        return generate_token(user)
+    return None

+15 -2 lines changed

Apply these changes? (y/n):
```

### Manual Diff Viewing
View diffs for any file at any time:

```bash
# View diff against most recent backup
agentix diff src/api/auth.py

# View unified diff (default)
agentix diff src/api/auth.py --type unified

# View side-by-side diff
agentix diff src/api/auth.py --type side-by-side

# Compare with specific backup (0 = most recent)
agentix diff src/api/auth.py --backup 1

# Compare two arbitrary files
agentix diff file1.py --compare file2.py

# Interactive file selection
agentix diff
```

### Diff Features
- **Unified Diff**: Standard git-style diff with +/- lines
- **Side-by-Side**: Visual comparison with color highlighting
- **Statistics**: Shows line additions/deletions count
- **Backup History**: Compare against any previous version
- **Color Coding**: Red for deletions, green for additions

## Real-World Example

```bash
# Large codebase refactoring with Gemini's massive context
cd my-monorepo
agentix init

# Gemini handles 2M tokens easily
agentix specify "Migrate all 500 microservices from REST to gRPC"

# Claude plans the architecture
agentix plan

# Claude breaks into atomic tasks
agentix tasks

# Tasks auto-route to best provider:
# - File changes → OpenAI Codex
# - Large file analysis → Gemini
# - Complex refactoring → Claude
agentix work  # Repeats until done

# Claude reviews all changes
agentix review
```

## Provider Comparison

### When to Use Each AI

**Use Claude when:**
- Writing specifications and requirements
- Planning complex architectures
- Refactoring existing code
- Reviewing code for quality and bugs
- Long reasoning chains needed

**Use OpenAI Codex when:**
- Generating new code from scratch
- Quick task execution
- General problem solving
- Function implementations

**Use Gemini when:**
- Handling large codebases (>100K tokens)
- Need ultra-fast responses
- Iterating rapidly on prototypes
- Processing multimodal inputs

## Advanced Usage

### Multi-Provider Fallback

If your preferred provider is unavailable, Agentix automatically falls back:

```python
# Routing preference: Claude → OpenAI → Gemini
# If Claude fails, tries OpenAI, then Gemini
```

### Provider Info

```bash
# See available providers
agentix status

# Output shows:
#   ✓ Initialized 3 AI providers
#   - claude (200K context)
#   - openai (128K context)
#   - gemini (2M context)
```

### Custom Prompts per Provider

```yaml
prompts:
  specify: |
    You are a product manager using {provider}.
    Generate a spec optimized for {provider}'s strengths.
```

## Architecture

```
Agentix
├── Orchestrator        # Workflow management
├── Provider Router     # Intelligent AI selection
│   ├── Claude Provider
│   ├── OpenAI Provider
│   └── Gemini Provider
├── Config Manager      # Multi-provider configuration
├── Validator           # Safety checks
└── Logger              # History tracking
```

## Requirements

- Python 3.8+
- At least one AI provider API key:
  - `ANTHROPIC_API_KEY` for Claude
  - `OPENAI_API_KEY` for OpenAI/Codex
  - `GOOGLE_API_KEY` for Gemini

## Best Practices

1. **Use all three providers** for optimal results
2. **Let intelligent routing decide** unless you have specific needs
3. **Configure task routing** for your project's specific requirements
4. **Monitor provider usage** via history logs
5. **Keep confirmation prompts enabled** for safety

## Roadmap

- [ ] Azure OpenAI support
- [ ] Local model integration (Ollama, etc.)
- [ ] Cost tracking per provider
- [ ] A/B testing between providers
- [ ] Custom provider plugins
- [ ] Web UI for provider analytics

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT - See [LICENSE](LICENSE)

## Credits

Built with ❤️ by the Agentix Team

Powered by:
- Anthropic Claude
- OpenAI GPT-4 / Codex
- Google Gemini
