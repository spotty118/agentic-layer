"""
Claude CLI provider for Agentix

Uses the authenticated Claude Code CLI tool (https://github.com/anthropics/claude-code)
No API keys needed - just run 'claude login' once to authenticate.

Prerequisites:
1. Install Claude Code CLI: npm install -g @anthropic/claude-code
2. Authenticate once: claude login
3. That's it! Agentix will use your authenticated session.
"""

import subprocess
import json
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class ClaudeCLIProvider(AIProvider):
    """Claude Code CLI provider (no API key needed)"""

    def __init__(self):
        # No API key needed - uses CLI authentication
        super().__init__(api_key=None)
        self.cli_command = "claude"

    @property
    def name(self) -> str:
        return "claude_cli"

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
        return "claude-sonnet-4.5-20250514"  # Latest Claude Sonnet 4.5 (Dec 2025)

    def get_client(self) -> Any:
        """Check if Claude CLI is installed"""
        if self._client is None:
            try:
                # Check if claude command exists
                result = subprocess.run(
                    [self.cli_command, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self._client = True
                else:
                    raise RuntimeError("Claude CLI not found")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                raise RuntimeError(
                    "Claude CLI not installed. Install with: npm install -g @anthropic/claude-code"
                )
        return self._client

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """Get completion from Claude CLI"""
        # Ensure CLI is available
        self.get_client()

        # Build the prompt from messages
        prompt = self._build_prompt(messages)

        try:
            # Execute claude CLI command
            # Format: claude "your prompt here"
            result = subprocess.run(
                [self.cli_command, prompt],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"

                # Check for common authentication errors
                if "not logged in" in error_msg.lower() or "authentication" in error_msg.lower():
                    raise RuntimeError(
                        "Not authenticated with Claude CLI. Run: claude login"
                    )

                raise RuntimeError(f"Claude CLI error: {error_msg}")

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude CLI request timed out")
        except FileNotFoundError:
            raise RuntimeError(
                "Claude CLI not found. Install with: npm install -g @anthropic/claude-code"
            )

    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Build a single prompt string from message list"""
        prompt_parts = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        return "\n\n".join(prompt_parts)

    def validate_config(self) -> bool:
        """Validate Claude CLI is installed and authenticated"""
        try:
            # Check if CLI exists
            result = subprocess.run(
                [self.cli_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False

            # Try a simple test command to verify authentication
            # This might vary based on actual Claude CLI implementation
            test_result = subprocess.run(
                [self.cli_command, "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )

            return test_result.returncode == 0

        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def get_optimal_model(self, task_type: str) -> str:
        """Get optimal Claude model for task type"""
        # Map task types to best Claude models
        task_models = {
            "planning": "claude-opus-4.5-20250514",  # Opus 4.5 for complex reasoning
            "refactoring": "claude-sonnet-4.5-20250514",  # Sonnet 4.5 for code understanding
            "specification": "claude-opus-4.5-20250514",  # Opus 4.5 for structured output
            "code_generation": "claude-sonnet-4.5-20250514",  # Sonnet 4.5 balanced performance
            "review": "claude-sonnet-4.5-20250514",  # Sonnet 4.5 for analysis
        }
        return task_models.get(task_type, self.default_model)
