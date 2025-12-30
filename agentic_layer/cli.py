import argparse
import os
import sys
from .orchestrator import Orchestrator

def main():
    parser = argparse.ArgumentParser(
        description="Agentic Layer: A spec-driven CLI for codebase operations.",
        epilog="For more information, visit the documentation or run: agent <command> --help"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    subparsers.add_parser(
        "init",
        help="Initialize the agentic layer in the current codebase."
    )

    # specify
    specify_parser = subparsers.add_parser(
        "specify",
        help="Generate or update the functional specification."
    )
    specify_parser.add_argument(
        "prompt",
        help="The high-level goal or feature description."
    )

    # plan
    subparsers.add_parser(
        "plan",
        help="Generate a technical implementation plan from the specification."
    )

    # tasks
    subparsers.add_parser(
        "tasks",
        help="Break the plan into an executable task list."
    )

    # work
    subparsers.add_parser(
        "work",
        help="Execute the next pending task."
    )

    # status
    subparsers.add_parser(
        "status",
        help="Show the current progress and state."
    )

    # review
    subparsers.add_parser(
        "review",
        help="Review recent changes made by the agent."
    )

    # history
    history_parser = subparsers.add_parser(
        "history",
        help="Show execution history."
    )
    history_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of history entries to show (default: 10)"
    )

    # rollback
    rollback_parser = subparsers.add_parser(
        "rollback",
        help="Rollback recent changes (shows available backups)."
    )
    rollback_parser.add_argument(
        "--task-id",
        type=int,
        help="Specific task ID to rollback (optional)"
    )

    args = parser.parse_args()

    # Check if no command provided
    if not args.command:
        parser.print_help()
        sys.exit(0)

    orchestrator = Orchestrator(os.getcwd())

    try:
        if args.command == "init":
            orchestrator.init()
        elif args.command == "specify":
            orchestrator.specify(args.prompt)
        elif args.command == "plan":
            orchestrator.plan()
        elif args.command == "tasks":
            orchestrator.tasks()
        elif args.command == "work":
            orchestrator.work()
        elif args.command == "status":
            orchestrator.status()
        elif args.command == "review":
            orchestrator.review()
        elif args.command == "history":
            orchestrator.history(limit=args.limit)
        elif args.command == "rollback":
            orchestrator.rollback(task_id=args.task_id)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        from .logger import ColoredOutput
        ColoredOutput.warning("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        from .logger import ColoredOutput
        ColoredOutput.error(f"\n✗ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
