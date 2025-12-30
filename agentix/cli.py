import argparse
import os
import sys
from .orchestrator import Orchestrator
from .config import Config
from .interactive import SetupWizard, InteractivePrompt, ColoredOutput
from .commands import ProviderCommands, ConfigCommands, ModelCommands
from .diff_utils import DiffViewer


def main():
    parser = argparse.ArgumentParser(
        description="Agentix: Multi-AI spec-driven coding agent with unlimited provider support",
        epilog="Interactive commands - no file editing needed! Run 'agentix setup' to get started."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # === SETUP & CONFIGURATION ===

    subparsers.add_parser(
        "setup",
        help="🚀 Interactive setup wizard - configure providers and settings"
    )

    subparsers.add_parser(
        "config",
        help="⚙️  Interactive configuration menu"
    )

    # === CORE WORKFLOW ===

    subparsers.add_parser(
        "init",
        help="Initialize Agentix in the current codebase"
    )

    specify_parser = subparsers.add_parser(
        "specify",
        help="📝 Generate functional specification from goal"
    )
    specify_parser.add_argument(
        "prompt",
        nargs="?",  # Make optional for interactive mode
        help="The high-level goal or feature description"
    )

    subparsers.add_parser(
        "plan",
        help="🏗️  Generate technical implementation plan"
    )

    subparsers.add_parser(
        "tasks",
        help="📋 Break plan into executable tasks"
    )

    subparsers.add_parser(
        "work",
        help="⚙️  Execute the next pending task"
    )

    subparsers.add_parser(
        "status",
        help="📊 Show current progress and state"
    )

    # === PROVIDER MANAGEMENT ===

    providers_parser = subparsers.add_parser(
        "providers",
        help="📦 Manage AI providers (list/add/remove)"
    )
    providers_subparsers = providers_parser.add_subparsers(dest="providers_command")

    providers_subparsers.add_parser(
        "list",
        help="List all configured providers"
    )

    add_provider_parser = providers_subparsers.add_parser(
        "add",
        help="Add a new provider"
    )
    add_provider_parser.add_argument(
        "provider_name",
        nargs="?",
        choices=["claude", "openai", "gemini", "openrouter", "ollama"],
        help="Provider to add (interactive if not specified)"
    )

    remove_provider_parser = providers_subparsers.add_parser(
        "remove",
        help="Remove a provider"
    )
    remove_provider_parser.add_argument(
        "provider_name",
        nargs="?",
        help="Provider to remove (interactive if not specified)"
    )

    model_provider_parser = providers_subparsers.add_parser(
        "models",
        help="List available models for a provider"
    )
    model_provider_parser.add_argument(
        "provider_name",
        nargs="?",
        help="Provider name (interactive if not specified)"
    )

    set_model_parser = providers_subparsers.add_parser(
        "set-model",
        help="Set default model for a provider"
    )
    set_model_parser.add_argument(
        "provider_name",
        nargs="?",
        help="Provider name (interactive if not specified)"
    )

    # === MODELS ===

    models_parser = subparsers.add_parser(
        "models",
        help="🤖 List available models for providers"
    )
    models_parser.add_argument(
        "provider_name",
        nargs="?",
        help="Provider name (interactive if not specified)"
    )

    # === CONTEXT MANAGEMENT ===

    context_parser = subparsers.add_parser(
        "context",
        help="🔄 Manage shared context window"
    )
    context_subparsers = context_parser.add_subparsers(dest="context_command")

    context_subparsers.add_parser(
        "show",
        help="Show current context summary"
    )

    context_subparsers.add_parser(
        "clear",
        help="Clear shared context"
    )

    context_subparsers.add_parser(
        "enable",
        help="Enable shared context"
    )

    context_subparsers.add_parser(
        "disable",
        help="Disable shared context"
    )

    # === REVIEW & HISTORY ===

    subparsers.add_parser(
        "review",
        help="🔍 Review recent changes"
    )

    history_parser = subparsers.add_parser(
        "history",
        help="📜 Show execution history"
    )
    history_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of entries to show (default: 10)"
    )

    rollback_parser = subparsers.add_parser(
        "rollback",
        help="⏮️  Show available backups for rollback"
    )
    rollback_parser.add_argument(
        "--task-id",
        type=int,
        help="Specific task ID to rollback (optional)"
    )

    # Diff command
    diff_parser = subparsers.add_parser(
        "diff",
        help="📊 View diffs for file changes"
    )
    diff_parser.add_argument(
        "file",
        nargs="?",
        help="File to show diff for (interactive if not specified)"
    )
    diff_parser.add_argument(
        "--backup",
        type=int,
        default=0,
        help="Backup index to compare against (0 = most recent, default: 0)"
    )
    diff_parser.add_argument(
        "--type",
        choices=["unified", "side-by-side"],
        default="unified",
        help="Diff format (default: unified)"
    )
    diff_parser.add_argument(
        "--compare",
        help="Compare with another file instead of backup"
    )

    # === UTILITIES ===

    subparsers.add_parser(
        "version",
        help="Show Agentix version"
    )

    args = parser.parse_args()

    # Check if no command provided
    if not args.command:
        show_welcome()
        parser.print_help()
        sys.exit(0)

    # Handle version command
    if args.command == "version":
        from . import __version__
        print(f"Agentix v{__version__}")
        sys.exit(0)

    # Handle setup command (doesn't need orchestrator)
    if args.command == "setup":
        run_setup()
        sys.exit(0)

    # Initialize orchestrator for other commands
    try:
        orchestrator = Orchestrator(os.getcwd())
    except RuntimeError as e:
        ColoredOutput.error(f"\n{str(e)}\n")
        print("Run 'agentix setup' to configure providers")
        sys.exit(1)

    # Handle commands
    try:
        if args.command == "init":
            orchestrator.init()

        elif args.command == "specify":
            if not args.prompt:
                # Interactive mode
                prompt = InteractivePrompt.input_text(
                    "What do you want to build?",
                    required=True
                )
            else:
                prompt = args.prompt
            orchestrator.specify(prompt)

        elif args.command == "plan":
            orchestrator.plan()

        elif args.command == "tasks":
            orchestrator.tasks()

        elif args.command == "work":
            orchestrator.work()

        elif args.command == "status":
            orchestrator.status()

        elif args.command == "config":
            config_commands = ConfigCommands(orchestrator.config)
            config_commands.interactive_config()

        elif args.command == "providers":
            handle_providers_command(args, orchestrator)

        elif args.command == "models":
            model_commands = ModelCommands(orchestrator)
            model_commands.list_models(args.provider_name)

        elif args.command == "context":
            handle_context_command(args, orchestrator)

        elif args.command == "review":
            orchestrator.review()

        elif args.command == "history":
            orchestrator.history(limit=args.limit)

        elif args.command == "rollback":
            orchestrator.rollback(task_id=args.task_id)

        elif args.command == "diff":
            handle_diff_command(args, orchestrator)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        ColoredOutput.warning("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        ColoredOutput.error(f"\n✗ Error: {str(e)}")
        import traceback
        if os.getenv("DEBUG"):
            traceback.print_exc()
        sys.exit(1)


def show_welcome():
    """Show welcome message"""
    print(f"""
{ColoredOutput.BOLD}Agentix - Multi-AI Spec-Driven Coding Agent{ColoredOutput.RESET}

Supports unlimited AI providers:
  📋 Claude - Superior reasoning and planning
  ⚡ OpenAI - Excellent code generation
  🚀 Gemini - Massive context, lightning fast
  🌐 OpenRouter - Access to 100+ models
  🏠 Ollama - Local models (free, private)

Get started:
  agentix setup      Interactive setup wizard
  agentix providers  Manage AI providers
  agentix specify    Start a new project

""")


def run_setup():
    """Run the interactive setup wizard"""
    # Create config if it doesn't exist
    agent_dir = os.path.join(os.getcwd(), ".agent")
    if not os.path.exists(agent_dir):
        os.makedirs(agent_dir)

    config = Config(agent_dir)
    wizard = SetupWizard(config)
    wizard.run()


def handle_providers_command(args, orchestrator):
    """Handle providers subcommands"""
    provider_commands = ProviderCommands(orchestrator.config, orchestrator)

    if not args.providers_command or args.providers_command == "list":
        provider_commands.list_providers()

    elif args.providers_command == "add":
        provider_name = getattr(args, 'provider_name', None)
        provider_commands.add_provider(provider_name)

    elif args.providers_command == "remove":
        provider_name = getattr(args, 'provider_name', None)
        provider_commands.remove_provider(provider_name)

    elif args.providers_command == "models":
        model_commands = ModelCommands(orchestrator)
        provider_name = getattr(args, 'provider_name', None)
        model_commands.list_models(provider_name)

    elif args.providers_command == "set-model":
        provider_name = getattr(args, 'provider_name', None)
        provider_commands.set_default_model(provider_name)


def handle_context_command(args, orchestrator):
    """Handle context subcommands"""
    if not args.context_command or args.context_command == "show":
        if orchestrator.router.shared_context:
            summary = orchestrator.router.shared_context.get_context_summary()
            ColoredOutput.header("\n🔄 Shared Context Window\n")
            for key, value in summary.items():
                print(f"  {key}: {value}")
            print()
        else:
            ColoredOutput.warning("Shared context is not enabled")
            print("Enable with: agentix context enable\n")

    elif args.context_command == "clear":
        if orchestrator.router.shared_context:
            if InteractivePrompt.confirm("Clear all context?", default=False):
                orchestrator.router.shared_context.clear()
                ColoredOutput.success("✓ Context cleared")
        else:
            ColoredOutput.warning("Shared context is not enabled")

    elif args.context_command == "enable":
        orchestrator.config.set("shared_context.enabled", True)
        orchestrator.config.save()
        ColoredOutput.success("✓ Shared context enabled")
        print("Restart agentix for changes to take effect\n")

    elif args.context_command == "disable":
        orchestrator.config.set("shared_context.enabled", False)
        orchestrator.config.save()
        ColoredOutput.success("✓ Shared context disabled")


def handle_diff_command(args, orchestrator):
    """Handle diff command"""
    diff_viewer = DiffViewer(orchestrator.agent_dir)

    # Get file to diff
    file_path = args.file
    if not file_path:
        # Interactive file selection
        import glob
        files = glob.glob("**/*", recursive=True)
        files = [f for f in files if os.path.isfile(f) and not f.startswith('.')]

        if not files:
            ColoredOutput.error("No files found in current directory")
            return

        file_path = InteractivePrompt.select(
            "Select file to view diff:",
            files[:20]  # Show first 20 files
        )

    if not os.path.exists(file_path):
        ColoredOutput.error(f"File not found: {file_path}")
        return

    # Generate diff
    if args.compare:
        # Compare with another file
        diff_text = diff_viewer.diff_files(file_path, args.compare, args.type)
        if not diff_text:
            ColoredOutput.error(f"Could not generate diff between {file_path} and {args.compare}")
            return
    else:
        # Compare with backup
        diff_text = diff_viewer.diff_with_backup(file_path, args.backup, args.type)
        if not diff_text:
            backups = diff_viewer.get_file_backups(file_path)
            if not backups:
                ColoredOutput.warning(f"No backups found for {file_path}")
                print("Make some changes first, or use --compare to compare with another file\n")
            else:
                ColoredOutput.error(f"Could not generate diff for backup index {args.backup}")
                print(f"Available backups: 0-{len(backups)-1}\n")
            return

    # Display diff
    ColoredOutput.header(f"\n📊 Diff for {file_path}\n")
    print(diff_text)

    # Show stats if unified diff
    if args.type == "unified":
        stats = diff_viewer.format_diff_stats(diff_text)
        print(f"\n{ColoredOutput.CYAN}{stats}{ColoredOutput.RESET}\n")


if __name__ == "__main__":
    main()
