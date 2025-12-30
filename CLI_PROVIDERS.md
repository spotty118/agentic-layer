# CLI Provider Support for Agentix

Agentix can use **authenticated CLI tools** like Claude Code, OpenAI CLI, and Gemini CLI without requiring API keys! Just log in once to each tool, and Agentix will use your authenticated session.

## Benefits

✅ **No API Keys Needed** - Use already-authenticated CLI tools
✅ **No API Costs** - Free usage through your authenticated sessions
✅ **Simple Setup** - Just run `<tool> login` once
✅ **Works Like Cline/Roo Code** - Same authentication approach as VS Code extensions

---

## Supported CLI Providers

| Provider | CLI Tool | Authentication Command | Install Command |
|----------|----------|----------------------|----------------|
| **Claude** | `claude` | `claude login` | `npm install -g @anthropic/claude-code` |
| **OpenAI** | `openai` | varies by tool | varies by tool |
| **Gemini** | `gemini` or `gcloud` | `gcloud auth login` | varies by tool |

---

## Quick Setup

### 1. Install CLI Tools

**Claude Code CLI:**
```bash
npm install -g @anthropic/claude-code
```

**OpenAI CLI:**
```bash
# Check OpenAI CLI documentation for installation
pip install openai-cli  # Example - verify actual command
```

**Gemini/Google Cloud:**
```bash
# Install Google Cloud SDK which includes Gemini access
curl https://sdk.cloud.google.com | bash
```

### 2. Authenticate Once

**Claude:**
```bash
claude login
# Follow the prompts to authenticate
```

**OpenAI:**
```bash
openai login
# Or: openai api-key set
# Follow authentication steps
```

**Gemini:**
```bash
gcloud auth login
# Authenticate with your Google account
```

### 3. Enable in Agentix

Edit `.agent/config.yaml`:

```yaml
providers:
  # CLI PROVIDERS (No API keys needed!)
  claude_cli:
    enabled: true  # Enable Claude CLI

  openai_cli:
    enabled: true  # Enable OpenAI CLI

  gemini_cli:
    enabled: true  # Enable Gemini CLI
```

### 4. Use Agentix

```bash
# That's it! Agentix will now use your authenticated CLI tools
agentix specify "Add JWT authentication"
agentix plan
agentix tasks
agentix work
```

---

## How It Works

Agentix executes CLI commands in the background:

```
┌─────────────┐
│   Agentix   │
└─────┬───────┘
      │
      ├─── executes ──→ `claude "<prompt>"`
      ├─── executes ──→ `openai chat "<prompt>"`
      └─── executes ──→ `gemini chat "<prompt>"`
```

Each CLI tool:
1. Uses your stored authentication credentials
2. Processes the request
3. Returns the response to Agentix

**No HTTP servers needed. No API keys needed. Just authenticated CLI tools.**

---

## Verification

Check if your CLI tools are installed and authenticated:

**Claude:**
```bash
claude --version  # Check if installed
claude --help     # Verify it works
```

**OpenAI:**
```bash
openai --version
openai --help
```

**Gemini/Google Cloud:**
```bash
gcloud --version
gcloud auth list  # See authenticated accounts
```

---

## Configuration Examples

### Use Only CLI Providers

```yaml
providers:
  # Enable CLI providers
  claude_cli:
    enabled: true

  openai_cli:
    enabled: true

  gemini_cli:
    enabled: true

  # Disable API providers
  claude:
    enabled: false

  openai:
    enabled: false

  gemini:
    enabled: false
```

### Mix CLI and API Providers

```yaml
providers:
  # CLI providers (preferred, no cost)
  claude_cli:
    enabled: true

  # API providers (fallback if CLI unavailable)
  claude:
    enabled: true
    api_key: null  # Will use env var as fallback
```

---

## Provider Routing

When CLI providers are available, they're **prioritized automatically**:

| Task Type | Priority Order |
|-----------|----------------|
| Specification | claude_cli → claude → openai_cli → ... |
| Planning | claude_cli → claude → openai_cli → ... |
| Code Generation | openai_cli → openai → gemini_cli → ... |
| Task Execution | gemini_cli → gemini → openai_cli → ... |

This means Agentix will:
1. Try CLI providers first (free, no API costs)
2. Fall back to API providers if CLI unavailable
3. Give you the best of both worlds!

---

## Troubleshooting

### "Claude CLI not found"

```bash
# Install Claude Code CLI
npm install -g @anthropic/claude-code

# Verify installation
claude --version
```

### "Not authenticated with Claude CLI"

```bash
# Authenticate
claude login

# Follow the prompts
```

### "Provider validation failed"

```bash
# Test the CLI tool directly
claude "Hello, how are you?"

# If this works, Agentix should work too
```

### CLI Provider Not Being Used

Check your config:
```yaml
claude_cli:
  enabled: true  # Must be true!
```

Check Agentix output:
```
✓ Initialized claude_cli provider  # Should see this
```

---

## Comparison with HTTP Approach

| Approach | Setup Required | How It Works |
|----------|---------------|--------------|
| **CLI Providers** ✅ | 1. Install CLI tool<br>2. Run `<tool> login` | Agentix executes CLI commands |
| ~~HTTP Servers~~ ❌ | 1. Start HTTP server<br>2. Keep it running<br>3. Configure URLs | Agentix makes HTTP requests |

**CLI providers are simpler** - no servers to manage!

---

## Advanced: Custom CLI Commands

If your CLI tool uses different command names, you can modify the provider files:

**Example:** Using `ai-claude` instead of `claude`:

Edit `agentix/providers/claude_cli.py`:
```python
class ClaudeCLIProvider(AIProvider):
    def __init__(self):
        super().__init__(api_key=None)
        self.cli_command = "ai-claude"  # Custom command name
```

---

## Supported Workflows

### Workflow 1: Pure CLI (No API Keys Ever)

```yaml
providers:
  claude_cli: {enabled: true}
  openai_cli: {enabled: true}
  gemini_cli: {enabled: true}
  # All API providers disabled
```

**Use case:** You never want to use API keys, only authenticated CLIs.

### Workflow 2: CLI Primary, API Fallback

```yaml
providers:
  claude_cli: {enabled: true}
  claude: {enabled: true, api_key: $ANTHROPIC_API_KEY}
```

**Use case:** Use CLI when available, fall back to API if CLI fails.

### Workflow 3: API Primary (Traditional)

```yaml
providers:
  claude: {enabled: true}
  openai: {enabled: true}
  gemini: {enabled: true}
  # CLI providers disabled
```

**Use case:** You prefer using API keys directly.

---

## CLI Tool Documentation

- **Claude Code CLI:** https://github.com/anthropics/claude-code
- **OpenAI CLI:** Check OpenAI documentation
- **Google Cloud SDK:** https://cloud.google.com/sdk/docs

---

## FAQ

**Q: Do I need API keys for CLI providers?**
A: No! Just authenticate once with `<tool> login`.

**Q: Can I use both CLI and API providers?**
A: Yes! Agentix will prefer CLI providers when available.

**Q: What if my CLI tool isn't installed?**
A: Agentix will skip it and use the next available provider.

**Q: How is this different from Cline/Roo Code?**
A: Same concept! They use authenticated tools, Agentix does too.

**Q: Do CLI providers work offline?**
A: They still need internet to connect to AI services, but don't need separate API keys.

**Q: Which provider should I use?**
A: Enable all CLI providers - Agentix will intelligently choose the best one for each task!

---

## Next Steps

1. ✅ Install your preferred CLI tools
2. ✅ Authenticate with `<tool> login`
3. ✅ Enable CLI providers in `.agent/config.yaml`
4. ✅ Run `agentix specify "test task"`
5. ✅ Enjoy free, easy AI coding!

For more information, see the [main README](README.md).
