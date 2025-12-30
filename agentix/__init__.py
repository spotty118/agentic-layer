"""
Agentix - Multi-AI Spec-Driven Coding Agent

Integrates Claude, OpenAI Codex, and Gemini for intelligent,
spec-driven codebase operations.
"""

__version__ = "1.2.0"
__author__ = "Agentix Team"

from .orchestrator import Orchestrator
from .config import Config
from .logger import AgentLogger, ColoredOutput
from .validators import Validator, ValidationError
from .interactive import InteractivePrompt, SetupWizard
from .commands import ProviderCommands, ConfigCommands, ModelCommands
from .syntax_highlighter import SyntaxHighlighter, ColorScheme, TokenType
from .code_viewer import CodeViewer
from .diff_utils import DiffViewer
from .providers import (
    AIProvider,
    ClaudeProvider,
    OpenAIProvider,
    GeminiProvider,
    OpenRouterProvider,
    OllamaProvider,
    ProviderRouter,
)

__all__ = [
    "Orchestrator",
    "Config",
    "AgentLogger",
    "ColoredOutput",
    "Validator",
    "ValidationError",
    "InteractivePrompt",
    "SetupWizard",
    "ProviderCommands",
    "ConfigCommands",
    "ModelCommands",
    "SyntaxHighlighter",
    "ColorScheme",
    "TokenType",
    "CodeViewer",
    "DiffViewer",
    "AIProvider",
    "ClaudeProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "OpenRouterProvider",
    "OllamaProvider",
    "ProviderRouter",
]
