"""
Local OpenAI/Codex provider for Agentix

Connects to locally installed OpenAI/Codex (VS Code extension or local instance)
via HTTP without requiring an API key.

Connection:
- Base URL: http://localhost:3002 (configurable via OPENAI_LOCAL_URL)
- No API key required - connects to local installation
- Compatible with VS Code Codex/OpenAI extensions

Setup:
1. Ensure OpenAI/Codex is running locally and exposing an HTTP API
2. Set OPENAI_LOCAL_URL environment variable (optional)
3. Enable in config.yaml:
   providers:
     local_openai:
       enabled: true
       base_url: http://localhost:3002
"""

import os
import requests
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class LocalOpenAIProvider(AIProvider):
    """Local OpenAI/Codex AI provider (no API key needed)"""

    def __init__(self, base_url: Optional[str] = None):
        # No API key needed for local connections
        super().__init__(api_key=None)
        self.base_url = base_url or os.getenv(
            "OPENAI_LOCAL_URL",
            "http://localhost:3002"
        )

    @property
    def name(self) -> str:
        return "local_openai"

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
        return "gpt-4-turbo"

    def get_client(self) -> Any:
        """
        No client needed for HTTP connections.
        Just return a session.
        """
        if self._client is None:
            self._client = requests.Session()
        return self._client

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """Get completion from local OpenAI/Codex instance"""
        session = self.get_client()

        try:
            # Standard OpenAI-compatible chat endpoint
            response = session.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": model or self.default_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False,
                    **kwargs
                },
                timeout=300  # 5 minute timeout for long responses
            )
            response.raise_for_status()
            data = response.json()

            # Extract message from response
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise RuntimeError("Invalid response format from local OpenAI")

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Could not connect to local OpenAI at {self.base_url}. "
                "Ensure OpenAI/Codex is running locally and accessible."
            )
        except requests.exceptions.Timeout:
            raise RuntimeError("Local OpenAI request timed out")
        except Exception as e:
            raise RuntimeError(f"Local OpenAI error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate local OpenAI is accessible"""
        try:
            session = self.get_client()
            # Try health check endpoint
            response = session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            # Try alternative endpoint
            try:
                response = session.get(
                    f"{self.base_url}/v1/models",
                    timeout=5
                )
                return response.status_code in [200, 401]
            except:
                return False

    def get_optimal_model(self, task_type: str) -> str:
        """Get optimal OpenAI model for task type"""
        task_models = {
            "code_generation": "gpt-4-turbo",  # Best for code
            "task_execution": "gpt-4-turbo",  # Quick task completion
            "specification": "gpt-4-turbo",  # Good for structured output
            "planning": "gpt-4-turbo",  # Decent planning
            "review": "gpt-4-turbo",  # Code analysis
        }
        return task_models.get(task_type, self.default_model)

    def get_codex_model(self) -> str:
        """Get the Codex model for code-specific tasks"""
        # Codex is now integrated into GPT-4
        return "gpt-4-turbo"

    def get_available_models(self) -> List[str]:
        """Get list of available models from local OpenAI instance"""
        try:
            session = self.get_client()
            response = session.get(
                f"{self.base_url}/v1/models",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            if "data" in data:
                return [model["id"] for model in data["data"]]
            return ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
        except:
            return ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
