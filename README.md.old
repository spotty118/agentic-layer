# Agentic Layer

A spec-driven CLI tool that uses AI agents to help you implement features in your codebase through a structured workflow.

## Overview

Agentic Layer follows a deliberate, spec-driven development workflow:

1. **Specify** - Generate a functional specification from your high-level goal
2. **Plan** - Create a technical implementation plan
3. **Tasks** - Break the plan into atomic, executable tasks
4. **Work** - Execute tasks one at a time with AI assistance
5. **Review** - Review and validate changes
6. **Status** - Track progress at any time

This approach ensures:
- Clear documentation of intent (the "why")
- Thoughtful technical design (the "how")
- Incremental, traceable changes
- Human oversight at each stage

## Installation

```bash
pip install -e .
```

Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Quick Start

```bash
# 1. Initialize in your codebase
agent init

# 2. Specify what you want to build
agent specify "Add user authentication with JWT tokens"

# 3. Generate a technical plan
agent plan

# 4. Break it into tasks
agent tasks

# 5. Execute tasks one by one
agent work
agent work  # Run again for next task

# 6. Check progress
agent status
```

## Commands

### `agent init`
Initialize the agentic layer in your codebase. Creates a `.agent/` directory to store specs, plans, and tasks.

### `agent specify <prompt>`
Generate a functional specification based on your high-level goal.

**Example:**
```bash
agent specify "Add a REST API endpoint for user profile updates"
```

Creates `.agent/spec.md` with:
- Goal and user stories
- Acceptance criteria
- Edge cases

### `agent plan`
Generate a technical implementation plan from the specification.

Creates `.agent/plan.md` with:
- Architecture overview
- File changes needed
- Dependencies
- Testing strategy

### `agent tasks`
Break the technical plan into executable tasks.

Creates `.agent/tasks.md` with:
- YAML-structured task list
- Task metadata (action type, file paths, status)
- Human-readable checklist

### `agent work`
Execute the next pending task using AI assistance.

- Reads context files
- Generates code changes
- Updates task status automatically

### `agent review`
Review generated changes before committing (coming soon).

### `agent status`
Show current progress and state of all artifacts.

## Workflow Example

Let's implement a new feature end-to-end:

```bash
# Initialize
cd my-project
agent init

# Specify the feature
agent specify "Add rate limiting to the API to prevent abuse"

# Review the spec
cat .agent/spec.md

# Generate implementation plan
agent plan

# Review the plan
cat .agent/plan.md

# Break into tasks
agent tasks

# Execute tasks
agent work    # Implements task 1
agent status  # Check progress
agent work    # Implements task 2
agent work    # Implements task 3

# Continue until all tasks complete
```

## Project Structure

```
your-project/
├── .agent/
│   ├── spec.md       # Functional specification
│   ├── plan.md       # Technical implementation plan
│   ├── tasks.md      # Executable task list
│   ├── config.yaml   # Configuration (optional)
│   └── history/      # Execution logs (coming soon)
└── ... your code ...
```

## Configuration

Create `.agent/config.yaml` to customize behavior:

```yaml
model: gpt-4.1-mini
max_context_files: 10
auto_commit: false
require_confirmation: true
```

## Task Format

Tasks in `tasks.md` follow this structure:

```yaml
tasks:
  - id: 1
    description: "Create middleware for rate limiting"
    status: pending  # pending | completed | failed
    action: create_file  # create_file | edit_file | delete_file | run_command
    path: "src/middleware/rateLimit.js"
    context_files:
      - "src/app.js"
      - "package.json"
```

## Supported Task Actions

- `create_file` - Create a new file
- `edit_file` - Modify an existing file
- `delete_file` - Remove a file
- `run_command` - Execute a shell command

## Advanced Usage

### Manual Task Editing
You can manually edit `.agent/tasks.md` to:
- Reorder tasks
- Add custom tasks
- Update task descriptions
- Mark tasks as completed/pending

### Custom Prompts
Modify the system prompts by editing `orchestrator.py` or use configuration overrides.

### Multiple Features
You can maintain multiple specs by creating separate directories:
```bash
mkdir -p .agent/features/auth
mkdir -p .agent/features/api
```

## Best Practices

1. **Review Before Executing** - Always review `spec.md` and `plan.md` before running `tasks`
2. **Commit Frequently** - Commit after each successful task execution
3. **Test As You Go** - Run tests after critical tasks
4. **Provide Context** - The more context in your `specify` prompt, the better
5. **Iterate** - Re-run `plan` or `tasks` if the output isn't quite right

## Troubleshooting

**Tasks not executing correctly?**
- Check that context files exist
- Verify the task action matches the file state
- Review the generated plan for clarity

**LLM outputting markdown instead of raw code?**
- The tool automatically strips code fences
- If issues persist, try regenerating with `agent tasks`

**Want to start over?**
```bash
rm -rf .agent/
agent init
```

## Roadmap

- [ ] Add `agent review` for change validation
- [ ] Add rollback/undo capabilities
- [ ] Enhanced logging and history
- [ ] Interactive mode with confirmations
- [ ] Support for other LLM providers (Anthropic, etc.)
- [ ] Plugin system for custom actions
- [ ] Web UI for visualization
- [ ] Multi-agent collaboration

## Contributing

This is an early-stage tool. Contributions welcome!

## License

MIT
