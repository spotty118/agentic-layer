"""
Built-in tools that come with Agentix.

These tools are always available and don't require external MCP servers.
"""

import os
import subprocess
from typing import List
from .base import BuiltinTool, ToolParameter, ToolResult, ToolParameterType


class FileReadTool(BuiltinTool):
    """Read the contents of a file."""

    @property
    def name(self) -> str:
        return "file_read"

    @property
    def description(self) -> str:
        return "Read the contents of a file from the filesystem"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="path",
                type=ToolParameterType.STRING,
                description="Path to the file to read",
                required=True,
            ),
            ToolParameter(
                name="encoding",
                type=ToolParameterType.STRING,
                description="File encoding (default: utf-8)",
                required=False,
                default="utf-8",
            ),
        ]

    def execute(self, **kwargs) -> ToolResult:
        path = kwargs["path"]
        encoding = kwargs.get("encoding", "utf-8")

        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()

            return ToolResult(
                success=True,
                data={"content": content, "path": path},
                metadata={"size": len(content)}
            )
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error=f"File not found: {path}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error reading file: {str(e)}"
            )


class FileWriteTool(BuiltinTool):
    """Write content to a file."""

    @property
    def name(self) -> str:
        return "file_write"

    @property
    def description(self) -> str:
        return "Write content to a file on the filesystem"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="path",
                type=ToolParameterType.STRING,
                description="Path to the file to write",
                required=True,
            ),
            ToolParameter(
                name="content",
                type=ToolParameterType.STRING,
                description="Content to write to the file",
                required=True,
            ),
            ToolParameter(
                name="encoding",
                type=ToolParameterType.STRING,
                description="File encoding (default: utf-8)",
                required=False,
                default="utf-8",
            ),
        ]

    def execute(self, **kwargs) -> ToolResult:
        path = kwargs["path"]
        content = kwargs["content"]
        encoding = kwargs.get("encoding", "utf-8")

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

            return ToolResult(
                success=True,
                data={"path": path, "bytes_written": len(content.encode(encoding))},
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error writing file: {str(e)}"
            )


class FileListTool(BuiltinTool):
    """List files in a directory."""

    @property
    def name(self) -> str:
        return "file_list"

    @property
    def description(self) -> str:
        return "List files and directories in a given path"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="path",
                type=ToolParameterType.STRING,
                description="Path to the directory to list",
                required=False,
                default=".",
            ),
            ToolParameter(
                name="recursive",
                type=ToolParameterType.BOOLEAN,
                description="List recursively",
                required=False,
                default=False,
            ),
        ]

    def execute(self, **kwargs) -> ToolResult:
        path = kwargs.get("path", ".")
        recursive = kwargs.get("recursive", False)

        try:
            if recursive:
                files = []
                for root, dirs, filenames in os.walk(path):
                    for filename in filenames:
                        files.append(os.path.join(root, filename))
            else:
                files = [
                    os.path.join(path, f)
                    for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path, f))
                ]

            return ToolResult(
                success=True,
                data={"files": files, "count": len(files)},
            )
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error=f"Directory not found: {path}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error listing directory: {str(e)}"
            )


class ShellExecuteTool(BuiltinTool):
    """Execute a shell command."""

    @property
    def name(self) -> str:
        return "shell_execute"

    @property
    def description(self) -> str:
        return "Execute a shell command and return its output"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="command",
                type=ToolParameterType.STRING,
                description="Shell command to execute",
                required=True,
            ),
            ToolParameter(
                name="working_dir",
                type=ToolParameterType.STRING,
                description="Working directory for the command",
                required=False,
                default=".",
            ),
            ToolParameter(
                name="timeout",
                type=ToolParameterType.INTEGER,
                description="Timeout in seconds",
                required=False,
                default=30,
            ),
        ]

    def execute(self, **kwargs) -> ToolResult:
        command = kwargs["command"]
        working_dir = kwargs.get("working_dir", ".")
        timeout = kwargs.get("timeout", 30)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=timeout,
            )

            return ToolResult(
                success=result.returncode == 0,
                data={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                },
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Command timed out after {timeout} seconds"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error executing command: {str(e)}"
            )


# List of all built-in tools
BUILTIN_TOOLS = [
    FileReadTool,
    FileWriteTool,
    FileListTool,
    ShellExecuteTool,
]


def get_builtin_tools() -> List[BuiltinTool]:
    """
    Get instances of all built-in tools.

    Returns:
        List of built-in tool instances
    """
    return [tool_class() for tool_class in BUILTIN_TOOLS]
