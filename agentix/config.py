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
        "claude": {
            "enabled": True,
            "api_key": None,  # Uses ANTHROPIC_API_KEY env var if not set
            "default_model": "claude-3-5-sonnet-20241022"
        },
        "openai": {
            "enabled": True,
            "api_key": None,  # Uses OPENAI_API_KEY env var if not set
            "default_model": "gpt-4.1-mini"
        },
        "gemini": {
            "enabled": True,
            "api_key": None,  # Uses GOOGLE_API_KEY env var if not set
            "default_model": "gemini-1.5-flash"
        },
        "routing": {
            "strategy": "intelligent",  # intelligent | preferred | round_robin
            "preferred_provider": None,  # Set to force a specific provider
            "task_routing": {
                "specification": "claude",  # Best for specs
                "planning": "claude",  # Best for planning
                "tasks": "claude",  # Best for task breakdown
                "code_generation": "openai",  # Codex excellence
                "task_execution": "gemini",  # Fast execution
                "refactoring": "claude",  # Best code understanding
                "review": "claude"  # Best analysis
            }
        }
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
