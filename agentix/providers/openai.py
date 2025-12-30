"""
OpenAI provider for Agentix (including Codex)

OpenAI's strengths:
- Excellent code generation with GPT-4
- Broad knowledge base
- Strong function calling capabilities
- Fast inference
- Best for: Code generation, task execution, general problem solving
"""

import os
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class OpenAIProvider(AIProvider):
    """OpenAI AI provider (GPT-4, Codex)"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"))

    @property
    def name(self) -> str:
        return "openai"

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.CODE_GENERATION,
            ProviderCapability.FAST_INFERENCE,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.CODE_UNDERSTANDING,
        ]

    @property
    def max_context_tokens(self) -> int:
        return 128000  # GPT-4 Turbo

    @property
    def default_model(self) -> str:
        return "codex-5.2-medium"  # Latest Codex 5.2 (Dec 2025)

    def get_client(self) -> Any:
        """Get or create OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI SDK not installed. Install with: pip install openai"
                )
        return self._client

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """Get completion from OpenAI"""
        client = self.get_client()

        try:
            response = client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate OpenAI configuration"""
        if not self.api_key:
            return False
        try:
            self.get_client()
            return True
        except Exception:
            return False

    def get_optimal_model(self, task_type: str) -> str:
        """Get optimal OpenAI model for task type"""
        # Map task types to best Codex/OpenAI models
        task_models = {
            "code_generation": "codex-5.2-medium",  # Codex 5.2 for code generation
            "task_execution": "codex-5.2-medium",  # Codex 5.2 for task execution
            "specification": "codex-5.2-medium",  # Good for structured output
            "planning": "codex-5.2-medium",  # Decent planning
            "review": "codex-5.2-medium",  # Code analysis
        }
        return task_models.get(task_type, self.default_model)

    def get_codex_model(self) -> str:
        """Get the Codex model for code-specific tasks"""
        return "codex-5.2-medium"  # Latest Codex 5.2
