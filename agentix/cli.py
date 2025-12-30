import argparse
import os
import sys
from pathlib import Path
from .orchestrator import Orchestrator
from .config import Config
from .interactive import SetupWizard, InteractivePrompt, ColoredOutput
from .commands import ProviderCommands, ConfigCommands, ModelCommands, ToolCommands, PluginCommands
from .diff_utils import DiffViewer
from .code_viewer import CodeViewer
from .syntax_highlighter import ColorScheme
from .tools import ToolManager
from .plugins import PluginManager


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
        help="🤖 Manage models for providers"
    )
    models_subparsers = models_parser.add_subparsers(dest="models_command")

    # List models
    list_models_parser = models_subparsers.add_parser(
        "list",
        help="List available models for a provider"
    )
    list_models_parser.add_argument(
        "provider_name",
        nargs="?",
        help="Provider name (interactive if not specified)"
    )

    # Select model
    select_model_parser = models_subparsers.add_parser(
        "select",
        help="Interactively select a model for a provider"
    )
    select_model_parser.add_argument(
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

    # === TOOLS & MCP ===

    tools_parser = subparsers.add_parser(
        "tools",
        help="🔧 Manage tools and MCP servers"
    )
    tools_subparsers = tools_parser.add_subparsers(dest="tools_command")

    tools_subparsers.add_parser(
        "list",
        help="List all available tools"
    )

    add_mcp_parser = tools_subparsers.add_parser(
        "add",
        help="Add an MCP server"
    )
    add_mcp_parser.add_argument(
        "server_name",
        nargs="?",
        help="Server name (interactive if not specified)"
    )

    remove_mcp_parser = tools_subparsers.add_parser(
        "remove",
        help="Remove an MCP server"
    )
    remove_mcp_parser.add_argument(
        "server_name",
        nargs="?",
        help="Server name (interactive if not specified)"
    )

    tools_subparsers.add_parser(
        "servers",
        help="List configured MCP servers"
    )

    test_tool_parser = tools_subparsers.add_parser(
        "test",
        help="Test a tool execution"
    )
    test_tool_parser.add_argument(
        "tool_name",
        nargs="?",
        help="Tool to test (interactive if not specified)"
    )

    # === PLUGINS ===

    plugins_parser = subparsers.add_parser(
        "plugins",
        help="🔌 Manage plugins"
    )
    plugins_subparsers = plugins_parser.add_subparsers(dest="plugins_command")

    plugins_subparsers.add_parser(
        "list",
        help="List installed plugins"
    )

    plugins_subparsers.add_parser(
        "discover",
        help="Discover available plugins"
    )

    enable_plugin_parser = plugins_subparsers.add_parser(
        "enable",
        help="Enable a plugin"
    )
    enable_plugin_parser.add_argument(
        "plugin_name",
        nargs="?",
        help="Plugin to enable (interactive if not specified)"
    )

    disable_plugin_parser = plugins_subparsers.add_parser(
        "disable",
        help="Disable a plugin"
    )
    disable_plugin_parser.add_argument(
        "plugin_name",
        nargs="?",
        help="Plugin to disable (interactive if not specified)"
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

    # View command - File preview with syntax highlighting
    view_parser = subparsers.add_parser(
        "view",
        help="👁️  View file with syntax highlighting"
    )
    view_parser.add_argument(
        "file",
        nargs="?",
        help="File to view (interactive if not specified)"
    )
    view_parser.add_argument(
        "--no-line-numbers",
        action="store_true",
        help="Hide line numbers"
    )
    view_parser.add_argument(
        "--start",
        type=int,
        help="Starting line number (1-indexed)"
    )
    view_parser.add_argument(
        "--end",
        type=int,
        help="Ending line number (1-indexed)"
    )
    view_parser.add_argument(
        "--theme",
        choices=["dark", "light", "monokai", "dracula"],
        default="dark",
        help="Color theme (default: dark)"
    )
    view_parser.add_argument(
        "--info",
        action="store_true",
        help="Show file information and statistics"
    )
    view_parser.add_argument(
        "--search",
        help="Search for a term in the file"
    )
    view_parser.add_argument(
        "--context",
        type=int,
        default=2,
        help="Number of context lines around search results (default: 2)"
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
            handle_models_command(args, orchestrator)

        elif args.command == "context":
            handle_context_command(args, orchestrator)

        elif args.command == "tools":
            handle_tools_command(args, orchestrator)

        elif args.command == "plugins":
            handle_plugins_command(args, orchestrator)

        elif args.command == "review":
            orchestrator.review()

        elif args.command == "history":
            orchestrator.history(limit=args.limit)

        elif args.command == "rollback":
            orchestrator.rollback(task_id=args.task_id)

        elif args.command == "diff":
            handle_diff_command(args, orchestrator)

        elif args.command == "view":
            handle_view_command(args, orchestrator)

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
  agentix setup         Interactive setup wizard
  agentix providers     Manage AI providers
  agentix models select Interactive model selection 🆕
  agentix specify       Start a new project

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
        model_commands = ModelCommands(orchestrator, orchestrator.config)
        provider_name = getattr(args, 'provider_name', None)
        model_commands.list_models(provider_name)

    elif args.providers_command == "set-model":
        provider_name = getattr(args, 'provider_name', None)
        provider_commands.set_default_model(provider_name)


def handle_models_command(args, orchestrator):
    """Handle models subcommands"""
    model_commands = ModelCommands(orchestrator, orchestrator.config)

    if not args.models_command or args.models_command == "list":
        provider_name = getattr(args, 'provider_name', None)
        model_commands.list_models(provider_name)

    elif args.models_command == "select":
        provider_name = getattr(args, 'provider_name', None)
        model_commands.select_model(provider_name)


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


def handle_tools_command(args, orchestrator):
    """Handle tools subcommands"""
    # Initialize tool manager if not already done
    if not hasattr(orchestrator, 'tool_manager') or orchestrator.tool_manager is None:
        orchestrator.tool_manager = ToolManager(orchestrator.config)

    tool_commands = ToolCommands(orchestrator.config, orchestrator.tool_manager)

    if not args.tools_command or args.tools_command == "list":
        tool_commands.list_tools()

    elif args.tools_command == "add":
        server_name = getattr(args, 'server_name', None)
        tool_commands.add_mcp_server(server_name)

    elif args.tools_command == "remove":
        server_name = getattr(args, 'server_name', None)
        tool_commands.remove_mcp_server(server_name)

    elif args.tools_command == "servers":
        tool_commands.list_mcp_servers()

    elif args.tools_command == "test":
        tool_name = getattr(args, 'tool_name', None)
        tool_commands.test_tool(tool_name)


def handle_plugins_command(args, orchestrator):
    """Handle plugins subcommands"""
    # Initialize plugin manager if not already done
    if not hasattr(orchestrator, 'plugin_manager') or orchestrator.plugin_manager is None:
        plugin_dirs = [Path(d) for d in orchestrator.config.get_plugin_directories()]
        orchestrator.plugin_manager = PluginManager(plugin_dirs)

        # Auto-load plugins if configured
        if orchestrator.config.should_auto_load_plugins():
            orchestrator.plugin_manager.load_all_plugins()

    plugin_commands = PluginCommands(orchestrator.config, orchestrator.plugin_manager)

    if not args.plugins_command or args.plugins_command == "list":
        plugin_commands.list_plugins()

    elif args.plugins_command == "discover":
        plugin_commands.discover_plugins()

    elif args.plugins_command == "enable":
        plugin_name = getattr(args, 'plugin_name', None)
        plugin_commands.enable_plugin(plugin_name)

    elif args.plugins_command == "disable":
        plugin_name = getattr(args, 'plugin_name', None)
        plugin_commands.disable_plugin(plugin_name)


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


def handle_view_command(args, orchestrator):
    """Handle view command for file preview with syntax highlighting"""
    # Get file to view
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
            "Select file to view:",
            files[:20]  # Show first 20 files
        )

    if not os.path.exists(file_path):
        ColoredOutput.error(f"File not found: {file_path}")
        return

    # Map theme name to ColorScheme enum
    theme_map = {
        "dark": ColorScheme.DARK,
        "light": ColorScheme.LIGHT,
        "monokai": ColorScheme.MONOKAI,
        "dracula": ColorScheme.DRACULA,
    }
    theme = theme_map.get(args.theme, ColorScheme.DARK)

    # Create code viewer
    viewer = CodeViewer(theme=theme)

    # Show file info if requested
    if args.info:
        ColoredOutput.header(f"\n👁️  File Information\n")
        info = viewer.show_file_info(file_path)
        print(info)
        print()
        return

    # Search in file if requested
    if args.search:
        ColoredOutput.header(f"\n🔍 Search Results\n")
        results = viewer.search_in_file(
            file_path,
            args.search,
            context_lines=args.context
        )
        print(results)
        print()
        return

    # View the file
    ColoredOutput.header(f"\n👁️  Viewing: {ColoredOutput.BRIGHT_CYAN}{file_path}{ColoredOutput.RESET}\n")

    output = viewer.view_file(
        file_path,
        show_line_numbers=not args.no_line_numbers,
        start_line=args.start,
        end_line=args.end
    )

    print(output)
    print()


if __name__ == "__main__":
    main()
