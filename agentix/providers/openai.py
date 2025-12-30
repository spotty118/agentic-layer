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

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available OpenAI models"""
        try:
            client = self.get_client()
            # Fetch models from OpenAI API
            models_response = client.models.list()
            models = []

            # Filter for relevant models (GPT-4, GPT-3.5, Codex)
            for model in models_response.data:
                model_id = model.id
                # Include GPT-4, GPT-3.5, and Codex models
                if any(prefix in model_id for prefix in ['gpt-4', 'gpt-3.5', 'codex', 'o1', 'o3']):
                    models.append({
                        "id": model_id,
                        "name": model_id,
                        "created": getattr(model, 'created', None)
                    })

            # Sort by creation date (newest first)
            models.sort(key=lambda x: x.get('created', 0), reverse=True)
            return models

        except Exception as e:
            # Fallback to known models if API call fails
            return [
                {
                    "id": "codex-5.2-medium",
                    "name": "Codex 5.2 Medium",
                    "description": "Latest Codex for code generation"
                },
                {
                    "id": "gpt-4-turbo",
                    "name": "GPT-4 Turbo",
                    "description": "Most capable GPT-4 model"
                },
                {
                    "id": "gpt-4",
                    "name": "GPT-4",
                    "description": "Standard GPT-4 model"
                },
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "description": "Fast and efficient"
                },
                {
                    "id": "o1-preview",
                    "name": "O1 Preview",
                    "description": "Advanced reasoning model"
                },
                {
                    "id": "o3-mini",
                    "name": "O3 Mini",
                    "description": "Efficient O3 variant"
                },
            ]
