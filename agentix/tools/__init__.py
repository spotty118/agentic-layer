"""
Agentix Tools Module - MCP Support and Plugin System

This module provides:
- Tool abstraction and base classes
- Tool registry for discovery and management
- MCP (Model Context Protocol) client implementation
- Tool execution engine
- Plugin system for extensibility
- Built-in tools
"""

from .base import Tool, ToolParameter, ToolResult, BuiltinTool
from .registry import ToolRegistry, get_global_registry
from .executor import ToolExecutor
from .mcp_client import MCPClient, MCPServer
from .manager import ToolManager
from .builtin_tools import get_builtin_tools

__all__ = [
    'Tool',
    'ToolParameter',
    'ToolResult',
    'BuiltinTool',
    'ToolRegistry',
    'get_global_registry',
    'ToolExecutor',
    'MCPClient',
    'MCPServer',
    'ToolManager',
    'get_builtin_tools',
]

__version__ = '1.0.0'
