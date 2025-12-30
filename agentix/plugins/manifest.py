"""
Plugin manifest definitions.

Each plugin must have a manifest file (plugin.yaml or plugin.json)
that describes its metadata, dependencies, and capabilities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import yaml
import json
from pathlib import Path


class PluginType(Enum):
    """Types of plugins supported by Agentix."""
    TOOL = "tool"              # Adds new tools
    PROVIDER = "provider"      # Adds new AI providers
    COMMAND = "command"        # Adds new CLI commands
    MIDDLEWARE = "middleware"  # Adds hooks/middleware
    EXTENSION = "extension"    # General extension


@dataclass
class PluginManifest:
    """
    Plugin manifest containing metadata and configuration.

    Attributes:
        name: Unique plugin name
        version: Plugin version
        plugin_type: Type of plugin
        description: Human-readable description
        author: Plugin author
        homepage: Plugin homepage URL
        license: Plugin license
        agentix_version: Required Agentix version
        dependencies: List of required dependencies
        python_version: Required Python version
        entry_point: Main entry point module/class
        config: Plugin-specific configuration
        enabled: Whether the plugin is enabled
    """
    name: str
    version: str
    plugin_type: PluginType
    description: str = ""
    author: str = ""
    homepage: str = ""
    license: str = ""
    agentix_version: str = ">=1.0.0"
    dependencies: List[str] = field(default_factory=list)
    python_version: str = ">=3.8"
    entry_point: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "version": self.version,
            "type": self.plugin_type.value,
            "description": self.description,
            "author": self.author,
            "homepage": self.homepage,
            "license": self.license,
            "agentix_version": self.agentix_version,
            "dependencies": self.dependencies,
            "python_version": self.python_version,
            "entry_point": self.entry_point,
            "config": self.config,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginManifest':
        """Create from dictionary format."""
        plugin_type = data.get("type", "extension")
        if isinstance(plugin_type, str):
            plugin_type = PluginType(plugin_type)

        return cls(
            name=data["name"],
            version=data["version"],
            plugin_type=plugin_type,
            description=data.get("description", ""),
            author=data.get("author", ""),
            homepage=data.get("homepage", ""),
            license=data.get("license", ""),
            agentix_version=data.get("agentix_version", ">=1.0.0"),
            dependencies=data.get("dependencies", []),
            python_version=data.get("python_version", ">=3.8"),
            entry_point=data.get("entry_point", ""),
            config=data.get("config", {}),
            enabled=data.get("enabled", True),
        )

    @classmethod
    def from_file(cls, path: Path) -> 'PluginManifest':
        """
        Load manifest from a file.

        Args:
            path: Path to manifest file (YAML or JSON)

        Returns:
            PluginManifest instance

        Raises:
            ValueError: If file format is unsupported
            FileNotFoundError: If file doesn't exist
        """
        if not path.exists():
            raise FileNotFoundError(f"Manifest file not found: {path}")

        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported manifest format: {path.suffix}")

        return cls.from_dict(data)

    def to_file(self, path: Path):
        """
        Save manifest to a file.

        Args:
            path: Path to save manifest (YAML or JSON)
        """
        data = self.to_dict()

        with open(path, 'w') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.safe_dump(data, f, default_flow_style=False)
            elif path.suffix == '.json':
                json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported manifest format: {path.suffix}")

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate the manifest.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.name:
            return False, "Plugin name is required"

        if not self.version:
            return False, "Plugin version is required"

        if not self.entry_point:
            return False, "Entry point is required"

        return True, None

    def __repr__(self) -> str:
        """String representation."""
        return f"PluginManifest(name='{self.name}', version='{self.version}', type={self.plugin_type.value})"
