"""
Tool Registry for discovery and management.

The registry maintains a catalog of all available tools, whether they're:
- Built-in tools
- MCP tools from external servers
- Custom user-defined tools
"""

from typing import Dict, List, Optional, Set, Callable
import logging
from .base import Tool


class ToolRegistry:
    """
    Central registry for all tools available to Agentix.

    The registry supports:
    - Tool registration and discovery
    - Tool lookup by name
    - Filtering by tags, capabilities, or source
    - Allow/deny lists for security
    """

    def __init__(self, allow_list: Optional[List[str]] = None,
                 deny_list: Optional[List[str]] = None):
        """
        Initialize the tool registry.

        Args:
            allow_list: If provided, only tools in this list are allowed
            deny_list: Tools in this list are denied
        """
        self._tools: Dict[str, Tool] = {}
        self._tags: Dict[str, Set[str]] = {}  # tag -> set of tool names
        self._sources: Dict[str, str] = {}  # tool_name -> source
        self._allow_list = set(allow_list) if allow_list else None
        self._deny_list = set(deny_list) if deny_list else set()
        self._logger = logging.getLogger(__name__)

    def register(self, tool: Tool, source: str = "builtin",
                 tags: Optional[List[str]] = None) -> bool:
        """
        Register a tool with the registry.

        Args:
            tool: The tool instance to register
            source: Source of the tool (e.g., "builtin", "mcp:server_name", "custom")
            tags: Optional tags for categorization

        Returns:
            True if registration succeeded, False otherwise
        """
        if not self._is_allowed(tool.name):
            self._logger.warning(f"Tool '{tool.name}' is not allowed (blocked by allow/deny list)")
            return False

        if tool.name in self._tools:
            self._logger.warning(f"Tool '{tool.name}' is already registered, replacing")

        self._tools[tool.name] = tool
        self._sources[tool.name] = source

        # Register tags
        if tags:
            for tag in tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(tool.name)

        self._logger.info(f"Registered tool '{tool.name}' from source '{source}'")
        return True

    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool from the registry.

        Args:
            tool_name: Name of the tool to unregister

        Returns:
            True if unregistration succeeded, False if tool wasn't found
        """
        if tool_name not in self._tools:
            return False

        # Remove from tools
        del self._tools[tool_name]

        # Remove from sources
        if tool_name in self._sources:
            del self._sources[tool_name]

        # Remove from tags
        for tag_set in self._tags.values():
            tag_set.discard(tool_name)

        self._logger.info(f"Unregistered tool '{tool_name}'")
        return True

    def get(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            The tool instance, or None if not found
        """
        return self._tools.get(tool_name)

    def list_tools(self, tag: Optional[str] = None,
                   source: Optional[str] = None) -> List[Tool]:
        """
        List all registered tools, optionally filtered by tag or source.

        Args:
            tag: If provided, only return tools with this tag
            source: If provided, only return tools from this source

        Returns:
            List of tool instances
        """
        tools = list(self._tools.values())

        if tag:
            tool_names = self._tags.get(tag, set())
            tools = [t for t in tools if t.name in tool_names]

        if source:
            tools = [t for t in tools if self._sources.get(t.name) == source]

        return tools

    def list_names(self, tag: Optional[str] = None,
                   source: Optional[str] = None) -> List[str]:
        """
        List names of all registered tools.

        Args:
            tag: If provided, only return tools with this tag
            source: If provided, only return tools from this source

        Returns:
            List of tool names
        """
        return [t.name for t in self.list_tools(tag=tag, source=source)]

    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            tool_name: Name of the tool

        Returns:
            True if the tool is registered, False otherwise
        """
        return tool_name in self._tools

    def get_source(self, tool_name: str) -> Optional[str]:
        """
        Get the source of a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            The source string, or None if tool not found
        """
        return self._sources.get(tool_name)

    def get_tags(self, tool_name: str) -> List[str]:
        """
        Get all tags associated with a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            List of tags
        """
        return [tag for tag, names in self._tags.items() if tool_name in names]

    def list_sources(self) -> List[str]:
        """
        List all unique sources.

        Returns:
            List of source names
        """
        return list(set(self._sources.values()))

    def list_tags(self) -> List[str]:
        """
        List all unique tags.

        Returns:
            List of tag names
        """
        return list(self._tags.keys())

    def clear(self, source: Optional[str] = None):
        """
        Clear tools from the registry.

        Args:
            source: If provided, only clear tools from this source.
                   If None, clear all tools.
        """
        if source is None:
            self._tools.clear()
            self._sources.clear()
            self._tags.clear()
            self._logger.info("Cleared all tools from registry")
        else:
            # Find tools from this source
            tools_to_remove = [
                name for name, src in self._sources.items()
                if src == source
            ]

            for name in tools_to_remove:
                self.unregister(name)

            self._logger.info(f"Cleared {len(tools_to_remove)} tools from source '{source}'")

    def count(self, source: Optional[str] = None) -> int:
        """
        Count the number of registered tools.

        Args:
            source: If provided, only count tools from this source

        Returns:
            Number of tools
        """
        if source is None:
            return len(self._tools)

        return sum(1 for src in self._sources.values() if src == source)

    def _is_allowed(self, tool_name: str) -> bool:
        """
        Check if a tool is allowed based on allow/deny lists.

        Args:
            tool_name: Name of the tool

        Returns:
            True if allowed, False if denied
        """
        # Check deny list first
        if tool_name in self._deny_list:
            return False

        # If there's an allow list, check it
        if self._allow_list is not None:
            return tool_name in self._allow_list

        # No restrictions
        return True

    def to_dict(self) -> Dict:
        """
        Export registry state to dictionary.

        Returns:
            Dictionary representation of the registry
        """
        return {
            "tools": {
                name: {
                    "definition": tool.to_dict(),
                    "source": self._sources.get(name),
                    "tags": self.get_tags(name),
                }
                for name, tool in self._tools.items()
            },
            "stats": {
                "total_tools": len(self._tools),
                "sources": self.list_sources(),
                "tags": self.list_tags(),
            }
        }

    def __repr__(self) -> str:
        """String representation of the registry."""
        return f"ToolRegistry(tools={len(self._tools)}, sources={len(self.list_sources())})"


# Global registry instance
_global_registry: Optional[ToolRegistry] = None


def get_global_registry() -> ToolRegistry:
    """
    Get the global tool registry instance.

    Returns:
        The global ToolRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def reset_global_registry():
    """Reset the global registry (useful for testing)."""
    global _global_registry
    _global_registry = None
