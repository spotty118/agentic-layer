"""
Interactive terminal utilities for Agentix

Provides rich, user-friendly terminal interactions:
- Setup wizards
- Interactive prompts
- Menu selections
- Provider configuration
- No file editing needed!
"""

import os
import sys
from typing import List, Dict, Any, Optional, Callable
from .logger import ColoredOutput


class InteractivePrompt:
    """Interactive terminal prompts and menus"""

    @staticmethod
    def confirm(message: str, default: bool = True) -> bool:
        """Ask yes/no question"""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{ColoredOutput.CYAN}? {message} [{default_str}]: {ColoredOutput.RESET}").strip().lower()

        if not response:
            return default

        return response in ['y', 'yes', 'true', '1']

    @staticmethod
    def input_text(message: str, default: Optional[str] = None, required: bool = False) -> str:
        """Get text input from user"""
        default_str = f" [{default}]" if default else ""
        prompt = f"{ColoredOutput.CYAN}? {message}{default_str}: {ColoredOutput.RESET}"

        while True:
            response = input(prompt).strip()

            if response:
                return response
            elif default:
                return default
            elif not required:
                return ""
            else:
                ColoredOutput.error("This field is required!")

    @staticmethod
    def input_secret(message: str, required: bool = True) -> str:
        """Get secret input (like API key) - masked"""
        import getpass
        prompt = f"{ColoredOutput.CYAN}? {message}: {ColoredOutput.RESET}"

        while True:
            response = getpass.getpass(prompt).strip()

            if response:
                return response
            elif not required:
                return ""
            else:
                ColoredOutput.error("This field is required!")

    @staticmethod
    def select(message: str, choices: List[str], default: Optional[int] = None) -> str:
        """Select from a list of choices"""
        print(f"\n{ColoredOutput.CYAN}? {message}{ColoredOutput.RESET}")

        for i, choice in enumerate(choices, 1):
            default_marker = " (default)" if default == i else ""
            print(f"  {i}. {choice}{default_marker}")

        while True:
            response = input(f"\n{ColoredOutput.CYAN}Select (1-{len(choices)}): {ColoredOutput.RESET}").strip()

            if not response and default:
                return choices[default - 1]

            try:
                choice_num = int(response)
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                else:
                    ColoredOutput.error(f"Please enter a number between 1 and {len(choices)}")
            except ValueError:
                ColoredOutput.error("Please enter a valid number")

    @staticmethod
    def multi_select(message: str, choices: List[str], defaults: Optional[List[str]] = None) -> List[str]:
        """Select multiple from a list"""
        defaults = defaults or []
        print(f"\n{ColoredOutput.CYAN}? {message} (space-separated numbers){ColoredOutput.RESET}")

        for i, choice in enumerate(choices, 1):
            selected = "✓" if choice in defaults else " "
            print(f"  [{selected}] {i}. {choice}")

        while True:
            response = input(f"\n{ColoredOutput.CYAN}Select (e.g., 1 3 5): {ColoredOutput.RESET}").strip()

            if not response:
                return defaults

            try:
                nums = [int(n) for n in response.split()]
                if all(1 <= n <= len(choices) for n in nums):
                    return [choices[n - 1] for n in nums]
                else:
                    ColoredOutput.error(f"All numbers must be between 1 and {len(choices)}")
            except ValueError:
                ColoredOutput.error("Please enter valid numbers separated by spaces")

    @staticmethod
    def menu(title: str, options: Dict[str, Callable], show_exit: bool = True):
        """Display interactive menu"""
        print(f"\n{ColoredOutput.BOLD}{title}{ColoredOutput.RESET}\n")

        items = list(options.items())
        for i, (name, _) in enumerate(items, 1):
            print(f"  {i}. {name}")

        if show_exit:
            print(f"  0. Exit")

        while True:
            try:
                choice = input(f"\n{ColoredOutput.CYAN}Select an option: {ColoredOutput.RESET}").strip()

                if not choice:
                    continue

                choice_num = int(choice)

                if choice_num == 0 and show_exit:
                    return None

                if 1 <= choice_num <= len(items):
                    _, func = items[choice_num - 1]
                    return func()
                else:
                    ColoredOutput.error(f"Please enter a number between 0 and {len(items)}")
            except ValueError:
                ColoredOutput.error("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n")
                return None


class SetupWizard:
    """Interactive setup wizard for Agentix"""

    def __init__(self, config):
        self.config = config

    def run(self):
        """Run the complete setup wizard"""
        ColoredOutput.header("\n🚀 Welcome to Agentix Setup Wizard!\n")

        print("Let's configure your AI providers and settings.")
        print("You can always change these later with 'agentix config'\n")

        # Step 1: Provider selection
        self.setup_providers()

        # Step 2: Shared context
        self.setup_shared_context()

        # Step 3: General settings
        self.setup_general()

        # Save configuration
        self.config.save()

        ColoredOutput.success("\n✓ Setup complete!")
        print("\nNext steps:")
        print("  1. Run 'agentix specify <goal>' to start")
        print("  2. Run 'agentix providers' to manage providers")
        print("  3. Run 'agentix config' to change settings\n")

    def setup_providers(self):
        """Interactive provider setup"""
        ColoredOutput.header("\n📦 Provider Setup\n")

        print("Select which AI providers you want to use:")
        print("(You can add more later with 'agentix providers add')\n")

        providers = [
            ("Claude", "claude", "Best for specs, planning, refactoring"),
            ("OpenAI/Codex", "openai", "Best for code generation"),
            ("Gemini", "gemini", "Fastest, largest context (2M tokens)"),
            ("OpenRouter", "openrouter", "Access to 100+ models"),
            ("Ollama", "ollama", "Local models (free, private)")
        ]

        for name, key, desc in providers:
            print(f"\n{ColoredOutput.BOLD}{name}{ColoredOutput.RESET} - {desc}")

            if InteractivePrompt.confirm(f"Enable {name}?", default=(key in ["claude", "openai", "gemini"])):
                self.config.set(f"providers.{key}.enabled", True)

                if key == "ollama":
                    base_url = InteractivePrompt.input_text(
                        "Ollama URL",
                        default="http://localhost:11434",
                        required=False
                    )
                    if base_url:
                        self.config.set(f"providers.{key}.base_url", base_url)
                elif key == "openrouter":
                    site_name = InteractivePrompt.input_text(
                        "Your app name (optional)",
                        default="Agentix",
                        required=False
                    )
                    if site_name:
                        self.config.set(f"providers.{key}.site_name", site_name)
                else:
                    # For API-based providers, remind about env vars
                    env_vars = {
                        "claude": "ANTHROPIC_API_KEY",
                        "openai": "OPENAI_API_KEY",
                        "gemini": "GOOGLE_API_KEY"
                    }
                    if key in env_vars:
                        print(f"  {ColoredOutput.YELLOW}→ Set {env_vars[key]} environment variable{ColoredOutput.RESET}")
            else:
                self.config.set(f"providers.{key}.enabled", False)

    def setup_shared_context(self):
        """Setup shared context window"""
        ColoredOutput.header("\n🔄 Shared Context Window\n")

        print("Shared context allows multiple AI models to collaborate:")
        print("  • Claude writes specs → OpenAI generates code → Gemini reviews")
        print("  • All models see each other's contributions")
        print("  • Better results through collaboration\n")

        if InteractivePrompt.confirm("Enable shared context?", default=False):
            self.config.set("shared_context.enabled", True)

            max_tokens = InteractivePrompt.input_text(
                "Max context tokens",
                default="200000"
            )
            self.config.set("shared_context.max_tokens", int(max_tokens))
        else:
            self.config.set("shared_context.enabled", False)

    def setup_general(self):
        """Setup general settings"""
        ColoredOutput.header("\n⚙️  General Settings\n")

        # Confirmation prompts
        if InteractivePrompt.confirm("Require confirmation before executing tasks?", default=True):
            self.config.set("require_confirmation", True)
        else:
            self.config.set("require_confirmation", False)

        # Temperature
        print("\nTemperature controls randomness (0.0 = focused, 1.0 = creative)")
        temp = InteractivePrompt.input_text("Temperature", default="0.7")
        try:
            self.config.set("temperature", float(temp))
        except ValueError:
            self.config.set("temperature", 0.7)
