"""
Local Claude Code provider for Agentix

Connects to locally installed Claude Code (VS Code extension or local instance)
via HTTP without requiring an API key.

Connection:
- Base URL: http://localhost:3000 (configurable via CLAUDE_LOCAL_URL)
- No API key required - connects to local installation
- Compatible with VS Code Claude Code extension

Setup:
1. Ensure Claude Code is running locally and exposing an HTTP API
2. Set CLAUDE_LOCAL_URL environment variable (optional)
3. Enable in config.yaml:
   providers:
     local_claude:
       enabled: true
       base_url: http://localhost:3000
"""

import os
import requests
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class LocalClaudeProvider(AIProvider):
    """Local Claude Code AI provider (no API key needed)"""

    def __init__(self, base_url: Optional[str] = None):
        # No API key needed for local connections
        super().__init__(api_key=None)
        self.base_url = base_url or os.getenv(
            "CLAUDE_LOCAL_URL",
            "http://localhost:3000"
        )

    @property
    def name(self) -> str:
        return "local_claude"

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.CODE_UNDERSTANDING,
            ProviderCapability.LONG_CONTEXT,
            ProviderCapability.PLANNING,
            ProviderCapability.REFACTORING,
            ProviderCapability.CODE_GENERATION,
        ]

    @property
    def max_context_tokens(self) -> int:
        return 200000  # Claude 3+ supports 200K tokens

    @property
    def default_model(self) -> str:
        return "claude-3-5-sonnet-20241022"

    def get_client(self) -> Any:
        """
        No client needed for HTTP connections.
        Just return the base URL.
        """
        if self._client is None:
            # Validate that requests library is available
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
        """Get completion from local Claude Code instance"""
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
                raise RuntimeError("Invalid response format from local Claude")

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Could not connect to local Claude at {self.base_url}. "
                "Ensure Claude Code is running locally and accessible."
            )
        except requests.exceptions.Timeout:
            raise RuntimeError("Local Claude request timed out")
        except Exception as e:
            raise RuntimeError(f"Local Claude error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate local Claude is accessible"""
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
                return response.status_code in [200, 401]  # 401 means it's there but needs auth
            except:
                return False

    def get_optimal_model(self, task_type: str) -> str:
        """Get optimal model for task type"""
        # For local Claude, usually only one model available
        task_models = {
            "planning": "claude-3-5-sonnet-20241022",
            "refactoring": "claude-3-5-sonnet-20241022",
            "specification": "claude-3-5-sonnet-20241022",
            "code_generation": "claude-3-5-sonnet-20241022",
            "review": "claude-3-5-sonnet-20241022",
        }
        return task_models.get(task_type, self.default_model)

    def get_available_models(self) -> List[str]:
        """Get list of available models from local Claude instance"""
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
            return [self.default_model]
        except:
            return [self.default_model]
