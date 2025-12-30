# Example Workflows

This document contains example workflows demonstrating how to use Agentic Layer.

## Example 1: Adding a New REST API Endpoint

```bash
# Initialize the agentic layer
cd my-project
agent init

# Specify the feature
agent specify "Add a REST API endpoint for user profile updates that accepts PUT requests with JSON payload and validates input"

# Review the generated spec
cat .agent/spec.md

# Generate implementation plan
agent plan

# Review the plan
cat .agent/plan.md

# Generate tasks
agent tasks

# Review tasks
cat .agent/tasks.md

# Execute tasks one by one
agent work    # Task 1: Create route handler
agent status  # Check progress
agent work    # Task 2: Add validation middleware
agent work    # Task 3: Update tests
agent work    # Task 4: Update documentation

# Review all changes
agent review

# Check final status
agent status
```

## Example 2: Refactoring with Safety

```bash
# Start with a clear specification
agent specify "Refactor authentication module to use JWT tokens instead of session cookies"

# Generate plan
agent plan

# Generate tasks
agent tasks

# Before executing, review the plan carefully
cat .agent/plan.md

# Execute with confirmation prompts (enabled by default)
agent work
# Prompted: "Execute this task? (y/n):"
# Type 'y' to confirm

# If something goes wrong, check backups
ls .agent/backups/

# Review changes
agent review

# Check history
agent history --limit 5
```

## Example 3: Custom Configuration

Create `.agent/config.yaml`:

```yaml
model: gpt-4.1-mini
temperature: 0.5
max_tokens: 8192
require_confirmation: true
auto_commit: false

logging:
  enabled: true
  level: DEBUG
  save_history: true

prompts:
  specify: |
    You are a product manager specializing in API design.
    Generate a detailed functional specification focusing on:
    - Clear API contracts
    - Data validation rules
    - Error handling scenarios
    - Security considerations
```

Then run your workflow:

```bash
agent specify "Add rate limiting to prevent API abuse"
agent plan
agent tasks
agent work
```

## Example 4: Working with Multiple Features

```bash
# Feature 1: Authentication
mkdir -p .agent/features/auth
cd .agent/features/auth
agent init
agent specify "Implement OAuth2 authentication"
agent plan
agent tasks

# Feature 2: API Enhancement (in parallel)
cd ../..
mkdir -p .agent/features/api
cd .agent/features/api
agent init
agent specify "Add GraphQL support alongside REST API"
agent plan
agent tasks

# Work on each feature independently
cd .agent/features/auth
agent work

cd ../api
agent work
```

## Example 5: Debugging and Recovery

```bash
# If a task fails
agent status
# Shows which task failed

# Check the error in history
agent history --limit 5

# Review what was attempted
agent review

# Check available backups
agent rollback
# Lists available backups

# Manually edit tasks.md to fix the problematic task
# Change the task description or action type
vi .agent/tasks.md

# Try again
agent work
```

## Example 6: CI/CD Integration

```bash
# In your CI/CD pipeline
export OPENAI_API_KEY="${SECRET_OPENAI_KEY}"

# Run in non-interactive mode (disable confirmations)
# Create config first
cat > .agent/config.yaml << EOF
require_confirmation: false
auto_commit: true
EOF

# Execute workflow
agent specify "Add automated testing for new features"
agent plan
agent tasks

# Execute all pending tasks
while agent work 2>/dev/null; do
  echo "Task completed, continuing..."
done

# Commit if successful
agent status
git add .
git commit -m "feat: Automated changes from agentic layer"
```

## Example 7: Code Review Workflow

```bash
# After completing tasks
agent status

# Review all changes
agent review

# Check specific file changes
git diff .agent/backups/some_file.py_20240115_143022.bak path/to/some_file.py

# If changes look good
git add .
git commit -m "feat: Implemented feature XYZ"

# If you want to rollback
agent rollback
# Follow manual instructions to restore files
```

## Example 8: Iterative Development

```bash
# Start with high-level specification
agent specify "Build a user notification system"

# Generate initial plan
agent plan

# Review and realize you need more detail
# Re-specify with more context
agent specify "Build a user notification system supporting email, SMS, and push notifications with template management and delivery tracking"

# Regenerate plan with better context
agent plan

# Now generate tasks
agent tasks

# Execute incrementally
agent work  # Creates notification service base
agent work  # Adds email provider
# ... continue until done
```

## Tips and Best Practices

1. **Always review before executing**: Use `cat .agent/spec.md` and `cat .agent/plan.md` before running `tasks`

2. **Small iterations**: Break large features into smaller specifications

3. **Backup frequently**: The tool creates backups automatically, but commit to git often

4. **Use history**: `agent history` helps understand what happened

5. **Customize prompts**: Tailor system prompts in config.yaml for your project style

6. **Validate as you go**: Run tests after each task completion:
   ```bash
   agent work && npm test
   ```

7. **Review changes**: Always use `agent review` before committing

8. **Non-interactive mode**: For automation, set `require_confirmation: false` in config

9. **Keep context files updated**: Ensure `context_files` in tasks reference the right files

10. **Log everything**: Keep `logging.enabled: true` for debugging
