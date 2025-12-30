import os
import yaml
from openai import OpenAI

class Orchestrator:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.agent_dir = os.path.join(root_dir, ".agent")
        self.spec_path = os.path.join(self.agent_dir, "spec.md")
        self.plan_path = os.path.join(self.agent_dir, "plan.md")
        self.tasks_path = os.path.join(self.agent_dir, "tasks.md")
        self.client = OpenAI() # Uses pre-configured environment variables

    def init(self):
        if not os.path.exists(self.agent_dir):
            os.makedirs(self.agent_dir)
            print(f"Initialized agentic layer in {self.agent_dir}")
        else:
            print("Agentic layer already initialized.")

    def _get_codebase_context(self):
        # Simple file tree for now
        context = "Codebase Structure:\n"
        for root, dirs, files in os.walk(self.root_dir):
            if ".agent" in root or ".git" in root:
                continue
            level = root.replace(self.root_dir, '').count(os.sep)
            indent = ' ' * 4 * (level)
            context += f"{indent}{os.path.basename(root)}/\n"
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                context += f"{subindent}{f}\n"
        return context

    def specify(self, prompt):
        print(f"Generating specification for: {prompt}")
        context = self._get_codebase_context()
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a product manager. Generate a functional specification (spec.md) based on the user's goal and codebase context. Focus on 'what' and 'why'. Use sections: Goal, User Stories, Acceptance Criteria, Edge Cases."},
                {"role": "user", "content": f"Goal: {prompt}\n\nCodebase Context:\n{context}"}
            ]
        )
        spec_content = response.choices[0].message.content
        with open(self.spec_path, "w") as f:
            f.write(spec_content)
        print(f"Specification saved to {self.spec_path}")

    def plan(self):
        if not os.path.exists(self.spec_path):
            print("Error: spec.md not found. Run 'specify' first.")
            return
        print("Generating technical plan...")
        with open(self.spec_path, "r") as f:
            spec = f.read()
        context = self._get_codebase_context()
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a software architect. Generate a technical implementation plan (plan.md) based on the functional specification and codebase context. Focus on 'how'. Use sections: Architecture Overview, File Changes, Dependencies, Testing Strategy."},
                {"role": "user", "content": f"Specification:\n{spec}\n\nCodebase Context:\n{context}"}
            ]
        )
        plan_content = response.choices[0].message.content
        with open(self.plan_path, "w") as f:
            f.write(plan_content)
        print(f"Plan saved to {self.plan_path}")

    def tasks(self):
        if not os.path.exists(self.plan_path):
            print("Error: plan.md not found. Run 'plan' first.")
            return
        print("Generating executable task list...")
        with open(self.plan_path, "r") as f:
            plan = f.read()
        
        system_prompt = """You are a technical lead. Break the technical plan into atomic, executable tasks.
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

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Technical Plan:\n{plan}"}
            ]
        )
        tasks_content = response.choices[0].message.content
        with open(self.tasks_path, "w") as f:
            f.write(tasks_content)
        print(f"Tasks saved to {self.tasks_path}")

    def work(self):
        if not os.path.exists(self.tasks_path):
            print("Error: tasks.md not found. Run 'tasks' first.")
            return
        
        with open(self.tasks_path, "r") as f:
            content = f.read()
        
        # Extract YAML
        try:
            yaml_part = content.split("---yaml")[1].split("---")[0]
            tasks_data = yaml.safe_load(yaml_part)
        except Exception as e:
            print(f"Error parsing tasks.md: {e}")
            return

        next_task = None
        for task in tasks_data.get("tasks", []):
            if task["status"] == "pending":
                next_task = task
                break
        
        if not next_task:
            print("No pending tasks found.")
            return

        print(f"Working on task {next_task['id']}: {next_task['description']}")
        
        # Implementation logic would go here
        # For this MVP, we'll simulate the implementation by calling the LLM to generate the code change
        self._execute_task(next_task, tasks_data, content)

    def _execute_task(self, task, tasks_data, full_content):
        # Read context files
        context_content = ""
        for cf in task.get("context_files", []):
            full_cf_path = os.path.join(self.root_dir, cf)
            if os.path.exists(full_cf_path):
                with open(full_cf_path, "r") as f:
                    context_content += f"\nFile: {cf}\nContent:\n{f.read()}\n"

        # If editing, read the target file
        target_file_content = ""
        if task["action"] == "edit_file" and os.path.exists(os.path.join(self.root_dir, task["path"])):
            with open(os.path.join(self.root_dir, task["path"]), "r") as f:
                target_file_content = f.read()

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": f"You are a senior developer. Execute the following task: {task['description']}. Action: {task['action']} on {task['path']}. Output ONLY the full content of the file after the change. No markdown blocks, no explanation."},
                {"role": "user", "content": f"Context Files:\n{context_content}\n\nTarget File Current Content:\n{target_file_content}"}
            ]
        )
        
        new_content = response.choices[0].message.content.strip()
        # Clean up potential markdown code blocks if the LLM ignored the "ONLY" instruction
        if new_content.startswith("```"):
            lines = new_content.split("\n")
            if lines[0].startswith("```"):
                new_content = "\n".join(lines[1:-1])

        # Write the change
        target_path = os.path.join(self.root_dir, task["path"])
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w") as f:
            f.write(new_content)
        
        print(f"Task {task['id']} completed. Updated {task['path']}")

        # Update status in tasks.md
        task["status"] = "completed"
        new_yaml = yaml.dump(tasks_data, default_flow_style=False)
        updated_content = full_content.replace(full_content.split("---yaml")[1].split("---")[0], "\n" + new_yaml + "\n")
        
        # Also update the human-readable checklist (simple string replace for MVP)
        desc = task['description']
        updated_content = updated_content.replace(f"- [ ] {desc}", f"- [x] {desc}")

        with open(self.tasks_path, "w") as f:
            f.write(updated_content)

    def status(self):
        print("--- Agentic Layer Status ---")
        for file, name in [(self.spec_path, "Specification"), (self.plan_path, "Plan"), (self.tasks_path, "Tasks")]:
            status = "Exists" if os.path.exists(file) else "Missing"
            print(f"{name}: {status}")
        
        if os.path.exists(self.tasks_path):
            with open(self.tasks_path, "r") as f:
                content = f.read()
            try:
                yaml_part = content.split("---yaml")[1].split("---")[0]
                tasks_data = yaml.safe_load(yaml_part)
                completed = sum(1 for t in tasks_data.get("tasks", []) if t["status"] == "completed")
                total = len(tasks_data.get("tasks", []))
                print(f"Progress: {completed}/{total} tasks completed.")
            except:
                print("Progress: Could not parse tasks.md")
