"""
AI Provider integrations for Agentix

Supports unlimited AI providers:
- Claude (Anthropic) - API and CLI
- OpenAI / Codex - API and CLI
- Gemini (Google) - API and CLI
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
from .claude_cli import ClaudeCLIProvider
from .openai_cli import OpenAICLIProvider
from .gemini_cli import GeminiCLIProvider
from .router import ProviderRouter

__all__ = [
    "AIProvider",
    "ProviderCapability",
    "ClaudeProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "OpenRouterProvider",
    "OllamaProvider",
    "ClaudeCLIProvider",
    "OpenAICLIProvider",
    "GeminiCLIProvider",
    "ProviderRouter",
]
