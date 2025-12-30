"""
Agentix Plugin System

This module provides a plugin architecture for extending Agentix with:
- Custom tools
- Custom providers
- Custom commands
- Middleware and hooks
"""

from .manager import PluginManager
from .manifest import PluginManifest, PluginType
from .loader import PluginLoader

__all__ = [
    'PluginManager',
    'PluginManifest',
    'PluginType',
    'PluginLoader',
]

__version__ = '1.0.0'
