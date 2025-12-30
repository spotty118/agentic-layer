"""
Interactive commands for Agentix CLI

All the interactive terminal commands:
- Provider management
- Configuration
- Model selection
- Context management
"""

import os
from .interactive import InteractivePrompt, ColoredOutput
from .config import Config


class ProviderCommands:
    """Commands for managing AI providers"""

    def __init__(self, config: Config, orchestrator):
        self.config = config
        self.orchestrator = orchestrator

    def list_providers(self):
        """List all configured providers"""
        ColoredOutput.header("\n📦 Configured Providers\n")

        if not self.orchestrator.router:
            ColoredOutput.error("No providers initialized. Run 'agentix setup' first.")
            return

        available = self.orchestrator.router.get_available_providers()

        if not available:
            ColoredOutput.warning("No providers available!")
            return

        for provider_name in available:
            info = self.orchestrator.router.get_provider_info(provider_name)
            print(f"\n{ColoredOutput.GREEN}✓ {provider_name}{ColoredOutput.RESET}")
            print(f"  Model: {info['default_model']}")
            print(f"  Max Context: {info['max_context']:,} tokens")
            print(f"  Capabilities: {', '.join(info['capabilities'][:3])}...")

    def add_provider(self, provider_name: str = None):
        """Interactively add a provider"""
        ColoredOutput.header("\n➕ Add AI Provider\n")

        providers = {
            "claude": "Anthropic Claude - Superior reasoning",
            "openai": "OpenAI/Codex - Excellent code generation",
            "gemini": "Google Gemini - Massive context, fast",
            "openrouter": "OpenRouter - Access 100+ models",
            "ollama": "Ollama - Local models (free)"
        }

        if not provider_name:
            print("Available providers:")
            for name, desc in providers.items():
                enabled = self.config.get(f"providers.{name}.enabled", False)
                status = "✓ enabled" if enabled else "  disabled"
                print(f"  [{status}] {name} - {desc}")

            provider_name = InteractivePrompt.select(
                "\nWhich provider do you want to add?",
                list(providers.keys())
            )

        # Enable the provider
        self.config.set(f"providers.{provider_name}.enabled", True)

        # Provider-specific setup
        if provider_name == "ollama":
            base_url = InteractivePrompt.input_text(
                "Ollama URL",
                default="http://localhost:11434"
            )
            self.config.set(f"providers.{provider_name}.base_url", base_url)

            print(f"\n{ColoredOutput.YELLOW}Make sure Ollama is running!{ColoredOutput.RESET}")
            print(f"  Start: ollama serve")
            print(f"  Pull model: ollama pull codellama")

        elif provider_name == "openrouter":
            print(f"\n{ColoredOutput.YELLOW}Set your OpenRouter API key:{ColoredOutput.RESET}")
            print(f"  export OPENROUTER_API_KEY='your-key'")

        else:
            env_vars = {
                "claude": "ANTHROPIC_API_KEY",
                "openai": "OPENAI_API_KEY",
                "gemini": "GOOGLE_API_KEY"
            }
            if provider_name in env_vars:
                print(f"\n{ColoredOutput.YELLOW}Set your API key:{ColoredOutput.RESET}")
                print(f"  export {env_vars[provider_name]}='your-key'")

        self.config.save()
        ColoredOutput.success(f"\n✓ {provider_name} enabled!")
        print("Restart agentix for changes to take effect.")

    def remove_provider(self, provider_name: str = None):
        """Remove a provider"""
        if not provider_name:
            available = [
                p for p in ["claude", "openai", "gemini", "openrouter", "ollama"]
                if self.config.get(f"providers.{p}.enabled", False)
            ]

            if not available:
                ColoredOutput.warning("No providers to remove!")
                return

            provider_name = InteractivePrompt.select(
                "Which provider do you want to remove?",
                available
            )

        if InteractivePrompt.confirm(f"Remove {provider_name}?", default=False):
            self.config.set(f"providers.{provider_name}.enabled", False)
            self.config.save()
            ColoredOutput.success(f"✓ {provider_name} removed!")

    def set_default_model(self, provider_name: str = None):
        """Set default model for a provider"""
        if not provider_name:
            available = self.orchestrator.router.get_available_providers()
            provider_name = InteractivePrompt.select(
                "Which provider?",
                available
            )

        current = self.config.get(f"providers.{provider_name}.default_model")
        print(f"\nCurrent: {current}")

        new_model = InteractivePrompt.input_text(
            "New default model",
            default=current
        )

        self.config.set(f"providers.{provider_name}.default_model", new_model)
        self.config.save()
        ColoredOutput.success(f"✓ Default model updated!")


class ConfigCommands:
    """Commands for managing configuration"""

    def __init__(self, config: Config):
        self.config = config

    def interactive_config(self):
        """Interactive configuration menu"""
        while True:
            result = InteractivePrompt.menu(
                "⚙️  Configuration Menu",
                {
                    "Toggle confirmation prompts": self.toggle_confirmation,
                    "Set temperature": self.set_temperature,
                    "Set max tokens": self.set_max_tokens,
                    "Enable/disable shared context": self.toggle_shared_context,
                    "View all settings": self.view_settings,
                }
            )

            if result is None:
                break

    def toggle_confirmation(self):
        """Toggle confirmation prompts"""
        current = self.config.get("require_confirmation", True)
        new_value = not current

        self.config.set("require_confirmation", new_value)
        self.config.save()

        status = "enabled" if new_value else "disabled"
        ColoredOutput.success(f"✓ Confirmation prompts {status}")

    def set_temperature(self):
        """Set temperature"""
        current = self.config.get("temperature", 0.7)
        print(f"\nCurrent: {current}")
        print("Temperature controls randomness:")
        print("  0.0 = Very focused and deterministic")
        print("  0.7 = Balanced (recommended)")
        print("  1.0 = Creative and varied\n")

        temp = InteractivePrompt.input_text("Temperature (0.0-1.0)", default=str(current))

        try:
            temp_float = float(temp)
            if 0.0 <= temp_float <= 1.0:
                self.config.set("temperature", temp_float)
                self.config.save()
                ColoredOutput.success(f"✓ Temperature set to {temp_float}")
            else:
                ColoredOutput.error("Temperature must be between 0.0 and 1.0")
        except ValueError:
            ColoredOutput.error("Invalid number")

    def set_max_tokens(self):
        """Set max tokens"""
        current = self.config.get("max_tokens", 4096)
        print(f"\nCurrent: {current}")

        tokens = InteractivePrompt.input_text("Max tokens", default=str(current))

        try:
            self.config.set("max_tokens", int(tokens))
            self.config.save()
            ColoredOutput.success(f"✓ Max tokens set to {tokens}")
        except ValueError:
            ColoredOutput.error("Invalid number")

    def toggle_shared_context(self):
        """Toggle shared context"""
        current = self.config.get("shared_context.enabled", False)
        new_value = not current

        self.config.set("shared_context.enabled", new_value)
        self.config.save()

        status = "enabled" if new_value else "disabled"
        ColoredOutput.success(f"✓ Shared context {status}")

        if new_value:
            print(f"\n{ColoredOutput.CYAN}Shared context allows multiple AI models to collaborate!{ColoredOutput.RESET}")

    def view_settings(self):
        """View all settings"""
        ColoredOutput.header("\n⚙️  Current Settings\n")

        settings = [
            ("Temperature", self.config.get("temperature")),
            ("Max Tokens", self.config.get("max_tokens")),
            ("Require Confirmation", self.config.get("require_confirmation")),
            ("Shared Context", self.config.get("shared_context.enabled")),
            ("Auto Commit", self.config.get("auto_commit")),
        ]

        for name, value in settings:
            print(f"  {name}: {ColoredOutput.CYAN}{value}{ColoredOutput.RESET}")

        print()


class ModelCommands:
    """Commands for model management"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def list_models(self, provider_name: str = None):
        """List available models"""
        if not provider_name:
            provider_name = InteractivePrompt.select(
                "Which provider?",
                self.orchestrator.router.get_available_providers()
            )

        ColoredOutput.header(f"\n🤖 Models for {provider_name}\n")

        provider = self.orchestrator.router.providers.get(provider_name)
        if not provider:
            ColoredOutput.error(f"Provider {provider_name} not available")
            return

        # Try to get model list from provider
        if hasattr(provider, 'get_available_models'):
            models = provider.get_available_models()
            if models:
                for model in models[:20]:  # Show first 20
                    model_id = model.get('id', model.get('name', ''))
                    print(f"  • {model_id}")
            else:
                print(f"  Default: {provider.default_model}")
        else:
            print(f"  Default: {provider.default_model}")
