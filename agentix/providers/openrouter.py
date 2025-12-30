"""
OpenRouter provider for Agentix

OpenRouter's strengths:
- Access to 100+ models from multiple providers
- Unified API for all models
- Cost-effective model selection
- Fallback and routing capabilities
- Best for: Model experimentation, cost optimization, accessing niche models
"""

import os
import requests
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class OpenRouterProvider(AIProvider):
    """OpenRouter AI provider - access to 100+ models"""

    def __init__(self, api_key: Optional[str] = None, site_url: Optional[str] = None, site_name: Optional[str] = None):
        super().__init__(api_key or os.getenv("OPENROUTER_API_KEY"))
        self.site_url = site_url or os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000")
        self.site_name = site_name or os.getenv("OPENROUTER_SITE_NAME", "Agentix")
        self.api_base = "https://openrouter.ai/api/v1"

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def capabilities(self) -> List[ProviderCapability]:
        # OpenRouter provides access to many models with varied capabilities
        return [
            ProviderCapability.CODE_GENERATION,
            ProviderCapability.CODE_UNDERSTANDING,
            ProviderCapability.PLANNING,
            ProviderCapability.FAST_INFERENCE,
            ProviderCapability.LONG_CONTEXT,
        ]

    @property
    def max_context_tokens(self) -> int:
        # Depends on selected model, use conservative estimate
        return 128000

    @property
    def default_model(self) -> str:
        return "anthropic/claude-3.5-sonnet"  # Good default

    def get_client(self) -> Any:
        """OpenRouter uses REST API, no SDK needed"""
        return self

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """Get completion from OpenRouter"""
        if not self.api_key:
            raise RuntimeError("OpenRouter API key not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name,
            "Content-Type": "application/json"
        }

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenRouter API error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate OpenRouter configuration"""
        return bool(self.api_key)

    def get_optimal_model(self, task_type: str) -> str:
        """Get optimal model for task type from OpenRouter's catalog"""
        task_models = {
            "specification": "anthropic/claude-3.5-sonnet",
            "planning": "anthropic/claude-3.5-sonnet",
            "code_generation": "openai/gpt-4-turbo",
            "task_execution": "google/gemini-pro-1.5",
            "refactoring": "anthropic/claude-3.5-sonnet",
            "review": "anthropic/claude-3.5-sonnet",
            "fast_iteration": "google/gemini-flash-1.5",
            "large_context": "google/gemini-pro-1.5",
        }
        return task_models.get(task_type, self.default_model)

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""
        if not self.api_key:
            return []

        try:
            response = requests.get(
                f"{self.api_base}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception:
            return []
