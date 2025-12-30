"""
MCP (Model Context Protocol) Client Implementation.

This module provides:
- MCP server connection and management
- Tool discovery via MCP protocol
- Tool invocation through MCP
- Session management
"""

import json
import logging
import subprocess
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .base import Tool, ToolParameter, ToolResult, ToolParameterType


class MCPTransport(Enum):
    """Supported MCP transport mechanisms."""
    STDIO = "stdio"  # Standard input/output
    HTTP = "http"    # HTTP/HTTPS
    SSE = "sse"      # Server-Sent Events


@dataclass
class MCPServer:
    """
    Configuration for an MCP server.

    Attributes:
        name: Unique identifier for this server
        command: Command to execute (for stdio transport)
        args: Arguments for the command
        env: Environment variables
        transport: Transport mechanism (stdio, http, sse)
        url: URL for http/sse transports
        enabled: Whether this server is enabled
        metadata: Additional server metadata
    """
    name: str
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    transport: MCPTransport = MCPTransport.STDIO
    url: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "transport": self.transport.value,
            "url": self.url,
            "enabled": self.enabled,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPServer':
        """Create from dictionary format."""
        transport = data.get("transport", "stdio")
        if isinstance(transport, str):
            transport = MCPTransport(transport)

        return cls(
            name=data["name"],
            command=data.get("command"),
            args=data.get("args", []),
            env=data.get("env", {}),
            transport=transport,
            url=data.get("url"),
            enabled=data.get("enabled", True),
            metadata=data.get("metadata", {}),
        )


class MCPTool(Tool):
    """
    A tool provided by an MCP server.

    This wraps an MCP tool definition and handles execution
    through the MCP client.
    """

    def __init__(self, server_name: str, tool_def: Dict[str, Any], client: 'MCPClient'):
        """
        Initialize an MCP tool.

        Args:
            server_name: Name of the MCP server providing this tool
            tool_def: Tool definition from MCP server
            client: MCP client for execution
        """
        self._server_name = server_name
        self._tool_def = tool_def
        self._client = client
        self._name = tool_def.get("name", "")
        self._description = tool_def.get("description", "")
        self._parameters = self._parse_parameters(tool_def.get("inputSchema", {}))

        super().__init__()

    @property
    def name(self) -> str:
        """Tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Tool description."""
        return self._description

    @property
    def parameters(self) -> List[ToolParameter]:
        """Tool parameters."""
        return self._parameters

    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool via MCP.

        Args:
            **kwargs: Tool parameters

        Returns:
            ToolResult: Result of execution
        """
        return self._client.call_tool(self._server_name, self._name, kwargs)

    def _parse_parameters(self, schema: Dict[str, Any]) -> List[ToolParameter]:
        """
        Parse MCP input schema into ToolParameter objects.

        Args:
            schema: JSON Schema object

        Returns:
            List of ToolParameter objects
        """
        parameters = []
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        for param_name, param_schema in properties.items():
            param_type = self._map_json_type(param_schema.get("type", "string"))

            param = ToolParameter(
                name=param_name,
                type=param_type,
                description=param_schema.get("description", ""),
                required=param_name in required,
                default=param_schema.get("default"),
                enum=param_schema.get("enum"),
            )

            # Handle nested objects
            if param_type == ToolParameterType.OBJECT and "properties" in param_schema:
                param.properties = {
                    k: ToolParameter(
                        name=k,
                        type=self._map_json_type(v.get("type", "string")),
                        description=v.get("description", ""),
                    )
                    for k, v in param_schema["properties"].items()
                }

            # Handle arrays
            if param_type == ToolParameterType.ARRAY and "items" in param_schema:
                items_schema = param_schema["items"]
                param.items = ToolParameter(
                    name="item",
                    type=self._map_json_type(items_schema.get("type", "string")),
                    description=items_schema.get("description", ""),
                )

            parameters.append(param)

        return parameters

    def _map_json_type(self, json_type: str) -> ToolParameterType:
        """Map JSON Schema type to ToolParameterType."""
        mapping = {
            "string": ToolParameterType.STRING,
            "integer": ToolParameterType.INTEGER,
            "number": ToolParameterType.FLOAT,
            "boolean": ToolParameterType.BOOLEAN,
            "object": ToolParameterType.OBJECT,
            "array": ToolParameterType.ARRAY,
        }
        return mapping.get(json_type, ToolParameterType.STRING)


class MCPClient:
    """
    Client for communicating with MCP servers.

    Supports:
    - Multiple server connections
    - Tool discovery
    - Tool invocation
    - Resource management
    """

    def __init__(self):
        """Initialize the MCP client."""
        self._servers: Dict[str, MCPServer] = {}
        self._processes: Dict[str, subprocess.Popen] = {}
        self._logger = logging.getLogger(__name__)

    def add_server(self, server: MCPServer) -> bool:
        """
        Add an MCP server configuration.

        Args:
            server: MCP server configuration

        Returns:
            True if added successfully
        """
        if server.name in self._servers:
            self._logger.warning(f"Server '{server.name}' already exists, replacing")

        self._servers[server.name] = server
        self._logger.info(f"Added MCP server '{server.name}'")
        return True

    def remove_server(self, server_name: str) -> bool:
        """
        Remove an MCP server.

        Args:
            server_name: Name of the server to remove

        Returns:
            True if removed successfully
        """
        if server_name not in self._servers:
            return False

        # Disconnect if connected
        self.disconnect(server_name)

        del self._servers[server_name]
        self._logger.info(f"Removed MCP server '{server_name}'")
        return True

    def connect(self, server_name: str) -> bool:
        """
        Connect to an MCP server.

        Args:
            server_name: Name of the server to connect to

        Returns:
            True if connection succeeded
        """
        if server_name not in self._servers:
            self._logger.error(f"Server '{server_name}' not found")
            return False

        server = self._servers[server_name]

        if not server.enabled:
            self._logger.warning(f"Server '{server_name}' is disabled")
            return False

        # Only stdio is implemented in this basic version
        if server.transport == MCPTransport.STDIO:
            return self._connect_stdio(server_name, server)
        else:
            self._logger.error(f"Transport '{server.transport}' not yet implemented")
            return False

    def _connect_stdio(self, server_name: str, server: MCPServer) -> bool:
        """
        Connect to an MCP server via stdio.

        Args:
            server_name: Server name
            server: Server configuration

        Returns:
            True if connection succeeded
        """
        if not server.command:
            self._logger.error(f"No command specified for server '{server_name}'")
            return False

        try:
            # Start the server process
            process = subprocess.Popen(
                [server.command] + server.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**subprocess.os.environ, **server.env},
                text=True,
            )

            self._processes[server_name] = process
            self._logger.info(f"Connected to MCP server '{server_name}' via stdio")

            # Send initialize request
            self._send_request(server_name, {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "agentix",
                        "version": "1.2.0",
                    }
                }
            })

            return True

        except Exception as e:
            self._logger.exception(f"Failed to connect to server '{server_name}': {e}")
            return False

    def disconnect(self, server_name: str) -> bool:
        """
        Disconnect from an MCP server.

        Args:
            server_name: Name of the server

        Returns:
            True if disconnected successfully
        """
        if server_name not in self._processes:
            return False

        process = self._processes[server_name]

        # Terminate the process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

        del self._processes[server_name]
        self._logger.info(f"Disconnected from MCP server '{server_name}'")
        return True

    def discover_tools(self, server_name: str) -> List[MCPTool]:
        """
        Discover tools available on an MCP server.

        Args:
            server_name: Name of the server

        Returns:
            List of MCPTool objects
        """
        if server_name not in self._processes:
            self._logger.error(f"Not connected to server '{server_name}'")
            return []

        try:
            # Send tools/list request
            response = self._send_request(server_name, {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            })

            if not response or "result" not in response:
                return []

            tools_data = response["result"].get("tools", [])
            tools = [
                MCPTool(server_name, tool_def, self)
                for tool_def in tools_data
            ]

            self._logger.info(
                f"Discovered {len(tools)} tools from server '{server_name}'"
            )
            return tools

        except Exception as e:
            self._logger.exception(f"Failed to discover tools from '{server_name}': {e}")
            return []

    def call_tool(self, server_name: str, tool_name: str,
                  arguments: Dict[str, Any]) -> ToolResult:
        """
        Call a tool on an MCP server.

        Args:
            server_name: Name of the server
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            ToolResult: Result of the tool execution
        """
        if server_name not in self._processes:
            return ToolResult(
                success=False,
                error=f"Not connected to server '{server_name}'"
            )

        try:
            # Send tools/call request
            response = self._send_request(server_name, {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments,
                }
            })

            if not response:
                return ToolResult(
                    success=False,
                    error="No response from server"
                )

            if "error" in response:
                return ToolResult(
                    success=False,
                    error=response["error"].get("message", "Unknown error")
                )

            result = response.get("result", {})
            return ToolResult(
                success=True,
                data=result.get("content", []),
                metadata={
                    "server": server_name,
                    "tool": tool_name,
                    "is_error": result.get("isError", False),
                }
            )

        except Exception as e:
            self._logger.exception(f"Failed to call tool '{tool_name}': {e}")
            return ToolResult(
                success=False,
                error=f"Exception: {str(e)}"
            )

    def _send_request(self, server_name: str, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a JSON-RPC request to an MCP server.

        Args:
            server_name: Name of the server
            request: JSON-RPC request

        Returns:
            Response dictionary, or None if failed
        """
        if server_name not in self._processes:
            return None

        process = self._processes[server_name]

        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()

            # Read response
            response_line = process.stdout.readline()
            if not response_line:
                return None

            response = json.loads(response_line)
            return response

        except Exception as e:
            self._logger.exception(f"Error communicating with server '{server_name}': {e}")
            return None

    def list_servers(self) -> List[MCPServer]:
        """
        List all configured servers.

        Returns:
            List of MCPServer objects
        """
        return list(self._servers.values())

    def is_connected(self, server_name: str) -> bool:
        """
        Check if connected to a server.

        Args:
            server_name: Name of the server

        Returns:
            True if connected
        """
        return server_name in self._processes

    def shutdown(self):
        """Shutdown all server connections."""
        for server_name in list(self._processes.keys()):
            self.disconnect(server_name)

        self._logger.info("MCP client shutdown")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()

    def __repr__(self) -> str:
        """String representation."""
        return f"MCPClient(servers={len(self._servers)}, connected={len(self._processes)})"
