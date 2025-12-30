"""
Base AI Provider abstraction for Agentix
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum


class ProviderCapability(Enum):
    """Capabilities that different providers excel at"""
    CODE_GENERATION = "code_generation"
    CODE_UNDERSTANDING = "code_understanding"
    LONG_CONTEXT = "long_context"
    FAST_INFERENCE = "fast_inference"
    PLANNING = "planning"
    REFACTORING = "refactoring"
    FUNCTION_CALLING = "function_calling"
    MULTIMODAL = "multimodal"


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._client = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[ProviderCapability]:
        """List of capabilities this provider excels at"""
        pass

    @property
    @abstractmethod
    def max_context_tokens(self) -> int:
        """Maximum context window size"""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model identifier"""
        pass

    @abstractmethod
    def get_client(self) -> Any:
        """Get or create the API client"""
        pass

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        Get a completion from the AI model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier (uses default if not specified)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific arguments

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate that the provider is properly configured"""
        pass

    def supports_capability(self, capability: ProviderCapability) -> bool:
        """Check if this provider supports a given capability"""
        return capability in self.capabilities

    def get_optimal_model(self, task_type: str) -> str:
        """Get the optimal model for a specific task type"""
        return self.default_model

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        # Rough estimate: ~4 characters per token
        return len(text) // 4

    def can_handle_context(self, context_size: int) -> bool:
        """Check if provider can handle the given context size"""
        return context_size <= self.max_context_tokens
