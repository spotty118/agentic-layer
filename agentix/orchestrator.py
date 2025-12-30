import os
import yaml
import subprocess
from .config import Config
from .validators import Validator, ValidationError, safe_file_operation
from .logger import AgentLogger, ColoredOutput
from .providers.router import ProviderRouter
from .diff_utils import DiffViewer
from .context_window import SharedContextWindow

class Orchestrator:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.agent_dir = os.path.join(root_dir, ".agent")
        self.spec_path = os.path.join(self.agent_dir, "spec.md")
        self.plan_path = os.path.join(self.agent_dir, "plan.md")
        self.tasks_path = os.path.join(self.agent_dir, "tasks.md")
        self.backup_dir = os.path.join(self.agent_dir, "backups")

        # Initialize configuration and logging
        self.config = Config(self.agent_dir) if os.path.exists(self.agent_dir) else None
        self.logger = None
        self.router = None
        self.shared_context = None
        self.diff_viewer = DiffViewer(self.agent_dir) if os.path.exists(self.agent_dir) else None

        if self.config:
            self.logger = AgentLogger(
                self.agent_dir,
                enabled=self.config.is_logging_enabled(),
                level=self.config.get_log_level()
            )

            # Initialize shared context window if enabled
            if self.config.get("shared_context.enabled", False):
                max_tokens = self.config.get("shared_context.max_tokens", 200000)
                self.shared_context = SharedContextWindow(max_tokens=max_tokens)
                ColoredOutput.success(f"Initialized shared context window ({max_tokens} tokens)")

            # Initialize AI provider router
            try:
                providers_config = self.config.get_providers_config()
                self.router = ProviderRouter(
                    config={"providers": providers_config},
                    shared_context=self.shared_context
                )
                ColoredOutput.success(f"Initialized {len(self.router.get_available_providers())} AI providers")
            except Exception as e:
                ColoredOutput.error(f"Failed to initialize AI providers: {str(e)}")
                raise

    def init(self):
        if not os.path.exists(self.agent_dir):
            os.makedirs(self.agent_dir)
            os.makedirs(self.backup_dir, exist_ok=True)

            # Initialize config and logger
            self.config = Config(self.agent_dir)
            self.config.create_default_config()

            self.logger = AgentLogger(
                self.agent_dir,
                enabled=self.config.is_logging_enabled(),
                level=self.config.get_log_level()
            )

            # Initialize diff viewer
            self.diff_viewer = DiffViewer(self.agent_dir)

            ColoredOutput.success(f"Initialized agentic layer in {self.agent_dir}")
            ColoredOutput.info("Created default config.yaml - customize as needed")
            if self.logger:
                self.logger.info("Agentic layer initialized")
        else:
            ColoredOutput.warning("Agentic layer already initialized.")

    def _get_codebase_context(self, max_depth=4):
        """
        Generate structured codebase context with intelligent filtering.

        Args:
            max_depth: Maximum directory depth to traverse (default: 4)

        Returns:
            str: Formatted codebase structure with file categorization
        """
        # Directories to ignore
        ignore_dirs = {
            '.agent', '.git', '__pycache__', 'node_modules',
            '.pytest_cache', '.mypy_cache', '.tox', 'venv',
            'env', '.env', 'dist', 'build', '.egg-info',
            '.idea', '.vscode', '.DS_Store'
        }

        # File extensions to ignore
        ignore_extensions = {
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
            '.class', '.o', '.obj', '.log', '.lock'
        }

        # File type categorization
        file_categories = {
            'Python': ['.py', '.pyi', '.pyx'],
            'JavaScript/TypeScript': ['.js', '.jsx', '.ts', '.tsx', '.mjs'],
            'Web': ['.html', '.css', '.scss', '.sass', '.vue'],
            'Config': ['.yaml', '.yml', '.json', '.toml', '.ini', '.cfg', '.conf'],
            'Documentation': ['.md', '.rst', '.txt', '.adoc'],
            'Data': ['.csv', '.parquet', '.pkl', '.h5', '.db', '.sqlite'],
        }

        context = "=== Codebase Structure ===\n\n"
        file_stats = {cat: 0 for cat in file_categories}
        file_stats['Other'] = 0
        total_files = 0

        # Build tree structure
        tree_lines = []

        for root, dirs, files in os.walk(self.root_dir):
            # Calculate depth
            rel_path = os.path.relpath(root, self.root_dir)
            if rel_path == '.':
                level = 0
            else:
                level = rel_path.count(os.sep) + 1

            # Skip if too deep
            if level > max_depth:
                dirs[:] = []  # Don't descend further
                continue

            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]

            # Skip if this is an ignored directory
            if any(ignored in root for ignored in ignore_dirs):
                continue

            # Format directory name
            indent = '  ' * level
            dir_name = os.path.basename(root) or os.path.basename(self.root_dir)

            if level == 0:
                tree_lines.append(f"{dir_name}/")
            else:
                tree_lines.append(f"{indent}├── {dir_name}/")

            # Process files
            file_indent = '  ' * (level + 1)
            filtered_files = []

            for f in sorted(files):
                # Skip ignored extensions
                _, ext = os.path.splitext(f)
                if ext in ignore_extensions or f.startswith('.'):
                    continue

                filtered_files.append(f)
                total_files += 1

                # Categorize file
                categorized = False
                for category, extensions in file_categories.items():
                    if ext in extensions:
                        file_stats[category] += 1
                        categorized = True
                        break

                if not categorized:
                    file_stats['Other'] += 1

            # Add files to tree (limit to prevent huge output)
            for f in filtered_files[:20]:  # Max 20 files per directory
                tree_lines.append(f"{file_indent}├── {f}")

            if len(filtered_files) > 20:
                tree_lines.append(f"{file_indent}├── ... ({len(filtered_files) - 20} more files)")

        # Build final context
        context += '\n'.join(tree_lines[:100])  # Limit total lines

        if len(tree_lines) > 100:
            context += f"\n\n... ({len(tree_lines) - 100} more lines)\n"

        # Add file statistics
        context += "\n\n=== File Statistics ===\n"
        context += f"Total Files: {total_files}\n\n"

        context += "By Type:\n"
        for category, count in sorted(file_stats.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                context += f"  • {category}: {count}\n"

        return context

    def specify(self, prompt):
        ColoredOutput.header(f"\n📝 Generating specification for: {prompt}\n")

        if self.logger:
            self.logger.info(f"Starting spec generation: {prompt}")

        context = self._get_codebase_context()

        system_prompt = self.config.get_prompt("specify") if self.config else \
            "You are a product manager. Generate a functional specification (spec.md) based on the user's goal and codebase context. Focus on 'what' and 'why'. Use sections: Goal, User Stories, Acceptance Criteria, Edge Cases."

        # Get preferred provider for specification task
        preferred_provider = self.config.get_task_routing("specification") if self.config else None

        try:
            # Use router to intelligently select provider
            spec_content, used_provider = self.router.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Goal: {prompt}\n\nCodebase Context:\n{context}"}
                ],
                task_type="specification",
                temperature=self.config.get_temperature() if self.config else 0.7,
                max_tokens=self.config.get_max_tokens() if self.config else 4096,
                preferred_provider=preferred_provider,
                use_shared_context=self.shared_context is not None
            )

            ColoredOutput.info(f"Used AI provider: {used_provider}")

            with open(self.spec_path, "w") as f:
                f.write(spec_content)

            ColoredOutput.success(f"Specification saved to {self.spec_path}")

            # Validate the generated spec
            is_valid, error_msg = Validator.validate_spec(self.spec_path)
            if not is_valid:
                ColoredOutput.warning(f"Spec validation warning: {error_msg}")

            if self.logger:
                self.logger.log_spec_generation(prompt, spec_content)
                self.logger.info(f"Spec generation completed using {used_provider}")

        except Exception as e:
            ColoredOutput.error(f"Error generating specification: {str(e)}")
            if self.logger:
                self.logger.error(f"Spec generation failed: {str(e)}")
            raise

    def plan(self):
        if not os.path.exists(self.spec_path):
            ColoredOutput.error("spec.md not found. Run 'specify' first.")
            return

        ColoredOutput.header("\n🏗️  Generating technical plan...\n")

        if self.logger:
            self.logger.info("Starting plan generation")

        # Validate spec first
        is_valid, error_msg = Validator.validate_spec(self.spec_path)
        if not is_valid:
            ColoredOutput.error(f"Cannot generate plan: {error_msg}")
            return

        with open(self.spec_path, "r") as f:
            spec = f.read()

        context = self._get_codebase_context()

        system_prompt = self.config.get_prompt("plan") if self.config else \
            "You are a software architect. Generate a technical implementation plan (plan.md) based on the functional specification and codebase context. Focus on 'how'. Use sections: Architecture Overview, File Changes, Dependencies, Testing Strategy."

        # Get preferred provider for planning task
        preferred_provider = self.config.get_task_routing("planning") if self.config else None

        try:
            # Use router to intelligently select provider
            plan_content, used_provider = self.router.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Specification:\n{spec}\n\nCodebase Context:\n{context}"}
                ],
                task_type="planning",
                temperature=self.config.get_temperature() if self.config else 0.7,
                max_tokens=self.config.get_max_tokens() if self.config else 4096,
                preferred_provider=preferred_provider,
                use_shared_context=self.shared_context is not None
            )

            ColoredOutput.info(f"Used AI provider: {used_provider}")

            with open(self.plan_path, "w") as f:
                f.write(plan_content)

            ColoredOutput.success(f"Plan saved to {self.plan_path}")

            # Validate the generated plan
            is_valid, error_msg = Validator.validate_plan(self.plan_path)
            if not is_valid:
                ColoredOutput.warning(f"Plan validation warning: {error_msg}")

            if self.logger:
                self.logger.log_plan_generation(plan_content)
                self.logger.info(f"Plan generation completed using {used_provider}")

        except Exception as e:
            ColoredOutput.error(f"Error generating plan: {str(e)}")
            if self.logger:
                self.logger.error(f"Plan generation failed: {str(e)}")
            raise

    def tasks(self):
        if not os.path.exists(self.plan_path):
            ColoredOutput.error("plan.md not found. Run 'plan' first.")
            return

        ColoredOutput.header("\n📋 Generating executable task list...\n")

        if self.logger:
            self.logger.info("Starting tasks generation")

        # Validate plan first
        is_valid, error_msg = Validator.validate_plan(self.plan_path)
        if not is_valid:
            ColoredOutput.error(f"Cannot generate tasks: {error_msg}")
            return

        with open(self.plan_path, "r") as f:
            plan = f.read()

        system_prompt = self.config.get_prompt("tasks") if self.config else \
            """You are a technical lead. Break the technical plan into atomic, executable tasks.
Output a Markdown file with a YAML block at the top.
The YAML block must follow this structure:
---yaml
tasks:
  - id: 1
    description: "Short description"
    status: pending
    action: create_file | edit_file | delete_file | run_command
    path: "path/to/file"
    context_files: []
---
Followed by a human-readable checklist."""

        # Get preferred provider for tasks task
        preferred_provider = self.config.get_task_routing("tasks") if self.config else None

        try:
            # Use router to intelligently select provider
            tasks_content, used_provider = self.router.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Technical Plan:\n{plan}"}
                ],
                task_type="tasks",
                temperature=self.config.get_temperature() if self.config else 0.7,
                max_tokens=self.config.get_max_tokens() if self.config else 4096,
                preferred_provider=preferred_provider,
                use_shared_context=self.shared_context is not None
            )

            ColoredOutput.info(f"Used AI provider: {used_provider}")
            tasks_content_to_save = tasks_content

            with open(self.tasks_path, "w") as f:
                f.write(tasks_content_to_save)

            ColoredOutput.success(f"Tasks saved to {self.tasks_path}")

            # Validate the generated tasks
            is_valid, error_msg, tasks_data = Validator.validate_tasks(self.tasks_path)
            if not is_valid:
                ColoredOutput.error(f"Tasks validation failed: {error_msg}")
                return

            num_tasks = len(tasks_data.get("tasks", []))
            ColoredOutput.info(f"Generated {num_tasks} tasks")

            if self.logger:
                self.logger.log_tasks_generation(num_tasks)
                self.logger.info(f"Tasks generation completed using {used_provider}")

        except Exception as e:
            ColoredOutput.error(f"Error generating tasks: {str(e)}")
            if self.logger:
                self.logger.error(f"Tasks generation failed: {str(e)}")
            raise

    def work(self):
        if not os.path.exists(self.tasks_path):
            ColoredOutput.error("tasks.md not found. Run 'tasks' first.")
            return

        ColoredOutput.header("\n⚙️  Executing next task...\n")

        # Validate tasks file
        is_valid, error_msg, tasks_data = Validator.validate_tasks(self.tasks_path)
        if not is_valid:
            ColoredOutput.error(f"Tasks validation failed: {error_msg}")
            return

        with open(self.tasks_path, "r") as f:
            content = f.read()

        # Find next pending task
        next_task = None
        for task in tasks_data.get("tasks", []):
            if task["status"] == "pending":
                next_task = task
                break

        if not next_task:
            ColoredOutput.success("🎉 No pending tasks found. All tasks completed!")
            return

        ColoredOutput.task(f"Task {next_task['id']}: {next_task['description']}")
        ColoredOutput.info(f"Action: {next_task['action']} on {next_task['path']}")

        # Validate task can be executed
        can_execute, validation_error = Validator.validate_task_execution(next_task, self.root_dir)
        if not can_execute:
            ColoredOutput.error(f"Cannot execute task: {validation_error}")
            if self.logger:
                self.logger.log_task_execution(next_task, False, validation_error)
            return

        # Request confirmation if configured
        if self.config and self.config.should_confirm():
            response = input(f"\n{ColoredOutput.YELLOW}Execute this task? (y/n): {ColoredOutput.RESET}")
            if response.lower() != 'y':
                ColoredOutput.warning("Task execution cancelled by user")
                return

        # Execute the task
        try:
            self._execute_task(next_task, tasks_data, content)
        except Exception as e:
            ColoredOutput.error(f"Task execution failed: {str(e)}")
            if self.logger:
                self.logger.log_task_execution(next_task, False, str(e))
            raise

    def _execute_task(self, task, tasks_data, full_content):
        if self.logger:
            self.logger.info(f"Executing task {task['id']}: {task['description']}")

        target_path = os.path.join(self.root_dir, task["path"])

        # Create backup if file exists
        if os.path.exists(target_path):
            self._create_backup(task["path"])

        # Handle different action types
        if task["action"] == "run_command":
            self._execute_command(task)
        elif task["action"] == "delete_file":
            self._delete_file(task, target_path)
        else:
            # create_file or edit_file
            self._generate_and_write_file(task, target_path)

        # Mark task as completed
        ColoredOutput.success(f"✓ Task {task['id']} completed")

        task["status"] = "completed"
        self._update_tasks_file(tasks_data, full_content, task)

        if self.logger:
            self.logger.log_task_execution(task, True)

    def _create_backup(self, relative_path: str):
        """Create a backup of the file before modifying."""
        source_path = os.path.join(self.root_dir, relative_path)
        if not os.path.exists(source_path):
            return

        import shutil
        from datetime import datetime

        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{relative_path.replace('/', '_')}_{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)

        shutil.copy2(source_path, backup_path)
        ColoredOutput.info(f"Backup created: {backup_name}")

    def _execute_command(self, task: dict):
        """Execute a shell command."""
        command = task.get("command", "")
        if not command:
            raise ValidationError("No command specified for run_command task")

        ColoredOutput.info(f"Running command: {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                ColoredOutput.error(f"Command failed with exit code {result.returncode}")
                ColoredOutput.error(f"stderr: {result.stderr}")
                raise RuntimeError(f"Command failed: {result.stderr}")

            ColoredOutput.success("Command executed successfully")
            if result.stdout:
                print(result.stdout)

        except subprocess.TimeoutExpired:
            raise RuntimeError("Command timed out after 5 minutes")

    def _delete_file(self, task: dict, target_path: str):
        """Delete a file."""
        try:
            os.remove(target_path)
            ColoredOutput.success(f"Deleted {task['path']}")
        except Exception as e:
            raise RuntimeError(f"Failed to delete file: {str(e)}")

    def _generate_and_write_file(self, task: dict, target_path: str):
        """Generate file content using LLM and write it."""
        # Read context files
        context_content = ""
        for cf in task.get("context_files", []):
            full_cf_path = os.path.join(self.root_dir, cf)
            if os.path.exists(full_cf_path):
                with open(full_cf_path, "r") as f:
                    context_content += f"\nFile: {cf}\nContent:\n{f.read()}\n"

        # If editing, read the target file
        target_file_content = ""
        if task["action"] == "edit_file" and os.path.exists(target_path):
            with open(target_path, "r") as f:
                target_file_content = f.read()

        # Get custom prompt or use default
        system_prompt = self.config.get_prompt("work") if self.config else \
            "You are a senior developer. Execute the following task: {description}. Action: {action} on {path}. Output ONLY the full content of the file after the change. No markdown blocks, no explanation."

        system_prompt = system_prompt.format(
            description=task['description'],
            action=task['action'],
            path=task['path']
        )

        # Get preferred provider for code generation task
        preferred_provider = self.config.get_task_routing("code_generation") if self.config else None

        ColoredOutput.info("Generating file content...")

        # Use router to intelligently select provider
        new_content, used_provider = self.router.complete(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context Files:\n{context_content}\n\nTarget File Current Content:\n{target_file_content}"}
            ],
            task_type="code_generation",
            temperature=self.config.get_temperature() if self.config else 0.7,
            max_tokens=self.config.get_max_tokens() if self.config else 4096,
            preferred_provider=preferred_provider,
            use_shared_context=self.shared_context is not None
        )

        ColoredOutput.info(f"Used AI provider: {used_provider}")
        new_content = new_content.strip()

        # Clean up potential markdown code blocks
        if new_content.startswith("```"):
            lines = new_content.split("\n")
            if lines[0].startswith("```"):
                new_content = "\n".join(lines[1:-1])

        # Validate generated content
        file_extension = os.path.splitext(task["path"])[1][1:]  # Remove the dot
        is_valid, validation_error = Validator.validate_file_content(new_content, file_extension)
        if not is_valid:
            ColoredOutput.warning(f"Content validation warning: {validation_error}")

        # Show diff preview if file already exists and confirmation is required
        if os.path.exists(target_path) and self.config and self.config.should_confirm() and self.diff_viewer:
            diff_text = self.diff_viewer.preview_change(task["path"], new_content, diff_type="unified")
            if diff_text and diff_text.strip():
                ColoredOutput.header(f"\n📊 Preview of changes to {task['path']}:\n")
                print(diff_text)
                stats = self.diff_viewer.format_diff_stats(diff_text)
                print(f"\n{ColoredOutput.CYAN}{stats}{ColoredOutput.RESET}\n")

                response = input(f"{ColoredOutput.YELLOW}Apply these changes? (y/n): {ColoredOutput.RESET}")
                if response.lower() != 'y':
                    ColoredOutput.warning("File changes cancelled by user")
                    return

        # Write the file
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w") as f:
            f.write(new_content)

        ColoredOutput.success(f"Updated {task['path']}")

    def _update_tasks_file(self, tasks_data: dict, full_content: str, completed_task: dict):
        """Update the tasks.md file with new status."""
        new_yaml = yaml.dump(tasks_data, default_flow_style=False)
        updated_content = full_content.replace(
            full_content.split("---yaml")[1].split("---")[0],
            "\n" + new_yaml + "\n"
        )

        # Update the human-readable checklist
        desc = completed_task['description']
        updated_content = updated_content.replace(f"- [ ] {desc}", f"- [x] {desc}")

        with open(self.tasks_path, "w") as f:
            f.write(updated_content)

    def status(self):
        ColoredOutput.header("\n--- 📊 Agentic Layer Status ---\n")

        # Check file status
        for file, name in [(self.spec_path, "Specification"), (self.plan_path, "Plan"), (self.tasks_path, "Tasks")]:
            if os.path.exists(file):
                ColoredOutput.success(f"{name}: ✓ Exists")
            else:
                ColoredOutput.warning(f"{name}: ✗ Missing")

        # Show task progress
        if os.path.exists(self.tasks_path):
            is_valid, error_msg, tasks_data = Validator.validate_tasks(self.tasks_path)

            if is_valid:
                tasks = tasks_data.get("tasks", [])
                completed = sum(1 for t in tasks if t["status"] == "completed")
                pending = sum(1 for t in tasks if t["status"] == "pending")
                failed = sum(1 for t in tasks if t["status"] == "failed")
                total = len(tasks)

                print(f"\n📋 Task Progress:")
                ColoredOutput.success(f"  Completed: {completed}/{total}")
                if pending > 0:
                    ColoredOutput.info(f"  Pending: {pending}/{total}")
                if failed > 0:
                    ColoredOutput.error(f"  Failed: {failed}/{total}")

                # Show next pending task
                for task in tasks:
                    if task["status"] == "pending":
                        ColoredOutput.task(f"\nNext task: {task['description']}")
                        break
            else:
                ColoredOutput.error(f"Could not parse tasks: {error_msg}")

        # Show recent activity if logging is enabled
        if self.logger and self.logger.enabled:
            print()
            self.logger.print_recent_activity(limit=3)

    def review(self):
        """Review recent changes made by the agent."""
        ColoredOutput.header("\n--- 🔍 Review Recent Changes ---\n")

        if not self.logger or not self.logger.enabled:
            ColoredOutput.warning("Logging is not enabled. Cannot review changes.")
            return

        # Get recent task executions
        task_history = self.logger.get_task_history(limit=10)

        if not task_history:
            ColoredOutput.info("No task execution history found.")
            return

        for i, entry in enumerate(task_history, 1):
            data = entry.get("data", {})
            timestamp = entry.get("timestamp", "Unknown")
            success = data.get("success", False)

            print(f"\n{i}. [{timestamp}]")
            ColoredOutput.task(f"   Description: {data.get('description', 'N/A')}")
            print(f"   Action: {data.get('action', 'N/A')}")
            print(f"   Path: {data.get('path', 'N/A')}")

            if success:
                ColoredOutput.success("   Status: ✓ Success")
            else:
                ColoredOutput.error("   Status: ✗ Failed")
                if data.get('error'):
                    print(f"   Error: {data['error']}")

        # Show backup files
        if os.path.exists(self.backup_dir):
            backups = os.listdir(self.backup_dir)
            if backups:
                print(f"\n💾 Backups available ({len(backups)}):")
                for backup in sorted(backups, reverse=True)[:5]:
                    print(f"   - {backup}")

    def history(self, limit: int = 10):
        """Show execution history."""
        if not self.logger or not self.logger.enabled:
            ColoredOutput.warning("Logging is not enabled.")
            return

        self.logger.print_recent_activity(limit=limit)

    def rollback(self, task_id: int = None, backup_index: int = None, auto_confirm: bool = False):
        """
        Rollback to a previous backup.

        Args:
            task_id: Not used (reserved for future task-specific rollback)
            backup_index: Index of backup to restore (1-based, None for interactive)
            auto_confirm: Skip confirmation prompt (use with caution)
        """
        ColoredOutput.header("\n--- ⏮️  Rollback ---\n")

        if not os.path.exists(self.backup_dir):
            ColoredOutput.error("No backups found.")
            return

        backups = sorted(os.listdir(self.backup_dir), reverse=True)
        if not backups:
            ColoredOutput.error("No backups found.")
            return

        # Show available backups with details
        ColoredOutput.info("Available backups:\n")
        backup_info = []

        for i, backup in enumerate(backups[:20], 1):  # Show up to 20 backups
            # Parse backup filename: {path}_{timestamp}.bak
            try:
                parts = backup.rsplit('_', 2)
                if len(parts) >= 3:
                    file_path = parts[0].replace('_', '/')
                    timestamp = f"{parts[1]}_{parts[2].replace('.bak', '')}"
                    # Format timestamp for readability
                    from datetime import datetime
                    try:
                        dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                        readable_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        readable_time = timestamp

                    backup_info.append((i, backup, file_path, readable_time))
                    print(f"  {i}. {file_path}")
                    print(f"     Time: {readable_time}")
                    print()
                else:
                    backup_info.append((i, backup, backup, "Unknown"))
                    print(f"  {i}. {backup}")
                    print()
            except Exception:
                backup_info.append((i, backup, backup, "Unknown"))
                print(f"  {i}. {backup}")
                print()

        # Select backup to restore
        if backup_index is None:
            try:
                selection = input(ColoredOutput.CYAN + "\nEnter backup number to restore (or 'q' to quit): " + ColoredOutput.RESET)
                if selection.lower() == 'q':
                    ColoredOutput.info("Rollback cancelled.")
                    return

                backup_index = int(selection)
            except (ValueError, KeyboardInterrupt):
                ColoredOutput.error("Invalid selection.")
                return

        if backup_index < 1 or backup_index > len(backup_info):
            ColoredOutput.error(f"Invalid backup number. Must be between 1 and {len(backup_info)}.")
            return

        # Get selected backup
        selected = backup_info[backup_index - 1]
        backup_file = selected[1]
        original_path = selected[2]

        # Confirmation
        if not auto_confirm:
            ColoredOutput.warning(f"\n⚠️  This will restore: {original_path}")
            ColoredOutput.warning(f"   From backup: {backup_file}")
            ColoredOutput.warning("\n   Current file will be backed up first.")

            confirm = input(ColoredOutput.YELLOW + "\nProceed with rollback? (yes/no): " + ColoredOutput.RESET)
            if confirm.lower() not in ['yes', 'y']:
                ColoredOutput.info("Rollback cancelled.")
                return

        # Perform rollback
        try:
            import shutil

            backup_path = os.path.join(self.backup_dir, backup_file)
            target_path = os.path.join(self.root_dir, original_path)

            # Create backup of current file before rolling back
            if os.path.exists(target_path):
                self._create_backup(original_path)
                ColoredOutput.info("Current file backed up before rollback.")

            # Ensure target directory exists
            target_dir = os.path.dirname(target_path)
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)

            # Restore from backup
            shutil.copy2(backup_path, target_path)
            ColoredOutput.success(f"\n✅ Successfully restored: {original_path}")
            ColoredOutput.info(f"   From: {backup_file}")

            if self.logger:
                self.logger.info(f"Rollback: Restored {original_path} from {backup_file}")

        except Exception as e:
            ColoredOutput.error(f"Rollback failed: {str(e)}")
            if self.logger:
                self.logger.error(f"Rollback failed: {str(e)}")
