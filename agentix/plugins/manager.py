"""
Plugin manager for discovering and managing plugins.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from .manifest import PluginManifest, PluginType
from .loader import PluginLoader


class PluginManager:
    """
    Manager for discovering, loading, and managing plugins.

    Features:
    - Auto-discovery from plugin directories
    - Plugin lifecycle management
    - Dependency resolution
    - Plugin isolation
    """

    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        """
        Initialize the plugin manager.

        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self._plugin_dirs = plugin_dirs or []
        self._loader = PluginLoader()
        self._plugins: Dict[str, tuple[PluginManifest, Any]] = {}
        self._logger = logging.getLogger(__name__)

    def add_plugin_dir(self, plugin_dir: Path):
        """
        Add a directory to search for plugins.

        Args:
            plugin_dir: Path to plugin directory
        """
        if plugin_dir not in self._plugin_dirs:
            self._plugin_dirs.append(plugin_dir)
            self._logger.info(f"Added plugin directory: {plugin_dir}")

    def discover_plugins(self) -> List[PluginManifest]:
        """
        Discover all plugins in configured directories.

        Returns:
            List of discovered plugin manifests
        """
        discovered = []

        for plugin_dir in self._plugin_dirs:
            if not plugin_dir.exists():
                self._logger.warning(f"Plugin directory not found: {plugin_dir}")
                continue

            # Each subdirectory is a potential plugin
            for item in plugin_dir.iterdir():
                if item.is_dir():
                    # Try to load manifest
                    for manifest_file in ['plugin.yaml', 'plugin.yml', 'plugin.json']:
                        manifest_path = item / manifest_file
                        if manifest_path.exists():
                            try:
                                manifest = PluginManifest.from_file(manifest_path)
                                discovered.append(manifest)
                                self._logger.debug(f"Discovered plugin: {manifest.name}")
                                break
                            except Exception as e:
                                self._logger.error(f"Error loading manifest from {manifest_path}: {e}")

        self._logger.info(f"Discovered {len(discovered)} plugins")
        return discovered

    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a specific plugin by name.

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            True if loaded successfully
        """
        # Find the plugin directory
        plugin_dir = self._find_plugin_dir(plugin_name)
        if plugin_dir is None:
            self._logger.error(f"Plugin '{plugin_name}' not found")
            return False

        # Load the plugin
        result = self._loader.load_plugin(plugin_dir)
        if result is None:
            return False

        manifest, plugin_instance = result
        self._plugins[plugin_name] = (manifest, plugin_instance)

        self._logger.info(f"Loaded plugin '{plugin_name}'")
        return True

    def load_all_plugins(self) -> int:
        """
        Load all discovered plugins.

        Returns:
            Number of plugins loaded
        """
        discovered = self.discover_plugins()
        loaded_count = 0

        for manifest in discovered:
            if self.load_plugin(manifest.name):
                loaded_count += 1

        self._logger.info(f"Loaded {loaded_count}/{len(discovered)} plugins")
        return loaded_count

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if unloaded successfully
        """
        if plugin_name not in self._plugins:
            return False

        # Remove from our registry
        del self._plugins[plugin_name]

        # Unload from loader
        self._loader.unload_plugin(plugin_name)

        self._logger.info(f"Unloaded plugin '{plugin_name}'")
        return True

    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """
        Get a loaded plugin instance.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin instance or None
        """
        if plugin_name in self._plugins:
            return self._plugins[plugin_name][1]
        return None

    def get_manifest(self, plugin_name: str) -> Optional[PluginManifest]:
        """
        Get a plugin's manifest.

        Args:
            plugin_name: Plugin name

        Returns:
            PluginManifest or None
        """
        if plugin_name in self._plugins:
            return self._plugins[plugin_name][0]
        return None

    def list_plugins(self, plugin_type: Optional[PluginType] = None,
                     enabled_only: bool = False) -> List[str]:
        """
        List loaded plugin names.

        Args:
            plugin_type: Filter by plugin type
            enabled_only: Only list enabled plugins

        Returns:
            List of plugin names
        """
        names = []

        for name, (manifest, _) in self._plugins.items():
            if plugin_type and manifest.plugin_type != plugin_type:
                continue

            if enabled_only and not manifest.enabled:
                continue

            names.append(name)

        return names

    def is_loaded(self, plugin_name: str) -> bool:
        """
        Check if a plugin is loaded.

        Args:
            plugin_name: Plugin name

        Returns:
            True if loaded
        """
        return plugin_name in self._plugins

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            True if enabled successfully
        """
        manifest = self.get_manifest(plugin_name)
        if manifest is None:
            return False

        manifest.enabled = True
        self._logger.info(f"Enabled plugin '{plugin_name}'")
        return True

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            True if disabled successfully
        """
        manifest = self.get_manifest(plugin_name)
        if manifest is None:
            return False

        manifest.enabled = False
        self._logger.info(f"Disabled plugin '{plugin_name}'")
        return True

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            Dictionary of plugin information
        """
        if plugin_name not in self._plugins:
            return None

        manifest, _ = self._plugins[plugin_name]

        return {
            "name": manifest.name,
            "version": manifest.version,
            "type": manifest.plugin_type.value,
            "description": manifest.description,
            "author": manifest.author,
            "enabled": manifest.enabled,
            "loaded": True,
        }

    def _find_plugin_dir(self, plugin_name: str) -> Optional[Path]:
        """
        Find the directory for a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            Path to plugin directory or None
        """
        for base_dir in self._plugin_dirs:
            if not base_dir.exists():
                continue

            for item in base_dir.iterdir():
                if item.is_dir():
                    # Check if this directory contains the plugin
                    for manifest_file in ['plugin.yaml', 'plugin.yml', 'plugin.json']:
                        manifest_path = item / manifest_file
                        if manifest_path.exists():
                            try:
                                manifest = PluginManifest.from_file(manifest_path)
                                if manifest.name == plugin_name:
                                    return item
                            except Exception:
                                pass

        return None

    def __repr__(self) -> str:
        """String representation."""
        return f"PluginManager(plugins={len(self._plugins)}, dirs={len(self._plugin_dirs)})"


# Global plugin manager instance
_global_manager: Optional[PluginManager] = None


def get_global_manager() -> PluginManager:
    """
    Get the global plugin manager instance.

    Returns:
        The global PluginManager instance
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = PluginManager()
    return _global_manager


def reset_global_manager():
    """Reset the global manager (useful for testing)."""
    global _global_manager
    _global_manager = None
