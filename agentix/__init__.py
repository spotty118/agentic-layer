"""
Agentix - Multi-AI Spec-Driven Coding Agent

Integrates Claude, OpenAI Codex, and Gemini for intelligent,
spec-driven codebase operations.
"""

__version__ = "1.0.0"
__author__ = "Agentix Team"

from .orchestrator import Orchestrator
from .config import Config
from .logger import AgentLogger, ColoredOutput
from .validators import Validator, ValidationError
from .providers import (
    AIProvider,
    ClaudeProvider,
    OpenAIProvider,
    GeminiProvider,
    ProviderRouter,
)

__all__ = [
    "Orchestrator",
    "Config",
    "AgentLogger",
    "ColoredOutput",
    "Validator",
    "ValidationError",
    "AIProvider",
    "ClaudeProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "ProviderRouter",
]
