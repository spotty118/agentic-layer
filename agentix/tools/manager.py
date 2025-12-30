"""
Tool Manager - Coordinates the tool system components.

The manager brings together:
- Tool registry
- Tool executor
- MCP client
- Built-in tools
"""

import logging
from pathlib import Path
from typing import Optional

from .registry import ToolRegistry
from .executor import ToolExecutor
from .mcp_client import MCPClient, MCPServer
from .builtin_tools import get_builtin_tools


class ToolManager:
    """
    Central manager for the tool system.

    Coordinates:
    - Tool registration (built-in and MCP)
    - Tool execution
    - MCP server connections
    """

    def __init__(self, config=None):
        """
        Initialize the tool manager.

        Args:
            config: Configuration object (optional)
        """
        self._config = config
        self._logger = logging.getLogger(__name__)

        # Initialize components
        allow_list = config.get_tools_allow_list() if config else []
        deny_list = config.get_tools_deny_list() if config else []
        timeout = config.get_tools_timeout() if config else 30

        self.registry = ToolRegistry(allow_list=allow_list, deny_list=deny_list)
        self.executor = ToolExecutor(registry=self.registry, default_timeout=timeout)
        self.mcp_client = MCPClient()

        # Initialize built-in tools if enabled
        if not config or config.is_builtin_tools_enabled():
            self._register_builtin_tools()

        # Initialize MCP servers if configured
        if config and config.is_mcp_enabled():
            self._initialize_mcp_servers()

    def _register_builtin_tools(self):
        """Register built-in tools."""
        builtin_tools = get_builtin_tools()
        for tool in builtin_tools:
            self.registry.register(tool, source="builtin", tags=["builtin"])

        self._logger.info(f"Registered {len(builtin_tools)} built-in tools")

    def _initialize_mcp_servers(self):
        """Initialize configured MCP servers."""
        if not self._config:
            return

        servers = self._config.get_mcp_servers()
        for server_config in servers:
            try:
                server = MCPServer.from_dict(server_config)
                self.mcp_client.add_server(server)

                # Connect if auto-discover is enabled
                if self._config.should_auto_discover_tools():
                    if self.mcp_client.connect(server.name):
                        self._discover_tools_from_server(server.name)
                    else:
                        self._logger.warning(f"Failed to connect to MCP server '{server.name}'")

            except Exception as e:
                self._logger.exception(f"Error initializing MCP server: {e}")

    def _discover_tools_from_server(self, server_name: str):
        """
        Discover and register tools from an MCP server.

        Args:
            server_name: Name of the MCP server
        """
        tools = self.mcp_client.discover_tools(server_name)
        for tool in tools:
            self.registry.register(
                tool,
                source=f"mcp:{server_name}",
                tags=["mcp", server_name]
            )

        self._logger.info(f"Registered {len(tools)} tools from MCP server '{server_name}'")

    def execute_tool(self, tool_name: str, parameters: dict = None, timeout: int = None):
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            timeout: Execution timeout

        Returns:
            ToolResult
        """
        return self.executor.execute(tool_name, parameters, timeout)

    def connect_mcp_server(self, server_name: str) -> bool:
        """
        Connect to an MCP server and discover its tools.

        Args:
            server_name: Name of the server

        Returns:
            True if successful
        """
        if self.mcp_client.connect(server_name):
            self._discover_tools_from_server(server_name)
            return True
        return False

    def disconnect_mcp_server(self, server_name: str) -> bool:
        """
        Disconnect from an MCP server and remove its tools.

        Args:
            server_name: Name of the server

        Returns:
            True if successful
        """
        # Remove tools from this server
        self.registry.clear(source=f"mcp:{server_name}")

        # Disconnect
        return self.mcp_client.disconnect(server_name)

    def get_tool_info(self, tool_name: str) -> Optional[dict]:
        """
        Get information about a tool.

        Args:
            tool_name: Tool name

        Returns:
            Dictionary of tool information
        """
        tool = self.registry.get(tool_name)
        if not tool:
            return None

        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": [p.to_dict() for p in tool.parameters],
            "source": self.registry.get_source(tool_name),
            "tags": self.registry.get_tags(tool_name),
        }

    def get_stats(self) -> dict:
        """
        Get statistics about the tool system.

        Returns:
            Dictionary of statistics
        """
        return {
            "total_tools": self.registry.count(),
            "builtin_tools": self.registry.count(source="builtin"),
            "mcp_tools": sum(
                self.registry.count(source=s)
                for s in self.registry.list_sources()
                if s.startswith("mcp:")
            ),
            "mcp_servers": len(self.mcp_client.list_servers()),
            "connected_servers": sum(
                1 for s in self.mcp_client.list_servers()
                if self.mcp_client.is_connected(s.name)
            ),
            "execution_metrics": self.executor.get_metrics(),
        }

    def shutdown(self):
        """Shutdown the tool manager and cleanup resources."""
        self.executor.shutdown()
        self.mcp_client.shutdown()
        self._logger.info("Tool manager shutdown")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (
            f"ToolManager("
            f"tools={stats['total_tools']}, "
            f"mcp_servers={stats['mcp_servers']})"
        )
