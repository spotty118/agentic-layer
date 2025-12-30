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


class ProviderRouter:
    """Intelligently routes tasks to optimal AI providers"""

    # Best provider for each task type based on strengths
    TASK_PREFERENCES = {
        "specification": ["claude", "gemini", "openai"],  # Claude best for specs
        "planning": ["claude", "openai", "gemini"],  # Claude excels at planning
        "tasks": ["claude", "openai", "gemini"],  # Claude for task breakdown
        "code_generation": ["openai", "gemini", "claude"],  # OpenAI Codex excellent
        "task_execution": ["gemini", "openai", "claude"],  # Gemini fast
        "refactoring": ["claude", "openai", "gemini"],  # Claude understands code best
        "review": ["claude", "openai", "gemini"],  # Claude for code analysis
        "large_context": ["gemini", "claude", "openai"],  # Gemini 2M context
        "fast_iteration": ["gemini", "openai", "claude"],  # Gemini fastest
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize provider router.

        Args:
            config: Configuration dict with provider settings
        """
        self.config = config or {}
        self.providers: Dict[str, AIProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available providers"""
        # Try to initialize each provider
        providers_config = self.config.get("providers", {})

        # Claude
        if providers_config.get("claude", {}).get("enabled", True):
            try:
                claude = ClaudeProvider(
                    api_key=providers_config.get("claude", {}).get("api_key")
                )
                if claude.validate_config():
                    self.providers["claude"] = claude
            except Exception as e:
                print(f"Warning: Could not initialize Claude provider: {e}")

        # OpenAI
        if providers_config.get("openai", {}).get("enabled", True):
            try:
                openai = OpenAIProvider(
                    api_key=providers_config.get("openai", {}).get("api_key")
                )
                if openai.validate_config():
                    self.providers["openai"] = openai
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI provider: {e}")

        # Gemini
        if providers_config.get("gemini", {}).get("enabled", True):
            try:
                gemini = GeminiProvider(
                    api_key=providers_config.get("gemini", {}).get("api_key")
                )
                if gemini.validate_config():
                    self.providers["gemini"] = gemini
            except Exception as e:
                print(f"Warning: Could not initialize Gemini provider: {e}")

        if not self.providers:
            raise RuntimeError(
                "No AI providers available. Please configure at least one provider "
                "(Claude, OpenAI, or Gemini) with a valid API key."
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
            **kwargs: Additional provider-specific arguments

        Returns:
            Tuple of (response_text, provider_name)
        """
        # Estimate context size
        context_text = " ".join(msg["content"] for msg in messages)
        context_size = len(context_text) // 4  # Rough token estimate

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
