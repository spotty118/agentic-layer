import argparse
import os
import sys
from .orchestrator import Orchestrator

def main():
    parser = argparse.ArgumentParser(description="Agentic Layer: A spec-driven CLI for codebase operations.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    subparsers.add_parser("init", help="Initialize the agentic layer in the current codebase.")

    # specify
    specify_parser = subparsers.add_parser("specify", help="Generate or update the functional specification.")
    specify_parser.add_argument("prompt", help="The high-level goal or feature description.")

    # plan
    subparsers.add_parser("plan", help="Generate a technical implementation plan.")

    # tasks
    subparsers.add_parser("tasks", help="Break the plan into an executable task list.")

    # work
    subparsers.add_parser("work", help="Execute the next pending task.")

    # status
    subparsers.add_parser("status", help="Show the current progress and state.")

    args = parser.parse_args()

    orchestrator = Orchestrator(os.getcwd())

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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
