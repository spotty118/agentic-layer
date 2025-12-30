import os
import yaml
from typing import Dict, List, Optional, Tuple

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class Validator:
    """Utility class for validating specs, plans, and tasks."""

    @staticmethod
    def validate_spec(spec_path: str) -> Tuple[bool, Optional[str]]:
        """Validate that a specification file exists and has required sections."""
        if not os.path.exists(spec_path):
            return False, "Specification file not found"

        try:
            with open(spec_path, "r") as f:
                content = f.read()

            if len(content.strip()) == 0:
                return False, "Specification file is empty"

            # Check for key sections (flexible matching)
            required_sections = ["goal", "user stor", "acceptance"]
            content_lower = content.lower()

            missing = []
            for section in required_sections:
                if section not in content_lower:
                    missing.append(section)

            if missing:
                return False, f"Specification missing sections: {', '.join(missing)}"

            return True, None
        except Exception as e:
            return False, f"Error reading specification: {str(e)}"

    @staticmethod
    def validate_plan(plan_path: str) -> Tuple[bool, Optional[str]]:
        """Validate that a plan file exists and has required sections."""
        if not os.path.exists(plan_path):
            return False, "Plan file not found"

        try:
            with open(plan_path, "r") as f:
                content = f.read()

            if len(content.strip()) == 0:
                return False, "Plan file is empty"

            # Check for key sections
            required_sections = ["architecture", "file", "testing"]
            content_lower = content.lower()

            missing = []
            for section in required_sections:
                if section not in content_lower:
                    missing.append(section)

            if missing:
                return False, f"Plan missing sections: {', '.join(missing)}"

            return True, None
        except Exception as e:
            return False, f"Error reading plan: {str(e)}"

    @staticmethod
    def validate_tasks(tasks_path: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Validate tasks file format and return parsed data."""
        if not os.path.exists(tasks_path):
            return False, "Tasks file not found", None

        try:
            with open(tasks_path, "r") as f:
                content = f.read()

            # Extract and parse YAML
            if "---yaml" not in content:
                return False, "Tasks file missing YAML block", None

            try:
                yaml_part = content.split("---yaml")[1].split("---")[0]
                tasks_data = yaml.safe_load(yaml_part)
            except Exception as e:
                return False, f"Invalid YAML format: {str(e)}", None

            if not tasks_data or "tasks" not in tasks_data:
                return False, "Tasks YAML missing 'tasks' key", None

            # Validate each task
            tasks = tasks_data.get("tasks", [])
            if not tasks:
                return False, "No tasks defined", None

            for i, task in enumerate(tasks):
                # Check required fields
                required_fields = ["id", "description", "status", "action", "path"]
                for field in required_fields:
                    if field not in task:
                        return False, f"Task {i+1} missing required field: {field}", None

                # Validate status
                valid_statuses = ["pending", "completed", "failed", "in_progress"]
                if task["status"] not in valid_statuses:
                    return False, f"Task {task['id']} has invalid status: {task['status']}", None

                # Validate action
                valid_actions = ["create_file", "edit_file", "delete_file", "run_command"]
                if task["action"] not in valid_actions:
                    return False, f"Task {task['id']} has invalid action: {task['action']}", None

            return True, None, tasks_data
        except Exception as e:
            return False, f"Error validating tasks: {str(e)}", None

    @staticmethod
    def validate_task_execution(task: Dict, root_dir: str) -> Tuple[bool, Optional[str]]:
        """Validate that a task can be executed."""
        action = task.get("action")
        path = task.get("path")

        if not path:
            return False, "Task missing path"

        full_path = os.path.join(root_dir, path)

        # Action-specific validation
        if action == "edit_file":
            if not os.path.exists(full_path):
                return False, f"Cannot edit non-existent file: {path}"

        elif action == "create_file":
            if os.path.exists(full_path):
                return False, f"File already exists: {path}"

            # Check parent directory exists or can be created
            parent_dir = os.path.dirname(full_path)
            if parent_dir and not os.path.exists(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                except Exception as e:
                    return False, f"Cannot create parent directory: {str(e)}"

        elif action == "delete_file":
            if not os.path.exists(full_path):
                return False, f"Cannot delete non-existent file: {path}"

        elif action == "run_command":
            # Basic validation for run_command
            if not task.get("command"):
                return False, "run_command task missing 'command' field"

        # Validate context files exist
        for context_file in task.get("context_files", []):
            context_path = os.path.join(root_dir, context_file)
            if not os.path.exists(context_path):
                return False, f"Context file not found: {context_file}"

        return True, None

    @staticmethod
    def validate_file_content(content: str, file_type: str = "unknown") -> Tuple[bool, Optional[str]]:
        """Validate that generated file content is reasonable."""
        if not content or len(content.strip()) == 0:
            return False, "Generated content is empty"

        # Check for common LLM artifacts that shouldn't be in the file
        unwanted_patterns = [
            "I apologize",
            "I cannot",
            "As an AI",
            "I don't have access",
            "I'm not able to"
        ]

        for pattern in unwanted_patterns:
            if pattern.lower() in content.lower():
                return False, f"Content contains unwanted pattern: {pattern}"

        # File type specific validation
        if file_type in ["py", "python"]:
            # Check for basic Python syntax (very basic check)
            if "def " not in content and "class " not in content and "import " not in content:
                return False, "Python file appears to have no functions, classes, or imports"

        return True, None

def safe_file_operation(operation, *args, **kwargs):
    """Wrapper for safe file operations with error handling."""
    try:
        return operation(*args, **kwargs)
    except PermissionError as e:
        raise ValidationError(f"Permission denied: {str(e)}")
    except FileNotFoundError as e:
        raise ValidationError(f"File not found: {str(e)}")
    except Exception as e:
        raise ValidationError(f"File operation failed: {str(e)}")
