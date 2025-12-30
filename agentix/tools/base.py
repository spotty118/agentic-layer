"""
Base classes for the Agentix tool system.

This module defines the core abstractions for tools, including:
- Tool: Abstract base class for all tools
- ToolParameter: Parameter definition for tools
- ToolResult: Standard result format for tool execution
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class ToolParameterType(Enum):
    """Supported parameter types for tools."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


@dataclass
class ToolParameter:
    """
    Definition of a tool parameter.

    Attributes:
        name: Parameter name
        type: Parameter type (from ToolParameterType)
        description: Human-readable description
        required: Whether this parameter is required
        default: Default value if not provided
        enum: List of allowed values (optional)
        properties: For object types, nested parameter definitions
        items: For array types, item type definition
    """
    name: str
    type: ToolParameterType
    description: str
    required: bool = False
    default: Any = None
    enum: Optional[List[Any]] = None
    properties: Optional[Dict[str, 'ToolParameter']] = None
    items: Optional['ToolParameter'] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert parameter definition to dictionary format."""
        result = {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "required": self.required,
        }

        if self.default is not None:
            result["default"] = self.default

        if self.enum is not None:
            result["enum"] = self.enum

        if self.properties is not None:
            result["properties"] = {
                k: v.to_dict() for k, v in self.properties.items()
            }

        if self.items is not None:
            result["items"] = self.items.to_dict()

        return result


@dataclass
class ToolResult:
    """
    Standard result format for tool execution.

    Attributes:
        success: Whether the tool executed successfully
        data: Result data (can be any type)
        error: Error message if execution failed
        metadata: Additional metadata about the execution
    """
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        result = {
            "success": self.success,
        }

        if self.data is not None:
            result["data"] = self.data

        if self.error is not None:
            result["error"] = self.error

        if self.metadata:
            result["metadata"] = self.metadata

        return result


class Tool(ABC):
    """
    Abstract base class for all tools.

    Tools are executable units that can be invoked by AI providers
    or directly by users. Each tool has:
    - A unique name
    - A description
    - A list of parameters
    - An execute method

    Subclasses must implement:
    - execute(): The actual tool logic
    """

    def __init__(self):
        """Initialize the tool."""
        self._validate_definition()

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """List of parameters this tool accepts."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with the given parameters.

        Args:
            **kwargs: Tool parameters as keyword arguments

        Returns:
            ToolResult: Result of the tool execution
        """
        pass

    def _validate_definition(self):
        """Validate that the tool definition is correct."""
        if not self.name:
            raise ValueError("Tool name cannot be empty")

        if not self.description:
            raise ValueError("Tool description cannot be empty")

    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate that the provided parameters match the tool's schema.

        Args:
            params: Dictionary of parameter values

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in params:
                return False, f"Required parameter '{param.name}' is missing"

        # Check parameter types (basic validation)
        for param_name, param_value in params.items():
            # Find parameter definition
            param_def = next(
                (p for p in self.parameters if p.name == param_name),
                None
            )

            if param_def is None:
                return False, f"Unknown parameter '{param_name}'"

            # Type validation
            if not self._validate_type(param_value, param_def.type):
                return False, f"Parameter '{param_name}' has invalid type"

            # Enum validation
            if param_def.enum and param_value not in param_def.enum:
                return False, f"Parameter '{param_name}' must be one of {param_def.enum}"

        return True, None

    def _validate_type(self, value: Any, expected_type: ToolParameterType) -> bool:
        """Validate that a value matches the expected type."""
        type_map = {
            ToolParameterType.STRING: str,
            ToolParameterType.INTEGER: int,
            ToolParameterType.FLOAT: (int, float),
            ToolParameterType.BOOLEAN: bool,
            ToolParameterType.OBJECT: dict,
            ToolParameterType.ARRAY: (list, tuple),
        }

        expected = type_map.get(expected_type)
        if expected is None:
            return True

        return isinstance(value, expected)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tool definition to dictionary format.

        This is useful for serialization and sending tool definitions
        to AI providers or MCP clients.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
        }

    def __repr__(self) -> str:
        """String representation of the tool."""
        return f"Tool(name='{self.name}')"


class BuiltinTool(Tool):
    """
    Base class for built-in tools that come with Agentix.

    Built-in tools are always available and don't require
    external MCP servers.
    """
    pass
