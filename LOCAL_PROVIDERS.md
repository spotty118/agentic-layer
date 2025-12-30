# Local AI Provider Setup for Agentix

Agentix now supports connecting to **locally installed AI providers** without requiring API keys! This allows you to use Claude Code, Gemini, and OpenAI/Codex installed locally (like VS Code extensions or local instances) similar to how Cline, Roo Code, and Kilo Code work.

## Benefits of Local Providers

✅ **No API Keys Required** - Connect to local installations directly
✅ **No API Costs** - Free usage through local connections
✅ **Lower Latency** - Direct local communication
✅ **Privacy** - Data stays on your machine
✅ **Works Offline** - No internet required once installed

## Supported Local Providers

| Provider | Default Port | Environment Variable | Description |
|----------|-------------|---------------------|-------------|
| **local_claude** | 3000 | `CLAUDE_LOCAL_URL` | Local Claude Code instance |
| **local_openai** | 3002 | `OPENAI_LOCAL_URL` | Local OpenAI/Codex instance |
| **local_gemini** | 3001 | `GEMINI_LOCAL_URL` | Local Gemini instance |

---

## Quick Start

### 1. Enable Local Providers

Edit your `.agent/config.yaml`:

```yaml
providers:
  # LOCAL PROVIDERS (No API keys needed!)
  local_claude:
    enabled: true  # Set to true
    base_url: http://localhost:3000  # Or your custom URL

  local_openai:
    enabled: true  # Set to true
    base_url: http://localhost:3002  # Or your custom URL

  local_gemini:
    enabled: true  # Set to true
    base_url: http://localhost:3001  # Or your custom URL
```

### 2. Start Your Local AI Provider

Ensure your local AI provider is running and exposing an HTTP API. The provider must implement the **OpenAI-compatible chat completions API**.

### 3. Use Agentix

```bash
# Agentix will automatically use local providers when available
agentix specify "Add JWT authentication"
agentix plan
agentix tasks
agentix work
```

**Local providers are prioritized** when both local and remote providers are available, saving you API costs!

---

## Environment Variables

Instead of editing `config.yaml`, you can set environment variables:

```bash
# Set local provider URLs
export CLAUDE_LOCAL_URL=http://localhost:3000
export OPENAI_LOCAL_URL=http://localhost:3002
export GEMINI_LOCAL_URL=http://localhost:3001

# Now run Agentix
agentix specify "Build a REST API"
```

---

## Setting Up Local Providers

### Option 1: VS Code Extensions

If you have Claude Code, OpenAI, or Gemini VS Code extensions installed, you'll need to enable their HTTP API servers.

**For Claude Code Extension:**
1. Open VS Code settings
2. Search for "Claude Code HTTP Server"
3. Enable HTTP API on port 3000
4. Configure in Agentix:
   ```yaml
   local_claude:
     enabled: true
     base_url: http://localhost:3000
   ```

**For OpenAI Extension:**
1. Configure OpenAI extension to expose HTTP API on port 3002
2. Configure in Agentix:
   ```yaml
   local_openai:
     enabled: true
     base_url: http://localhost:3002
   ```

**For Gemini Extension:**
1. Configure Gemini extension to expose HTTP API on port 3001
2. Configure in Agentix:
   ```yaml
   local_gemini:
     enabled: true
     base_url: http://localhost:3001
   ```

### Option 2: Local HTTP Proxy

You can create a simple HTTP proxy server that forwards requests to your local AI installations:

```python
# local_ai_server.py
from flask import Flask, request, jsonify
import anthropic  # or openai, google.generativeai

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.json
    # Forward to your local AI provider
    # Return OpenAI-compatible response
    return jsonify({
        "choices": [{
            "message": {
                "content": response_text
            }
        }]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(port=3000)
```

Run the server:
```bash
python local_ai_server.py
```

### Option 3: LiteLLM Proxy

Use [LiteLLM](https://github.com/BerriAI/litellm) to create OpenAI-compatible endpoints for any AI provider:

```bash
# Install LiteLLM
pip install litellm[proxy]

# Start proxy for Claude
litellm --model claude-3-5-sonnet-20241022 --port 3000

# Start proxy for Gemini
litellm --model gemini/gemini-1.5-flash --port 3001

# Start proxy for OpenAI
litellm --model gpt-4-turbo --port 3002
```

Then configure Agentix:
```yaml
local_claude:
  enabled: true
  base_url: http://localhost:3000

local_gemini:
  enabled: true
  base_url: http://localhost:3001

local_openai:
  enabled: true
  base_url: http://localhost:3002
```

---

## API Requirements

Your local provider must implement these endpoints:

### 1. Chat Completions (Required)

```http
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "model-name",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"}
  ],
  "temperature": 0.7,
  "max_tokens": 4096
}
```

**Response:**
```json
{
  "choices": [
    {
      "message": {
        "content": "Response text here"
      }
    }
  ]
}
```

### 2. Health Check (Recommended)

```http
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

### 3. Model Listing (Optional)

```http
GET /v1/models
```

**Response:**
```json
{
  "data": [
    {"id": "model-1"},
    {"id": "model-2"}
  ]
}
```

---

## Configuration Examples

### Use Only Local Providers

```yaml
providers:
  # Enable local providers
  local_claude:
    enabled: true
    base_url: http://localhost:3000

  local_openai:
    enabled: true
    base_url: http://localhost:3002

  local_gemini:
    enabled: true
    base_url: http://localhost:3001

  # Disable remote API providers
  claude:
    enabled: false

  openai:
    enabled: false

  gemini:
    enabled: false
```

### Mix Local and Remote Providers

```yaml
providers:
  # Local providers (preferred, no cost)
  local_claude:
    enabled: true

  # Remote providers (fallback if local unavailable)
  claude:
    enabled: true
    api_key: sk-ant-xxx  # API key for fallback
```

### Force Local-Only Mode

```yaml
providers:
  routing:
    strategy: intelligent
    task_routing:
      specification: local_claude
      planning: local_claude
      code_generation: local_openai
      task_execution: local_gemini
      # Agentix will use local providers only
```

---

## Provider Routing

When both local and remote providers are available, **local providers are prioritized**:

| Task Type | Priority Order |
|-----------|---------------|
| Specification | local_claude → claude → local_openai → openai → ... |
| Planning | local_claude → claude → local_openai → openai → ... |
| Code Generation | local_openai → openai → local_gemini → gemini → ... |
| Task Execution | local_gemini → gemini → local_openai → openai → ... |
| Refactoring | local_claude → claude → local_openai → openai → ... |
| Review | local_claude → claude → local_openai → openai → ... |

This means you'll **automatically use free local providers** when available, with automatic fallback to remote APIs.

---

## Troubleshooting

### Provider Not Found

```
⚠ local_claude validation failed - skipping
```

**Solution:**
1. Check that your local provider is running: `curl http://localhost:3000/health`
2. Verify the port is correct in config
3. Check firewall settings
4. Test the endpoint manually:
   ```bash
   curl -X POST http://localhost:3000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"test","messages":[{"role":"user","content":"hi"}]}'
   ```

### Connection Refused

```
Could not connect to local Claude at http://localhost:3000
```

**Solution:**
1. Ensure the provider is running
2. Check the URL/port in config
3. Verify no other service is using the port
4. Try a different port and update config

### Invalid Response Format

```
Invalid response format from local Claude
```

**Solution:**
Your local provider must return OpenAI-compatible responses:
```json
{
  "choices": [
    {
      "message": {
        "content": "text here"
      }
    }
  ]
}
```

---

## Custom Ports

Using non-standard ports? Configure them:

```yaml
local_claude:
  enabled: true
  base_url: http://localhost:8080  # Custom port

local_openai:
  enabled: true
  base_url: http://localhost:8081

local_gemini:
  enabled: true
  base_url: http://localhost:8082
```

Or via environment variables:

```bash
export CLAUDE_LOCAL_URL=http://localhost:8080
export OPENAI_LOCAL_URL=http://localhost:8081
export GEMINI_LOCAL_URL=http://localhost:8082
```

---

## Remote Servers (Not Just Localhost)

Connect to AI providers running on other machines:

```yaml
local_claude:
  enabled: true
  base_url: http://192.168.1.100:3000  # Remote machine

local_openai:
  enabled: true
  base_url: http://ai-server.local:3002  # DNS name
```

---

## Docker/Container Setup

Running local providers in Docker:

```bash
# Run your local AI provider in Docker
docker run -d -p 3000:3000 my-claude-server
docker run -d -p 3001:3001 my-gemini-server
docker run -d -p 3002:3002 my-openai-server

# Configure Agentix
agentix init
```

Update `.agent/config.yaml`:
```yaml
local_claude:
  enabled: true
  base_url: http://localhost:3000  # Maps to Docker container
```

---

## Checking Active Providers

See which providers Agentix detected:

```bash
agentix status
```

Output:
```
✓ Initialized 3 AI providers
  - local_claude (http://localhost:3000)
  - local_gemini (http://localhost:3001)
  - local_openai (http://localhost:3002)

Current project: /path/to/project
Spec: ✓ spec.md exists
Plan: ✓ plan.md exists
Tasks: ✓ tasks.md (2/5 completed)
```

---

## Best Practices

1. **Prefer Local Providers** - Enable local providers for cost-free usage
2. **Keep Fallbacks** - Enable remote providers as backup
3. **Test Connections** - Use `curl` to verify endpoints before configuring
4. **Monitor Performance** - Local providers should respond faster than remote APIs
5. **Secure Your Endpoints** - Use localhost or private networks only

---

## Example: Complete Local Setup

### Step 1: Start LiteLLM Proxies

```bash
# Terminal 1 - Claude proxy
litellm --model claude-3-5-sonnet-20241022 --port 3000 --api_key $ANTHROPIC_API_KEY

# Terminal 2 - Gemini proxy
litellm --model gemini/gemini-1.5-flash --port 3001 --api_key $GOOGLE_API_KEY

# Terminal 3 - OpenAI proxy
litellm --model gpt-4-turbo --port 3002 --api_key $OPENAI_API_KEY
```

### Step 2: Configure Agentix

Create `.agent/config.yaml`:
```yaml
providers:
  local_claude:
    enabled: true
    base_url: http://localhost:3000

  local_openai:
    enabled: true
    base_url: http://localhost:3002

  local_gemini:
    enabled: true
    base_url: http://localhost:3001

  # Disable remote (already proxied locally)
  claude:
    enabled: false
  openai:
    enabled: false
  gemini:
    enabled: false
```

### Step 3: Use Agentix

```bash
agentix specify "Build a URL shortener API"
agentix plan
agentix tasks
agentix work
```

All requests now go through your local proxies! 🎉

---

## Architecture

```
┌─────────────┐
│   Agentix   │
└─────┬───────┘
      │
      ├─── HTTP ───→ local_claude (localhost:3000)
      ├─── HTTP ───→ local_openai (localhost:3002)
      └─── HTTP ───→ local_gemini (localhost:3001)
```

Each local provider:
1. Receives OpenAI-compatible requests from Agentix
2. Processes them using local AI instance
3. Returns OpenAI-compatible responses

---

## FAQ

**Q: Do I need API keys for local providers?**
A: No! Local providers connect via HTTP without API keys.

**Q: Can I use both local and remote providers?**
A: Yes! Agentix will prefer local providers when available and fall back to remote APIs.

**Q: What if my local provider goes down?**
A: Agentix will automatically fall back to the next available provider (remote APIs if configured).

**Q: Can I use custom models with local providers?**
A: Yes! Set `default_model` in config to any model your local provider supports.

**Q: Is this compatible with Cline/Roo Code/Kilo Code?**
A: Yes! If those tools expose OpenAI-compatible HTTP APIs, Agentix can connect to them.

**Q: How do I know which provider was used?**
A: Agentix logs the provider used for each task: `✓ Used AI provider: local_claude`

---

## Next Steps

- ✅ Set up local providers following this guide
- ✅ Test with `agentix specify "test task"`
- ✅ Configure task routing preferences
- ✅ Disable remote providers if desired
- ✅ Enjoy free, fast, local AI coding!

For more information, see the [main README](README.md).
