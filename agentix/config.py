import os
import yaml
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "max_context_files": 10,
    "auto_commit": False,
    "require_confirmation": True,
    "temperature": 0.7,
    "max_tokens": 4096,
    "logging": {
        "enabled": True,
        "level": "INFO",
        "save_history": True
    },
    "providers": {
        # Configure any/all providers - use 1 or use them all!

        # CLI PROVIDERS (No API keys needed - use authenticated CLI tools)
        "claude_cli": {
            "enabled": False,  # Set to True to use Claude CLI (after `claude login`)
            "default_model": "claude-3-5-sonnet-20241022"
        },
        "openai_cli": {
            "enabled": False,  # Set to True to use OpenAI CLI (after authentication)
            "default_model": "gpt-4-turbo"
        },
        "gemini_cli": {
            "enabled": False,  # Set to True to use Gemini CLI (after `gcloud auth login`)
            "default_model": "gemini-1.5-flash"
        },

        # API PROVIDERS (Require API keys)
        "claude": {
            "enabled": True,
            "api_key": None,  # Uses ANTHROPIC_API_KEY env var if not set
            "default_model": "claude-sonnet-4-20250514"  # Latest Sonnet 4 (Dec 2025)
        },
        "openai": {
            "enabled": True,
            "api_key": None,  # Uses OPENAI_API_KEY env var if not set
            "default_model": "gpt-4o"  # Latest GPT-4o (Dec 2025)
        },
        "gemini": {
            "enabled": True,
            "api_key": None,  # Uses GOOGLE_API_KEY env var if not set
            "default_model": "gemini-2.0-flash-exp"  # Gemini 2.0 (Dec 2025)
        },
        "openrouter": {
            "enabled": False,  # Set to True to use OpenRouter
            "api_key": None,  # Uses OPENROUTER_API_KEY env var if not set
            "default_model": "anthropic/claude-sonnet-4-20250514",  # Latest via OpenRouter
            "site_url": None,  # Optional: your site URL
            "site_name": None  # Optional: your app name
        },
        "ollama": {
            "enabled": False,  # Set to True to use Ollama (local models)
            "base_url": None,  # Uses OLLAMA_HOST env var, defaults to http://localhost:11434
            "default_model": "codellama"
        },
        "routing": {
            "strategy": "intelligent",  # intelligent | preferred | round_robin
            "preferred_provider": None,  # Set to force a specific provider
            "task_routing": {
                # CLI providers preferred when available (use authenticated tools, no API costs)
                "specification": "claude_cli",  # Best for specs
                "planning": "claude_cli",  # Best for planning
                "tasks": "claude_cli",  # Best for task breakdown
                "code_generation": "openai_cli",  # Codex excellence
                "task_execution": "gemini_cli",  # Fast execution
                "refactoring": "claude_cli",  # Best code understanding
                "review": "claude_cli",  # Best analysis
                "cli": "claude_cli",  # For CLI tool usage
                "cost_effective": "claude_cli"  # Free CLI providers
            }
        }
    },
    "shared_context": {
        "enabled": False,  # Enable multi-model collaboration
        "max_tokens": 200000,  # Max context to maintain
        "save_snapshots": True  # Save context snapshots
    },
    "mcp": {
        "enabled": True,  # Enable MCP (Model Context Protocol) support
        "auto_discover": True,  # Automatically discover tools from MCP servers
        "timeout": 30,  # Default timeout for MCP operations (seconds)
        "servers": []  # MCP servers configuration (added via agentix tools add)
    },
    "tools": {
        "enabled": True,  # Enable tool system
        "builtin_enabled": True,  # Enable built-in tools (file_read, file_write, etc.)
        "allow_list": [],  # If set, only these tools are allowed (empty = allow all)
        "deny_list": [],  # Tools in this list are denied
        "default_timeout": 30  # Default timeout for tool execution (seconds)
    },
    "plugins": {
        "enabled": True,  # Enable plugin system
        "auto_load": True,  # Automatically load plugins on startup
        "directories": ["~/.agentix/plugins", ".agentix/plugins"]  # Plugin search paths
    },
    "prompts": {
        "specify": "You are a product manager. Generate a functional specification (spec.md) based on the user's goal and codebase context. Focus on 'what' and 'why'. Use sections: Goal, User Stories, Acceptance Criteria, Edge Cases.",
        "plan": "You are a software architect. Generate a technical implementation plan (plan.md) based on the functional specification and codebase context. Focus on 'how'. Use sections: Architecture Overview, File Changes, Dependencies, Testing Strategy.",
        "tasks": """You are a technical lead. Break the technical plan into atomic, executable tasks.
Output a Markdown file with a YAML block at the top.
The YAML block must follow this structure:
---yaml
tasks:
  - id: 1
    description: "Short description"
    status: pending
    action: create_file | edit_file | delete_file | run_command
    path: "path/to/file"
    context_files: []
---
Followed by a human-readable checklist.""",
        "work": "You are a senior developer. Execute the following task: {description}. Action: {action} on {path}. Output ONLY the full content of the file after the change. No markdown blocks, no explanation."
    }
}

class Config:
    def __init__(self, agent_dir: str):
        self.agent_dir = agent_dir
        self.config_path = os.path.join(agent_dir, "config.yaml")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    user_config = yaml.safe_load(f) or {}
                return self._merge_config(DEFAULT_CONFIG, user_config)
            except Exception as e:
                print(f"Warning: Could not load config.yaml: {e}")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user config with defaults."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def save(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
            print(f"Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Set a configuration value using dot notation."""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_temperature(self) -> float:
        """Get the temperature for AI completions."""
        return float(os.getenv("AGENT_TEMPERATURE", self.get("temperature", 0.7)))

    def get_max_tokens(self) -> int:
        """Get the max tokens for AI completions."""
        return int(os.getenv("AGENT_MAX_TOKENS", self.get("max_tokens", 4096)))

    def get_prompt(self, prompt_type: str) -> Optional[str]:
        """Get a system prompt by type."""
        return self.get(f"prompts.{prompt_type}")

    def should_confirm(self) -> bool:
        """Check if user confirmation is required."""
        return self.get("require_confirmation", True)

    def should_auto_commit(self) -> bool:
        """Check if auto-commit is enabled."""
        return self.get("auto_commit", False)

    def is_logging_enabled(self) -> bool:
        """Check if logging is enabled."""
        return self.get("logging.enabled", True)

    def get_log_level(self) -> str:
        """Get the logging level."""
        return self.get("logging.level", "INFO")

    def should_save_history(self) -> bool:
        """Check if history should be saved."""
        return self.get("logging.save_history", True)

    def create_default_config(self):
        """Create a default config.yaml file."""
        self.config = DEFAULT_CONFIG.copy()
        self.save()

    def get_providers_config(self) -> Dict[str, Any]:
        """Get providers configuration."""
        return self.get("providers", DEFAULT_CONFIG["providers"])

    def get_routing_strategy(self) -> str:
        """Get the routing strategy."""
        return self.get("providers.routing.strategy", "intelligent")

    def get_preferred_provider(self) -> Optional[str]:
        """Get the preferred provider if set."""
        return self.get("providers.routing.preferred_provider")

    def get_task_routing(self, task_type: str) -> Optional[str]:
        """Get the preferred provider for a specific task type."""
        return self.get(f"providers.routing.task_routing.{task_type}")

    def is_provider_enabled(self, provider_name: str) -> bool:
        """Check if a provider is enabled."""
        return self.get(f"providers.{provider_name}.enabled", False)

    # MCP Configuration
    def is_mcp_enabled(self) -> bool:
        """Check if MCP support is enabled."""
        return self.get("mcp.enabled", True)

    def should_auto_discover_tools(self) -> bool:
        """Check if tools should be auto-discovered from MCP servers."""
        return self.get("mcp.auto_discover", True)

    def get_mcp_timeout(self) -> int:
        """Get MCP operation timeout in seconds."""
        return self.get("mcp.timeout", 30)

    def get_mcp_servers(self) -> list:
        """Get configured MCP servers."""
        return self.get("mcp.servers", [])

    def add_mcp_server(self, server_config: Dict[str, Any]):
        """Add an MCP server configuration."""
        servers = self.get_mcp_servers()
        servers.append(server_config)
        self.set("mcp.servers", servers)

    def remove_mcp_server(self, server_name: str) -> bool:
        """Remove an MCP server by name."""
        servers = self.get_mcp_servers()
        filtered = [s for s in servers if s.get("name") != server_name]
        if len(filtered) < len(servers):
            self.set("mcp.servers", filtered)
            return True
        return False

    # Tools Configuration
    def is_tools_enabled(self) -> bool:
        """Check if the tool system is enabled."""
        return self.get("tools.enabled", True)

    def is_builtin_tools_enabled(self) -> bool:
        """Check if built-in tools are enabled."""
        return self.get("tools.builtin_enabled", True)

    def get_tools_allow_list(self) -> list:
        """Get the tools allow list."""
        return self.get("tools.allow_list", [])

    def get_tools_deny_list(self) -> list:
        """Get the tools deny list."""
        return self.get("tools.deny_list", [])

    def get_tools_timeout(self) -> int:
        """Get default tool execution timeout."""
        return self.get("tools.default_timeout", 30)

    # Plugins Configuration
    def is_plugins_enabled(self) -> bool:
        """Check if plugins are enabled."""
        return self.get("plugins.enabled", True)

    def should_auto_load_plugins(self) -> bool:
        """Check if plugins should auto-load on startup."""
        return self.get("plugins.auto_load", True)

    def get_plugin_directories(self) -> list:
        """Get plugin search directories."""
        dirs = self.get("plugins.directories", ["~/.agentix/plugins", ".agentix/plugins"])
        # Expand user paths
        return [os.path.expanduser(d) for d in dirs]
