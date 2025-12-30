# MCP and Plugin Support for Agentix

This document describes the Model Context Protocol (MCP) and plugin system support added to Agentix.

## 🔧 Tool System

Agentix now includes a comprehensive tool system that allows AI models to interact with external tools and services.

### Built-in Tools

The following tools are available out of the box:

- **file_read** - Read file contents from the filesystem
- **file_write** - Write content to files
- **file_list** - List files in a directory (with recursive option)
- **shell_execute** - Execute shell commands safely with timeout

### Tool Management Commands

```bash
# List all available tools
agentix tools list

# Add an MCP server
agentix tools add

# Remove an MCP server
agentix tools remove

# List configured MCP servers
agentix tools servers

# Test a tool execution
agentix tools test
```

## 📡 MCP (Model Context Protocol) Support

Agentix now supports the Model Context Protocol, allowing it to connect to external MCP servers and discover their tools dynamically.

### What is MCP?

Model Context Protocol is a standard protocol for connecting AI applications to external tools and data sources. It allows:

- Dynamic tool discovery
- Standardized tool invocation
- Multiple transport mechanisms (stdio, HTTP, SSE)
- Secure communication with external services

### Adding an MCP Server

Interactive mode:
```bash
agentix tools add
```

You'll be prompted for:
1. Server name (unique identifier)
2. Transport type (stdio, http, or sse)
3. Command and arguments (for stdio)
4. URL (for http/sse)
5. Environment variables (optional)

### Example: Adding an MCP Server via stdio

```bash
$ agentix tools add

Server name: filesystem
Transport type: stdio
Command: npx
Arguments: @modelcontextprotocol/server-filesystem /path/to/allow
```

### MCP Configuration

MCP settings are stored in `.agent/config.yaml`:

```yaml
mcp:
  enabled: true
  auto_discover: true
  timeout: 30
  servers:
    - name: filesystem
      transport: stdio
      command: npx
      args:
        - "@modelcontextprotocol/server-filesystem"
        - "/path/to/allow"
      enabled: true
```

### Available MCP Servers

The MCP ecosystem includes many community-built servers:

- **@modelcontextprotocol/server-filesystem** - File system operations
- **@modelcontextprotocol/server-github** - GitHub API integration
- **@modelcontextprotocol/server-postgres** - PostgreSQL database access
- **@modelcontextprotocol/server-brave-search** - Web search via Brave
- **@modelcontextprotocol/server-google-maps** - Google Maps integration
- And many more...

Check the [MCP Server Registry](https://github.com/modelcontextprotocol/servers) for more.

## 🔌 Plugin System

Agentix now supports a plugin architecture for extending functionality.

### Plugin Types

Plugins can extend Agentix in various ways:

- **tool** - Add new tools
- **provider** - Add new AI providers
- **command** - Add new CLI commands
- **middleware** - Add hooks and middleware
- **extension** - General-purpose extensions

### Plugin Structure

A plugin is a directory containing:

```
my-plugin/
├── plugin.yaml          # Plugin manifest
├── main.py             # Entry point
└── README.md           # Documentation (optional)
```

### Plugin Manifest (plugin.yaml)

```yaml
name: my-plugin
version: 1.0.0
type: tool
description: My custom tool plugin
author: Your Name
homepage: https://github.com/yourname/my-plugin
license: MIT
agentix_version: ">=1.0.0"
dependencies: []
python_version: ">=3.8"
entry_point: "main:MyPlugin"
enabled: true
config:
  custom_setting: value
```

### Creating a Plugin

1. Create plugin directory:
```bash
mkdir -p ~/.agentix/plugins/my-plugin
cd ~/.agentix/plugins/my-plugin
```

2. Create `plugin.yaml` (see example above)

3. Create `main.py`:
```python
from agentix.tools import Tool, ToolParameter, ToolResult, ToolParameterType

class MyCustomTool(Tool):
    @property
    def name(self) -> str:
        return "my_custom_tool"

    @property
    def description(self) -> str:
        return "Description of what my tool does"

    @property
    def parameters(self):
        return [
            ToolParameter(
                name="input",
                type=ToolParameterType.STRING,
                description="Input parameter",
                required=True
            )
        ]

    def execute(self, **kwargs) -> ToolResult:
        input_value = kwargs["input"]
        # Your tool logic here
        return ToolResult(
            success=True,
            data={"output": f"Processed: {input_value}"}
        )

class MyPlugin:
    def __init__(self, config=None):
        self.config = config or {}
        self.tool = MyCustomTool()

    def get_tools(self):
        return [self.tool]
```

### Plugin Management Commands

```bash
# List installed plugins
agentix plugins list

# Discover available plugins
agentix plugins discover

# Enable a plugin
agentix plugins enable my-plugin

# Disable a plugin
agentix plugins disable my-plugin
```

### Plugin Directories

Plugins are discovered in these directories:
- `~/.agentix/plugins/` - Global plugins
- `.agentix/plugins/` - Project-specific plugins

You can configure additional plugin directories in `config.yaml`:

```yaml
plugins:
  enabled: true
  auto_load: true
  directories:
    - "~/.agentix/plugins"
    - ".agentix/plugins"
    - "/path/to/custom/plugins"
```

## 🎯 Use Cases

### 1. File System Operations via MCP

```bash
# Add filesystem MCP server
agentix tools add
# Server: filesystem
# Command: npx @modelcontextprotocol/server-filesystem /home/user/projects

# Now AI models can read/write files through MCP
agentix specify "Create a data analysis script that reads CSV files"
```

### 2. GitHub Integration

```bash
# Add GitHub MCP server
agentix tools add
# Server: github
# Command: npx @modelcontextprotocol/server-github
# Env: GITHUB_TOKEN=your_token

# Now AI can interact with GitHub
agentix specify "Create an issue for the bug in authentication.py"
```

### 3. Custom Business Tools via Plugins

Create a plugin that exposes your company's internal APIs or databases to AI models.

## 🔒 Security Considerations

### Tool Allow/Deny Lists

Control which tools can be used:

```yaml
tools:
  enabled: true
  allow_list: []  # If set, only these tools are allowed
  deny_list:      # These tools are always denied
    - shell_execute  # Dangerous tools
```

### MCP Server Permissions

- Only run trusted MCP servers
- Use allow/deny lists for file paths
- Set appropriate timeouts
- Review server source code before using

### Plugin Security

- Only install plugins from trusted sources
- Review plugin code before installation
- Plugins run in the same process (no sandboxing yet)
- Use plugin enable/disable to control what runs

## 📊 Tool Execution

### Timeout Configuration

```yaml
tools:
  default_timeout: 30  # seconds
```

### Execution Metrics

Tool execution is tracked with metrics:
- Total executions
- Success rate
- Average execution time
- Failed executions

View metrics programmatically:
```python
tool_manager.executor.get_metrics()
```

## 🔄 Architecture

### Components

```
agentix/
├── tools/
│   ├── base.py           # Tool abstractions
│   ├── registry.py       # Tool registry
│   ├── executor.py       # Safe tool execution
│   ├── mcp_client.py     # MCP protocol client
│   ├── builtin_tools.py  # Built-in tools
│   └── manager.py        # Tool manager coordinator
├── plugins/
│   ├── manifest.py       # Plugin manifest
│   ├── loader.py         # Dynamic plugin loading
│   └── manager.py        # Plugin manager
```

### Tool Lifecycle

1. **Registration** - Tools are registered in the ToolRegistry
2. **Discovery** - MCP servers are connected and tools discovered
3. **Validation** - Parameters are validated before execution
4. **Execution** - Tools run with timeout and error handling
5. **Result** - Standardized ToolResult returned

### Plugin Lifecycle

1. **Discovery** - Plugins found in configured directories
2. **Loading** - Plugin manifest read and validated
3. **Initialization** - Plugin module imported and instantiated
4. **Registration** - Plugin tools/providers registered
5. **Execution** - Plugin components used by Agentix

## 🚀 Getting Started

### Quick Start with MCP

1. Install an MCP server:
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

2. Add it to Agentix:
```bash
agentix tools add
```

3. List available tools:
```bash
agentix tools list
```

4. Use tools in your workflow:
```bash
agentix specify "Build a file analyzer that scans Python files"
```

### Quick Start with Plugins

1. Create a plugin directory:
```bash
mkdir -p ~/.agentix/plugins/my-tool
```

2. Add `plugin.yaml` and `main.py` (see examples above)

3. Discover and enable:
```bash
agentix plugins discover
agentix plugins enable my-tool
```

4. Use your plugin:
```bash
agentix tools list  # Should see your tool
```

## 📝 Configuration Reference

### Complete MCP/Tools Configuration

```yaml
mcp:
  enabled: true
  auto_discover: true
  timeout: 30
  servers:
    - name: example
      transport: stdio
      command: npx
      args: ["@modelcontextprotocol/server-example"]
      env:
        API_KEY: your_key
      enabled: true

tools:
  enabled: true
  builtin_enabled: true
  allow_list: []
  deny_list: []
  default_timeout: 30

plugins:
  enabled: true
  auto_load: true
  directories:
    - "~/.agentix/plugins"
    - ".agentix/plugins"
```

## 🆘 Troubleshooting

### Tools not showing up

1. Check if tools are enabled:
```bash
grep "enabled" .agent/config.yaml
```

2. List MCP servers:
```bash
agentix tools servers
```

3. Check logs for connection errors

### Plugin not loading

1. Verify plugin manifest:
```bash
cat ~/.agentix/plugins/my-plugin/plugin.yaml
```

2. Check plugin is discovered:
```bash
agentix plugins discover
```

3. Enable the plugin:
```bash
agentix plugins enable my-plugin
```

### MCP server connection fails

1. Verify command works standalone:
```bash
npx @modelcontextprotocol/server-filesystem --help
```

2. Check environment variables are set
3. Review server logs
4. Verify network connectivity (for HTTP/SSE)

## 🔮 Future Enhancements

Planned improvements:
- [ ] Plugin sandboxing for security
- [ ] HTTP/SSE transport support for MCP
- [ ] Tool composition (tools calling tools)
- [ ] Remote plugin repositories
- [ ] Tool usage analytics dashboard
- [ ] AI model tool selection optimization
- [ ] Tool result caching

## 📚 Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [Agentix Documentation](README.md)
- [Plugin Development Guide](docs/plugin-development.md)

## 🤝 Contributing

To contribute MCP servers or plugins:

1. Fork the repository
2. Create your feature branch
3. Add tests
4. Submit a pull request

For MCP servers, consider publishing to npm and the MCP registry.

---

**Note**: This is an experimental feature. APIs may change in future versions. Always backup your data before using new tools or plugins.
