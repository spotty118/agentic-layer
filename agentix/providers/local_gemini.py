"""
Local Gemini provider for Agentix

Connects to locally installed Gemini (VS Code extension or local instance)
via HTTP without requiring an API key.

Connection:
- Base URL: http://localhost:3001 (configurable via GEMINI_LOCAL_URL)
- No API key required - connects to local installation
- Compatible with VS Code Gemini extension

Setup:
1. Ensure Gemini is running locally and exposing an HTTP API
2. Set GEMINI_LOCAL_URL environment variable (optional)
3. Enable in config.yaml:
   providers:
     local_gemini:
       enabled: true
       base_url: http://localhost:3001
"""

import os
import requests
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class LocalGeminiProvider(AIProvider):
    """Local Gemini AI provider (no API key needed)"""

    def __init__(self, base_url: Optional[str] = None):
        # No API key needed for local connections
        super().__init__(api_key=None)
        self.base_url = base_url or os.getenv(
            "GEMINI_LOCAL_URL",
            "http://localhost:3001"
        )

    @property
    def name(self) -> str:
        return "local_gemini"

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.FAST_INFERENCE,
            ProviderCapability.LONG_CONTEXT,
            ProviderCapability.MULTIMODAL,
            ProviderCapability.CODE_GENERATION,
            ProviderCapability.CODE_UNDERSTANDING,
        ]

    @property
    def max_context_tokens(self) -> int:
        return 2000000  # Gemini 1.5 Pro supports 2M tokens

    @property
    def default_model(self) -> str:
        return "gemini-1.5-flash"

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
        """Get completion from local Gemini instance"""
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
                raise RuntimeError("Invalid response format from local Gemini")

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Could not connect to local Gemini at {self.base_url}. "
                "Ensure Gemini is running locally and accessible."
            )
        except requests.exceptions.Timeout:
            raise RuntimeError("Local Gemini request timed out")
        except Exception as e:
            raise RuntimeError(f"Local Gemini error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate local Gemini is accessible"""
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
        """Get optimal Gemini model for task type"""
        task_models = {
            "code_generation": "gemini-1.5-flash",  # Fast code generation
            "task_execution": "gemini-1.5-flash",  # Quick iterations
            "specification": "gemini-1.5-pro",  # Better structured output
            "planning": "gemini-1.5-pro",  # Better reasoning
            "review": "gemini-1.5-pro",  # Better analysis
            "large_context": "gemini-1.5-pro",  # Handles massive context
        }
        return task_models.get(task_type, self.default_model)

    def get_available_models(self) -> List[str]:
        """Get list of available models from local Gemini instance"""
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
            return ["gemini-1.5-flash", "gemini-1.5-pro"]
        except:
            return ["gemini-1.5-flash", "gemini-1.5-pro"]
