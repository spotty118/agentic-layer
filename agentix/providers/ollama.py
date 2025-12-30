"""
Ollama provider for Agentix

Ollama's strengths:
- 100% local execution (no API costs, privacy)
- Support for Llama, Mistral, CodeLlama, and many more
- Custom model fine-tuning
- Fast inference on local hardware
- Best for: Privacy-sensitive projects, offline development, cost-free usage
"""

import os
import requests
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class OllamaProvider(AIProvider):
    """Ollama provider for local AI models"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key)  # Ollama doesn't need API key
        self.base_url = base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.CODE_GENERATION,
            ProviderCapability.CODE_UNDERSTANDING,
            ProviderCapability.FAST_INFERENCE,
            ProviderCapability.PLANNING,
        ]

    @property
    def max_context_tokens(self) -> int:
        # Most Ollama models support 4K-8K, some up to 32K
        return 32000

    @property
    def default_model(self) -> str:
        return "codellama"  # Good for coding tasks

    def get_client(self) -> Any:
        """Ollama uses REST API"""
        return self

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """Get completion from Ollama"""
        # Convert messages to Ollama format
        # Ollama expects a single prompt or a chat format
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model or self.default_model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                },
                timeout=300  # Local models can be slower
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def get_optimal_model(self, task_type: str) -> str:
        """Get optimal Ollama model for task type"""
        task_models = {
            "code_generation": "codellama:13b",
            "specification": "llama2:13b",
            "planning": "mistral:latest",
            "task_execution": "codellama:7b",
            "review": "codellama:13b",
            "fast_iteration": "codellama:7b",
        }
        return task_models.get(task_type, self.default_model)

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of locally installed Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [{"id": m["name"], "name": m["name"]} for m in models]
        except Exception:
            return []

    def pull_model(self, model_name: str) -> bool:
        """Pull/download a model to Ollama"""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=600
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error pulling model {model_name}: {e}")
            return False
