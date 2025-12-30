"""
Interactive commands for Agentix CLI

All the interactive terminal commands:
- Provider management
- Configuration
- Model selection
- Context management
- Tool management
- Plugin management
"""

import os
from pathlib import Path
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

    def __init__(self, orchestrator, config: Config = None):
        self.orchestrator = orchestrator
        self.config = config

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

    def select_model(self, provider_name: str = None):
        """Interactively select a model for a provider"""
        # Select provider if not specified
        if not provider_name:
            available_providers = self.orchestrator.router.get_available_providers()
            if not available_providers:
                ColoredOutput.error("No providers available!")
                return

            ColoredOutput.header("\n🤖 Select Model\n")
            provider_name = InteractivePrompt.select(
                "Which provider?",
                available_providers
            )

        provider = self.orchestrator.router.providers.get(provider_name)
        if not provider:
            ColoredOutput.error(f"Provider {provider_name} not available")
            return

        # Get current model
        current_model = provider.default_model
        print(f"\nCurrent model: {ColoredOutput.CYAN}{current_model}{ColoredOutput.RESET}")

        # Fetch available models
        if not hasattr(provider, 'get_available_models'):
            ColoredOutput.warning(f"\n{provider_name} doesn't support dynamic model fetching")
            new_model = InteractivePrompt.input_text(
                "Enter model name manually",
                default=current_model
            )
        else:
            ColoredOutput.info("\nFetching available models...")
            try:
                models = provider.get_available_models()

                if not models:
                    ColoredOutput.warning("No models found. Enter manually.")
                    new_model = InteractivePrompt.input_text(
                        "Model name",
                        default=current_model
                    )
                else:
                    # Prepare model choices with descriptions
                    print(f"\n{ColoredOutput.CYAN}Available models:{ColoredOutput.RESET}\n")

                    model_choices = []
                    for idx, model in enumerate(models, 1):
                        model_id = model.get('id', model.get('name', ''))
                        model_name = model.get('name', model_id)
                        model_desc = model.get('description', '')

                        # Display model info
                        print(f"  {idx}. {ColoredOutput.BOLD}{model_id}{ColoredOutput.RESET}")
                        if model_desc:
                            print(f"     {model_desc}")

                        model_choices.append(model_id)

                    print()

                    # Let user select from the list
                    selected_model = InteractivePrompt.select(
                        "Select a model",
                        model_choices
                    )

                    new_model = selected_model

            except Exception as e:
                ColoredOutput.error(f"Error fetching models: {str(e)}")
                new_model = InteractivePrompt.input_text(
                    "Enter model name manually",
                    default=current_model
                )

        # Confirm and save
        if new_model != current_model:
            if InteractivePrompt.confirm(f"\nSet default model to {new_model}?", default=True):
                # Save to config
                if self.config:
                    self.config.set(f"providers.{provider_name}.default_model", new_model)
                    self.config.save()
                    ColoredOutput.success(f"\n✓ Default model for {provider_name} set to {new_model}")
                    print(f"{ColoredOutput.YELLOW}Restart agentix for changes to take effect{ColoredOutput.RESET}")
                else:
                    ColoredOutput.warning("\nConfig not available. Changes not saved.")
        else:
            ColoredOutput.info("\nNo changes made")


class ToolCommands:
    """Commands for managing tools and MCP servers"""

    def __init__(self, config: Config, tool_manager=None):
        self.config = config
        self.tool_manager = tool_manager

    def list_tools(self, source: str = None):
        """List all available tools"""
        if not self.tool_manager:
            ColoredOutput.error("Tool system not initialized!")
            return

        ColoredOutput.header("\n🔧 Available Tools\n")

        tools = self.tool_manager.registry.list_tools(source=source)

        if not tools:
            ColoredOutput.warning("No tools available!")
            if self.config.is_mcp_enabled():
                print("\nAdd MCP servers with: agentix tools add")
            return

        # Group by source
        by_source = {}
        for tool in tools:
            tool_source = self.tool_manager.registry.get_source(tool.name)
            if tool_source not in by_source:
                by_source[tool_source] = []
            by_source[tool_source].append(tool)

        for source_name, source_tools in by_source.items():
            print(f"\n{ColoredOutput.CYAN}{source_name}{ColoredOutput.RESET}")
            for tool in source_tools:
                print(f"  • {ColoredOutput.GREEN}{tool.name}{ColoredOutput.RESET}")
                print(f"    {tool.description}")

        print(f"\n{ColoredOutput.BOLD}Total: {len(tools)} tools{ColoredOutput.RESET}\n")

    def add_mcp_server(self, server_name: str = None):
        """Add an MCP server"""
        ColoredOutput.header("\n➕ Add MCP Server\n")

        if not server_name:
            server_name = InteractivePrompt.input_text("Server name (unique identifier)")

        # Get transport type
        transport = InteractivePrompt.select(
            "Transport type",
            ["stdio", "http", "sse"]
        )

        server_config = {
            "name": server_name,
            "transport": transport,
            "enabled": True
        }

        if transport == "stdio":
            command = InteractivePrompt.input_text("Command to execute")
            args_str = InteractivePrompt.input_text("Arguments (space-separated)", default="")
            args = args_str.split() if args_str else []

            server_config["command"] = command
            server_config["args"] = args

            # Optional environment variables
            if InteractivePrompt.confirm("Add environment variables?", default=False):
                env = {}
                while True:
                    key = InteractivePrompt.input_text("Environment variable name (empty to finish)")
                    if not key:
                        break
                    value = InteractivePrompt.input_text(f"Value for {key}")
                    env[key] = value

                if env:
                    server_config["env"] = env

        else:  # http or sse
            url = InteractivePrompt.input_text(f"{transport.upper()} URL")
            server_config["url"] = url

        # Save configuration
        self.config.add_mcp_server(server_config)
        self.config.save()

        ColoredOutput.success(f"\n✓ MCP server '{server_name}' added!")
        print(f"{ColoredOutput.YELLOW}Restart agentix to connect to the server{ColoredOutput.RESET}")

    def remove_mcp_server(self, server_name: str = None):
        """Remove an MCP server"""
        servers = self.config.get_mcp_servers()

        if not servers:
            ColoredOutput.warning("No MCP servers configured!")
            return

        if not server_name:
            server_names = [s["name"] for s in servers]
            server_name = InteractivePrompt.select(
                "Which server to remove?",
                server_names
            )

        if InteractivePrompt.confirm(f"Remove MCP server '{server_name}'?", default=False):
            if self.config.remove_mcp_server(server_name):
                self.config.save()
                ColoredOutput.success(f"✓ MCP server '{server_name}' removed!")
            else:
                ColoredOutput.error(f"Server '{server_name}' not found!")

    def list_mcp_servers(self):
        """List configured MCP servers"""
        ColoredOutput.header("\n📡 MCP Servers\n")

        servers = self.config.get_mcp_servers()

        if not servers:
            ColoredOutput.warning("No MCP servers configured!")
            print("\nAdd a server with: agentix tools add")
            return

        for server in servers:
            name = server.get("name", "Unknown")
            transport = server.get("transport", "unknown")
            enabled = server.get("enabled", True)

            status = f"{ColoredOutput.GREEN}✓ enabled" if enabled else f"{ColoredOutput.RED}✗ disabled"

            print(f"\n{ColoredOutput.BOLD}{name}{ColoredOutput.RESET} ({transport}) [{status}{ColoredOutput.RESET}]")

            if transport == "stdio":
                cmd = server.get("command", "")
                args = " ".join(server.get("args", []))
                print(f"  Command: {cmd} {args}")
            else:
                url = server.get("url", "")
                print(f"  URL: {url}")

        print()

    def test_tool(self, tool_name: str = None):
        """Test a tool execution"""
        if not self.tool_manager:
            ColoredOutput.error("Tool system not initialized!")
            return

        if not tool_name:
            tools = self.tool_manager.registry.list_names()
            if not tools:
                ColoredOutput.warning("No tools available!")
                return

            tool_name = InteractivePrompt.select("Which tool to test?", tools)

        tool = self.tool_manager.registry.get(tool_name)
        if not tool:
            ColoredOutput.error(f"Tool '{tool_name}' not found!")
            return

        ColoredOutput.header(f"\n🧪 Testing tool: {tool_name}\n")
        print(f"Description: {tool.description}\n")

        # Collect parameters
        params = {}
        for param in tool.parameters:
            if param.required:
                prompt = f"{param.name} ({param.type.value}) *required*"
            else:
                prompt = f"{param.name} ({param.type.value}) [optional]"

            value = InteractivePrompt.input_text(prompt, default=str(param.default) if param.default else "")

            if value:
                # Try to convert to appropriate type
                if param.type.value == "integer":
                    try:
                        value = int(value)
                    except ValueError:
                        ColoredOutput.error(f"Invalid integer: {value}")
                        return
                elif param.type.value == "float":
                    try:
                        value = float(value)
                    except ValueError:
                        ColoredOutput.error(f"Invalid float: {value}")
                        return
                elif param.type.value == "boolean":
                    value = value.lower() in ["true", "yes", "1"]

                params[param.name] = value

        # Execute the tool
        ColoredOutput.info("\nExecuting tool...")

        result = self.tool_manager.executor.execute(tool_name, params)

        if result.success:
            ColoredOutput.success("\n✓ Tool executed successfully!")
            print(f"\nResult: {result.data}")
        else:
            ColoredOutput.error(f"\n✗ Tool execution failed!")
            print(f"Error: {result.error}")

        if result.metadata:
            print(f"\nMetadata: {result.metadata}")


class PluginCommands:
    """Commands for managing plugins"""

    def __init__(self, config: Config, plugin_manager=None):
        self.config = config
        self.plugin_manager = plugin_manager

    def list_plugins(self):
        """List all plugins"""
        if not self.plugin_manager:
            ColoredOutput.error("Plugin system not initialized!")
            return

        ColoredOutput.header("\n🔌 Installed Plugins\n")

        plugins = self.plugin_manager.list_plugins()

        if not plugins:
            ColoredOutput.warning("No plugins installed!")
            print("\nPlugin directories:")
            for directory in self.config.get_plugin_directories():
                print(f"  • {directory}")
            return

        for plugin_name in plugins:
            info = self.plugin_manager.get_plugin_info(plugin_name)
            if not info:
                continue

            status = f"{ColoredOutput.GREEN}✓" if info["enabled"] else f"{ColoredOutput.RED}✗"

            print(f"\n{status} {ColoredOutput.BOLD}{info['name']}{ColoredOutput.RESET} v{info['version']}")
            print(f"  Type: {info['type']}")
            print(f"  {info['description']}")
            if info.get('author'):
                print(f"  Author: {info['author']}")

        print()

    def discover_plugins(self):
        """Discover available plugins"""
        if not self.plugin_manager:
            ColoredOutput.error("Plugin system not initialized!")
            return

        ColoredOutput.header("\n🔍 Discovering Plugins\n")

        discovered = self.plugin_manager.discover_plugins()

        if not discovered:
            ColoredOutput.warning("No plugins found!")
            print("\nPlugin search directories:")
            for directory in self.config.get_plugin_directories():
                print(f"  • {directory}")
            return

        ColoredOutput.success(f"Found {len(discovered)} plugins:\n")

        for manifest in discovered:
            loaded = self.plugin_manager.is_loaded(manifest.name)
            status = f"{ColoredOutput.GREEN}loaded" if loaded else "not loaded"

            print(f"  • {ColoredOutput.BOLD}{manifest.name}{ColoredOutput.RESET} v{manifest.version} [{status}{ColoredOutput.RESET}]")
            print(f"    {manifest.description}")

        print()

    def enable_plugin(self, plugin_name: str = None):
        """Enable a plugin"""
        if not self.plugin_manager:
            ColoredOutput.error("Plugin system not initialized!")
            return

        if not plugin_name:
            plugins = self.plugin_manager.list_plugins()
            if not plugins:
                ColoredOutput.warning("No plugins available!")
                return

            plugin_name = InteractivePrompt.select("Which plugin to enable?", plugins)

        if self.plugin_manager.enable_plugin(plugin_name):
            ColoredOutput.success(f"✓ Plugin '{plugin_name}' enabled!")
            print(f"{ColoredOutput.YELLOW}Restart agentix for changes to take effect{ColoredOutput.RESET}")
        else:
            ColoredOutput.error(f"Failed to enable plugin '{plugin_name}'")

    def disable_plugin(self, plugin_name: str = None):
        """Disable a plugin"""
        if not self.plugin_manager:
            ColoredOutput.error("Plugin system not initialized!")
            return

        if not plugin_name:
            plugins = self.plugin_manager.list_plugins(enabled_only=True)
            if not plugins:
                ColoredOutput.warning("No enabled plugins!")
                return

            plugin_name = InteractivePrompt.select("Which plugin to disable?", plugins)

        if InteractivePrompt.confirm(f"Disable plugin '{plugin_name}'?", default=False):
            if self.plugin_manager.disable_plugin(plugin_name):
                ColoredOutput.success(f"✓ Plugin '{plugin_name}' disabled!")
                print(f"{ColoredOutput.YELLOW}Restart agentix for changes to take effect{ColoredOutput.RESET}")
            else:
                ColoredOutput.error(f"Failed to disable plugin '{plugin_name}'")
