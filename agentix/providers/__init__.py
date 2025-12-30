"""
AI Provider integrations for Agentix

Supports unlimited AI providers:
- Claude (Anthropic)
- OpenAI / Codex
- Gemini (Google)
- OpenRouter (100+ models)
- Ollama (local models)
- ... and more!
"""

from .base import AIProvider, ProviderCapability
from .claude import ClaudeProvider
from .openai import OpenAIProvider
from .gemini import GeminiProvider
from .openrouter import OpenRouterProvider
from .ollama import OllamaProvider
from .router import ProviderRouter

__all__ = [
    "AIProvider",
    "ProviderCapability",
    "ClaudeProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "OpenRouterProvider",
    "OllamaProvider",
    "ProviderRouter",
]
