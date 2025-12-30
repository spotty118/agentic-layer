"""
Intelligent Provider Router for Agentix

Routes tasks to the optimal AI provider based on:
- Task type and requirements
- Provider capabilities and strengths
- Context size
- User preferences
- Availability
"""

from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability
from .claude import ClaudeProvider
from .openai import OpenAIProvider
from .gemini import GeminiProvider
from .openrouter import OpenRouterProvider
from .ollama import OllamaProvider
from .claude_cli import ClaudeCLIProvider
from .openai_cli import OpenAICLIProvider
from .gemini_cli import GeminiCLIProvider


class ProviderRouter:
    """
    Intelligently routes tasks to optimal AI providers.

    Supports unlimited providers - configure as many as you want!
    """

    # Best provider for each task type based on strengths
    # CLI providers are prioritized when available (use authenticated tools, no API keys needed)
    TASK_PREFERENCES = {
        "specification": ["claude_cli", "claude", "openai_cli", "openai", "gemini_cli", "gemini", "openrouter", "ollama"],
        "planning": ["claude_cli", "claude", "openai_cli", "openai", "gemini_cli", "gemini", "openrouter", "ollama"],
        "tasks": ["claude_cli", "claude", "openai_cli", "openai", "gemini_cli", "gemini", "openrouter", "ollama"],
        "code_generation": ["openai_cli", "openai", "gemini_cli", "ollama", "gemini", "claude_cli", "claude", "openrouter"],
        "task_execution": ["gemini_cli", "gemini", "openai_cli", "ollama", "openai", "claude_cli", "claude", "openrouter"],
        "refactoring": ["claude_cli", "claude", "openai_cli", "openai", "gemini_cli", "gemini", "openrouter", "ollama"],
        "review": ["claude_cli", "claude", "openai_cli", "openai", "gemini_cli", "gemini", "openrouter", "ollama"],
        "large_context": ["gemini_cli", "gemini", "claude_cli", "claude", "openrouter", "openai_cli", "openai", "ollama"],
        "fast_iteration": ["gemini_cli", "gemini", "openai_cli", "ollama", "openai", "claude_cli", "claude", "openrouter"],
        "cli": ["claude_cli", "openai_cli", "gemini_cli", "ollama"],  # Prefer CLI tools when requested
        "cost_effective": ["claude_cli", "openai_cli", "gemini_cli", "ollama", "openrouter", "gemini", "openai", "claude"],
    }

    # Map of provider names to their class constructors
    PROVIDER_CLASSES = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "openrouter": OpenRouterProvider,
        "ollama": OllamaProvider,
        "claude_cli": ClaudeCLIProvider,
        "openai_cli": OpenAICLIProvider,
        "gemini_cli": GeminiCLIProvider,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None, shared_context: Optional[Any] = None):
        """
        Initialize provider router.

        Args:
            config: Configuration dict with provider settings
            shared_context: Optional SharedContextWindow for multi-model collaboration
        """
        self.config = config or {}
        self.providers: Dict[str, AIProvider] = {}
        self.shared_context = shared_context
        self._initialize_providers()

    def _initialize_providers(self):
        """
        Initialize all configured providers dynamically.

        This supports unlimited providers! Just add them to PROVIDER_CLASSES
        and configure them in config.yaml
        """
        providers_config = self.config.get("providers", {})

        # Dynamically initialize all known providers
        for provider_name, ProviderClass in self.PROVIDER_CLASSES.items():
            provider_cfg = providers_config.get(provider_name, {})

            # Skip if explicitly disabled
            if not provider_cfg.get("enabled", True):
                continue

            try:
                # Extract provider-specific config
                api_key = provider_cfg.get("api_key")

                # Special handling for providers with extra params
                if provider_name == "openrouter":
                    provider = ProviderClass(
                        api_key=api_key,
                        site_url=provider_cfg.get("site_url"),
                        site_name=provider_cfg.get("site_name")
                    )
                elif provider_name == "ollama":
                    provider = ProviderClass(
                        base_url=provider_cfg.get("base_url")
                    )
                elif provider_name in ["claude_cli", "openai_cli", "gemini_cli"]:
                    # CLI providers don't need api_key or base_url - they use authenticated CLI tools
                    provider = ProviderClass()
                else:
                    provider = ProviderClass(api_key=api_key)

                # Validate and add if successful
                if provider.validate_config():
                    self.providers[provider_name] = provider
                    print(f"✓ Initialized {provider_name} provider")
                else:
                    print(f"⚠ {provider_name} validation failed - skipping")

            except Exception as e:
                print(f"⚠ Could not initialize {provider_name}: {e}")

        if not self.providers:
            raise RuntimeError(
                "No AI providers available! Please configure at least one provider:\n"
                "- Claude: Set ANTHROPIC_API_KEY\n"
                "- OpenAI: Set OPENAI_API_KEY\n"
                "- Gemini: Set GOOGLE_API_KEY\n"
                "- OpenRouter: Set OPENROUTER_API_KEY\n"
                "- Ollama: Ensure Ollama is running (http://localhost:11434)"
            )

    def get_provider(
        self,
        task_type: str = "code_generation",
        context_size: Optional[int] = None,
        preferred_provider: Optional[str] = None,
        required_capabilities: Optional[List[ProviderCapability]] = None
    ) -> AIProvider:
        """
        Get the optimal provider for a task.

        Args:
            task_type: Type of task (specification, planning, code_generation, etc.)
            context_size: Size of context in tokens
            preferred_provider: User's preferred provider name
            required_capabilities: Required provider capabilities

        Returns:
            AIProvider instance

        Raises:
            RuntimeError: If no suitable provider is available
        """
        # If user specified a provider, try to use it
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if self._can_handle_task(provider, context_size, required_capabilities):
                return provider

        # Get preference order for this task type
        preference_order = self.TASK_PREFERENCES.get(
            task_type,
            ["openai", "claude", "gemini"]
        )

        # Try providers in preference order
        for provider_name in preference_order:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                if self._can_handle_task(provider, context_size, required_capabilities):
                    return provider

        # Fallback to any available provider that can handle the task
        for provider in self.providers.values():
            if self._can_handle_task(provider, context_size, required_capabilities):
                return provider

        raise RuntimeError(
            f"No available provider can handle task type '{task_type}' "
            f"with context size {context_size}"
        )

    def _can_handle_task(
        self,
        provider: AIProvider,
        context_size: Optional[int],
        required_capabilities: Optional[List[ProviderCapability]]
    ) -> bool:
        """Check if a provider can handle a task"""
        # Check context size
        if context_size and not provider.can_handle_context(context_size):
            return False

        # Check required capabilities
        if required_capabilities:
            for capability in required_capabilities:
                if not provider.supports_capability(capability):
                    return False

        return True

    def complete(
        self,
        messages: List[Dict[str, str]],
        task_type: str = "code_generation",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        preferred_provider: Optional[str] = None,
        use_shared_context: bool = False,
        **kwargs
    ) -> tuple[str, str]:
        """
        Get completion from optimal provider.

        Args:
            messages: Conversation messages
            task_type: Type of task
            model: Specific model to use
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            preferred_provider: Preferred provider name
            use_shared_context: Use shared context window if available
            **kwargs: Additional provider-specific arguments

        Returns:
            Tuple of (response_text, provider_name)
        """
        # If using shared context, add messages to it and get full context
        if use_shared_context and self.shared_context:
            # Add user messages to shared context
            for msg in messages:
                if msg["role"] == "user":
                    self.shared_context.add_message(
                        role=msg["role"],
                        content=msg["content"]
                    )

            # Get full context including contributions from other providers
            messages = self.shared_context.get_messages(format="openai")

        # Estimate context size using improved estimation
        from ..context_window import estimate_tokens
        context_text = " ".join(msg["content"] for msg in messages)
        context_size = estimate_tokens(context_text)

        # Get optimal provider
        provider = self.get_provider(
            task_type=task_type,
            context_size=context_size,
            preferred_provider=preferred_provider
        )

        # Get optimal model for this task if not specified
        if not model:
            model = provider.get_optimal_model(task_type)

        # Generate completion
        response = provider.complete(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        # Add response to shared context if enabled
        if use_shared_context and self.shared_context:
            self.shared_context.add_message(
                role="assistant",
                content=response,
                provider=provider.name,
                model=model
            )

        return response, provider.name

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self.providers.keys())

    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """Get information about a provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not available")

        provider = self.providers[provider_name]
        return {
            "name": provider.name,
            "default_model": provider.default_model,
            "max_context": provider.max_context_tokens,
            "capabilities": [cap.value for cap in provider.capabilities]
        }

    def get_all_providers_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available providers"""
        return {
            name: self.get_provider_info(name)
            for name in self.providers.keys()
        }
