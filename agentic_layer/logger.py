import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

class AgentLogger:
    """Logger for tracking agent operations and history."""

    def __init__(self, agent_dir: str, enabled: bool = True, level: str = "INFO"):
        self.agent_dir = agent_dir
        self.enabled = enabled
        self.history_dir = os.path.join(agent_dir, "history")
        self.log_file = os.path.join(agent_dir, "agent.log")

        # Create history directory if it doesn't exist
        if self.enabled and not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir, exist_ok=True)

        # Setup Python logging
        self.logger = logging.getLogger("agentic_layer")
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # File handler
        if self.enabled:
            handler = logging.FileHandler(self.log_file)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)

    def info(self, message: str):
        """Log an info message."""
        if self.enabled:
            self.logger.info(message)

    def error(self, message: str):
        """Log an error message."""
        if self.enabled:
            self.logger.error(message)

    def warning(self, message: str):
        """Log a warning message."""
        if self.enabled:
            self.logger.warning(message)

    def debug(self, message: str):
        """Log a debug message."""
        if self.enabled:
            self.logger.debug(message)

    def log_operation(self, operation: str, data: Dict[str, Any]):
        """Log an operation with structured data."""
        if not self.enabled:
            return

        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "operation": operation,
            "data": data
        }

        # Save to history
        history_file = os.path.join(
            self.history_dir,
            f"{operation}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            with open(history_file, "w") as f:
                json.dump(log_entry, f, indent=2)
            self.info(f"Operation logged: {operation}")
        except Exception as e:
            self.error(f"Failed to log operation: {str(e)}")

    def log_task_execution(self, task: Dict[str, Any], success: bool, error: Optional[str] = None):
        """Log task execution results."""
        self.log_operation("task_execution", {
            "task_id": task.get("id"),
            "description": task.get("description"),
            "action": task.get("action"),
            "path": task.get("path"),
            "success": success,
            "error": error
        })

    def log_spec_generation(self, prompt: str, spec_content: str):
        """Log specification generation."""
        self.log_operation("spec_generation", {
            "prompt": prompt,
            "spec_length": len(spec_content),
            "spec_preview": spec_content[:200]
        })

    def log_plan_generation(self, plan_content: str):
        """Log plan generation."""
        self.log_operation("plan_generation", {
            "plan_length": len(plan_content),
            "plan_preview": plan_content[:200]
        })

    def log_tasks_generation(self, num_tasks: int):
        """Log tasks generation."""
        self.log_operation("tasks_generation", {
            "num_tasks": num_tasks
        })

    def get_history(self, operation_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Retrieve operation history."""
        if not self.enabled or not os.path.exists(self.history_dir):
            return []

        history_files = []
        for filename in os.listdir(self.history_dir):
            if filename.endswith(".json"):
                if operation_type is None or filename.startswith(operation_type):
                    history_files.append(os.path.join(self.history_dir, filename))

        # Sort by modification time (newest first)
        history_files.sort(key=os.path.getmtime, reverse=True)

        # Load and return entries
        entries = []
        for filepath in history_files[:limit]:
            try:
                with open(filepath, "r") as f:
                    entries.append(json.load(f))
            except Exception as e:
                self.error(f"Error reading history file {filepath}: {str(e)}")

        return entries

    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """Get history of task executions."""
        return self.get_history("task_execution", limit)

    def clear_history(self):
        """Clear all history files."""
        if not self.enabled or not os.path.exists(self.history_dir):
            return

        for filename in os.listdir(self.history_dir):
            filepath = os.path.join(self.history_dir, filename)
            try:
                os.remove(filepath)
                self.info(f"Removed history file: {filename}")
            except Exception as e:
                self.error(f"Error removing history file {filename}: {str(e)}")

    def print_recent_activity(self, limit: int = 5):
        """Print recent activity to console."""
        entries = self.get_history(limit=limit)

        if not entries:
            print("No recent activity")
            return

        print(f"\n--- Recent Activity (last {len(entries)}) ---")
        for entry in entries:
            timestamp = entry.get("timestamp", "Unknown")
            operation = entry.get("operation", "Unknown")
            data = entry.get("data", {})

            print(f"\n[{timestamp}] {operation}")
            if operation == "task_execution":
                print(f"  Task: {data.get('description', 'N/A')}")
                print(f"  Status: {'✓ Success' if data.get('success') else '✗ Failed'}")
                if data.get('error'):
                    print(f"  Error: {data['error']}")
            elif operation == "spec_generation":
                print(f"  Prompt: {data.get('prompt', 'N/A')[:50]}...")
            elif operation == "plan_generation":
                print(f"  Plan length: {data.get('plan_length', 'N/A')} chars")
            elif operation == "tasks_generation":
                print(f"  Tasks generated: {data.get('num_tasks', 'N/A')}")

class ColoredOutput:
    """Utility for colored console output."""

    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"

    @staticmethod
    def success(message: str):
        """Print success message in green."""
        print(f"{ColoredOutput.GREEN}✓ {message}{ColoredOutput.RESET}")

    @staticmethod
    def error(message: str):
        """Print error message in red."""
        print(f"{ColoredOutput.RED}✗ {message}{ColoredOutput.RESET}")

    @staticmethod
    def warning(message: str):
        """Print warning message in yellow."""
        print(f"{ColoredOutput.YELLOW}⚠ {message}{ColoredOutput.RESET}")

    @staticmethod
    def info(message: str):
        """Print info message in blue."""
        print(f"{ColoredOutput.BLUE}ℹ {message}{ColoredOutput.RESET}")

    @staticmethod
    def header(message: str):
        """Print header message in bold."""
        print(f"{ColoredOutput.BOLD}{message}{ColoredOutput.RESET}")

    @staticmethod
    def task(message: str):
        """Print task message in cyan."""
        print(f"{ColoredOutput.CYAN}→ {message}{ColoredOutput.RESET}")
