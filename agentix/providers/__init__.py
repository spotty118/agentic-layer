"""
AI Provider integrations for Agentix

Supports unlimited AI providers:
- Claude (Anthropic) - API and Local
- OpenAI / Codex - API and Local
- Gemini (Google) - API and Local
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
from .local_claude import LocalClaudeProvider
from .local_openai import LocalOpenAIProvider
from .local_gemini import LocalGeminiProvider
from .router import ProviderRouter

__all__ = [
    "AIProvider",
    "ProviderCapability",
    "ClaudeProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "OpenRouterProvider",
    "OllamaProvider",
    "LocalClaudeProvider",
    "LocalOpenAIProvider",
    "LocalGeminiProvider",
    "ProviderRouter",
]
