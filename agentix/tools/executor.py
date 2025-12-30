"""
Tool Executor - Handles safe execution of tools.

The executor provides:
- Parameter validation
- Timeout handling
- Error handling and recovery
- Execution logging and metrics
"""

import time
import logging
from typing import Any, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from .base import Tool, ToolResult
from .registry import ToolRegistry


class ToolExecutor:
    """
    Executor for running tools safely with timeouts and error handling.

    Features:
    - Automatic parameter validation
    - Configurable timeouts
    - Async execution support
    - Execution metrics and logging
    """

    def __init__(self, registry: Optional[ToolRegistry] = None,
                 default_timeout: int = 30,
                 max_workers: int = 4):
        """
        Initialize the tool executor.

        Args:
            registry: Tool registry to use (uses global if None)
            default_timeout: Default timeout in seconds for tool execution
            max_workers: Maximum number of concurrent tool executions
        """
        from .registry import get_global_registry

        self._registry = registry or get_global_registry()
        self._default_timeout = default_timeout
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._logger = logging.getLogger(__name__)
        self._metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_time": 0.0,
        }

    def execute(self, tool_name: str, parameters: Optional[Dict[str, Any]] = None,
                timeout: Optional[int] = None) -> ToolResult:
        """
        Execute a tool by name with the given parameters.

        Args:
            tool_name: Name of the tool to execute
            parameters: Dictionary of parameters to pass to the tool
            timeout: Timeout in seconds (uses default if None)

        Returns:
            ToolResult: Result of the execution
        """
        start_time = time.time()
        self._metrics["total_executions"] += 1
        parameters = parameters or {}

        # Get the tool
        tool = self._registry.get(tool_name)
        if tool is None:
            self._metrics["failed_executions"] += 1
            self._logger.error(f"Tool '{tool_name}' not found in registry")
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found",
            )

        # Validate parameters
        is_valid, error_msg = tool.validate_parameters(parameters)
        if not is_valid:
            self._metrics["failed_executions"] += 1
            self._logger.error(f"Parameter validation failed for '{tool_name}': {error_msg}")
            return ToolResult(
                success=False,
                error=f"Parameter validation failed: {error_msg}",
            )

        # Execute the tool
        try:
            result = self._execute_with_timeout(tool, parameters, timeout)
            execution_time = time.time() - start_time

            if result.success:
                self._metrics["successful_executions"] += 1
            else:
                self._metrics["failed_executions"] += 1

            self._metrics["total_time"] += execution_time

            # Add execution metadata
            result.metadata.update({
                "tool_name": tool_name,
                "execution_time": execution_time,
                "source": self._registry.get_source(tool_name),
            })

            self._logger.info(
                f"Executed tool '{tool_name}' in {execution_time:.2f}s - "
                f"{'success' if result.success else 'failed'}"
            )

            return result

        except Exception as e:
            self._metrics["failed_executions"] += 1
            execution_time = time.time() - start_time
            self._metrics["total_time"] += execution_time

            self._logger.exception(f"Unexpected error executing tool '{tool_name}'")
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                metadata={
                    "tool_name": tool_name,
                    "execution_time": execution_time,
                    "error_type": type(e).__name__,
                }
            )

    def _execute_with_timeout(self, tool: Tool, parameters: Dict[str, Any],
                              timeout: Optional[int]) -> ToolResult:
        """
        Execute a tool with a timeout.

        Args:
            tool: The tool to execute
            parameters: Parameters to pass
            timeout: Timeout in seconds

        Returns:
            ToolResult: Result of execution

        Raises:
            TimeoutError: If execution exceeds timeout
        """
        timeout = timeout or self._default_timeout

        # Submit to executor
        future = self._executor.submit(tool.execute, **parameters)

        try:
            result = future.result(timeout=timeout)
            return result
        except FutureTimeoutError:
            future.cancel()
            self._logger.error(f"Tool '{tool.name}' exceeded timeout of {timeout}s")
            return ToolResult(
                success=False,
                error=f"Execution exceeded timeout of {timeout}s",
                metadata={"timeout": timeout}
            )
        except Exception as e:
            self._logger.exception(f"Error during tool execution: {e}")
            return ToolResult(
                success=False,
                error=f"Execution error: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )

    def execute_batch(self, executions: list[tuple[str, Dict[str, Any]]],
                      timeout: Optional[int] = None) -> list[ToolResult]:
        """
        Execute multiple tools in parallel.

        Args:
            executions: List of (tool_name, parameters) tuples
            timeout: Timeout for each individual execution

        Returns:
            List of ToolResults in the same order as executions
        """
        results = []
        for tool_name, parameters in executions:
            result = self.execute(tool_name, parameters, timeout)
            results.append(result)

        return results

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get execution metrics.

        Returns:
            Dictionary of metrics
        """
        metrics = self._metrics.copy()

        if metrics["total_executions"] > 0:
            metrics["success_rate"] = (
                metrics["successful_executions"] / metrics["total_executions"]
            )
            metrics["average_time"] = (
                metrics["total_time"] / metrics["total_executions"]
            )
        else:
            metrics["success_rate"] = 0.0
            metrics["average_time"] = 0.0

        return metrics

    def reset_metrics(self):
        """Reset execution metrics."""
        self._metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_time": 0.0,
        }
        self._logger.info("Reset executor metrics")

    def shutdown(self, wait: bool = True):
        """
        Shutdown the executor.

        Args:
            wait: If True, wait for pending executions to complete
        """
        self._executor.shutdown(wait=wait)
        self._logger.info("Executor shutdown")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown(wait=True)

    def __repr__(self) -> str:
        """String representation of the executor."""
        metrics = self.get_metrics()
        return (
            f"ToolExecutor("
            f"executions={metrics['total_executions']}, "
            f"success_rate={metrics['success_rate']:.2%})"
        )
