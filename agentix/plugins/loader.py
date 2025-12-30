"""
Plugin loader for dynamic loading of plugins.
"""

import sys
import importlib.util
import logging
from pathlib import Path
from typing import Any, Optional

from .manifest import PluginManifest, PluginType


class PluginLoader:
    """
    Loader for dynamically loading plugins.

    Supports:
    - Loading plugins from directories
    - Importing plugin modules
    - Instantiating plugin classes
    - Validating plugin compatibility
    """

    def __init__(self):
        """Initialize the plugin loader."""
        self._logger = logging.getLogger(__name__)
        self._loaded_modules = {}

    def load_plugin(self, plugin_dir: Path) -> Optional[tuple[PluginManifest, Any]]:
        """
        Load a plugin from a directory.

        Args:
            plugin_dir: Path to the plugin directory

        Returns:
            Tuple of (manifest, plugin_instance) or None if loading failed
        """
        if not plugin_dir.is_dir():
            self._logger.error(f"Plugin directory not found: {plugin_dir}")
            return None

        # Find and load manifest
        manifest = self._load_manifest(plugin_dir)
        if manifest is None:
            return None

        # Validate manifest
        is_valid, error = manifest.validate()
        if not is_valid:
            self._logger.error(f"Invalid plugin manifest for '{manifest.name}': {error}")
            return None

        # Check if enabled
        if not manifest.enabled:
            self._logger.info(f"Plugin '{manifest.name}' is disabled, skipping")
            return None

        # Load the plugin module
        plugin_instance = self._load_module(plugin_dir, manifest)
        if plugin_instance is None:
            return None

        self._logger.info(f"Loaded plugin '{manifest.name}' v{manifest.version}")
        return manifest, plugin_instance

    def _load_manifest(self, plugin_dir: Path) -> Optional[PluginManifest]:
        """
        Load plugin manifest from directory.

        Args:
            plugin_dir: Plugin directory

        Returns:
            PluginManifest or None if not found
        """
        # Try different manifest filenames
        for filename in ['plugin.yaml', 'plugin.yml', 'plugin.json']:
            manifest_path = plugin_dir / filename
            if manifest_path.exists():
                try:
                    return PluginManifest.from_file(manifest_path)
                except Exception as e:
                    self._logger.exception(f"Error loading manifest from {manifest_path}: {e}")
                    return None

        self._logger.error(f"No manifest file found in {plugin_dir}")
        return None

    def _load_module(self, plugin_dir: Path, manifest: PluginManifest) -> Optional[Any]:
        """
        Load and instantiate the plugin module.

        Args:
            plugin_dir: Plugin directory
            manifest: Plugin manifest

        Returns:
            Plugin instance or None if loading failed
        """
        try:
            # Parse entry point (format: "module:ClassName" or "module")
            parts = manifest.entry_point.split(":")
            module_name = parts[0]
            class_name = parts[1] if len(parts) > 1 else None

            # Find the module file
            module_path = plugin_dir / f"{module_name}.py"
            if not module_path.exists():
                # Try as a package
                module_path = plugin_dir / module_name / "__init__.py"
                if not module_path.exists():
                    self._logger.error(f"Module file not found: {module_name}")
                    return None

            # Load the module
            spec = importlib.util.spec_from_file_location(
                f"agentix_plugin_{manifest.name}",
                module_path
            )
            if spec is None or spec.loader is None:
                self._logger.error(f"Failed to create module spec for {module_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            self._loaded_modules[manifest.name] = module

            # If a class name is specified, instantiate it
            if class_name:
                if not hasattr(module, class_name):
                    self._logger.error(f"Class '{class_name}' not found in module")
                    return None

                plugin_class = getattr(module, class_name)
                plugin_instance = plugin_class(config=manifest.config)
                return plugin_instance
            else:
                # Return the module itself
                return module

        except Exception as e:
            self._logger.exception(f"Error loading plugin module: {e}")
            return None

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if unloaded successfully
        """
        if plugin_name not in self._loaded_modules:
            return False

        # Remove from sys.modules
        module_name = f"agentix_plugin_{plugin_name}"
        if module_name in sys.modules:
            del sys.modules[module_name]

        del self._loaded_modules[plugin_name]
        self._logger.info(f"Unloaded plugin '{plugin_name}'")
        return True

    def is_loaded(self, plugin_name: str) -> bool:
        """
        Check if a plugin is loaded.

        Args:
            plugin_name: Plugin name

        Returns:
            True if loaded
        """
        return plugin_name in self._loaded_modules

    def get_module(self, plugin_name: str) -> Optional[Any]:
        """
        Get a loaded plugin module.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin module or None
        """
        return self._loaded_modules.get(plugin_name)
