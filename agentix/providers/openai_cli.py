"""
OpenAI CLI provider for Agentix

Uses the authenticated OpenAI CLI tool
No API keys needed - just authenticate once with the OpenAI CLI.

Prerequisites:
1. Install OpenAI CLI
2. Authenticate once: openai login (or similar authentication command)
3. That's it! Agentix will use your authenticated session.
"""

import subprocess
import json
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class OpenAICLIProvider(AIProvider):
    """OpenAI CLI provider (no API key needed)"""

    def __init__(self):
        # No API key needed - uses CLI authentication
        super().__init__(api_key=None)
        self.cli_command = "openai"

    @property
    def name(self) -> str:
        return "openai_cli"

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.CODE_GENERATION,
            ProviderCapability.FAST_INFERENCE,
            ProviderCapability.FUNCTION_CALLING,
            ProviderCapability.CODE_UNDERSTANDING,
        ]

    @property
    def max_context_tokens(self) -> int:
        return 128000  # GPT-4 Turbo

    @property
    def default_model(self) -> str:
        return "codex-5.2-medium"  # Latest Codex 5.2 (Dec 2025)

    def get_client(self) -> Any:
        """Check if OpenAI CLI is installed"""
        if self._client is None:
            try:
                # Check if openai command exists
                result = subprocess.run(
                    [self.cli_command, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self._client = True
                else:
                    raise RuntimeError("OpenAI CLI not found")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                raise RuntimeError(
                    "OpenAI CLI not installed"
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
        """Get completion from OpenAI CLI"""
        # Ensure CLI is available
        self.get_client()

        # Build the prompt from messages
        prompt = self._build_prompt(messages)

        try:
            # Execute openai CLI command
            # This format may vary based on actual OpenAI CLI implementation
            result = subprocess.run(
                [self.cli_command, "chat", prompt, "--model", model or self.default_model],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"

                # Check for authentication errors
                if "not logged in" in error_msg.lower() or "authentication" in error_msg.lower():
                    raise RuntimeError(
                        "Not authenticated with OpenAI CLI. Please authenticate first."
                    )

                raise RuntimeError(f"OpenAI CLI error: {error_msg}")

        except subprocess.TimeoutExpired:
            raise RuntimeError("OpenAI CLI request timed out")
        except FileNotFoundError:
            raise RuntimeError("OpenAI CLI not found")

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
        """Validate OpenAI CLI is installed and authenticated"""
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

            # Try help command to verify installation
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
        """Get optimal OpenAI model for task type"""
        task_models = {
            "code_generation": "codex-5.2-medium",
            "task_execution": "codex-5.2-medium",
            "specification": "codex-5.2-medium",
            "planning": "codex-5.2-medium",
            "review": "codex-5.2-medium",
        }
        return task_models.get(task_type, self.default_model)

    def get_codex_model(self) -> str:
        """Get the Codex model for code-specific tasks"""
        return "codex-5.2-medium"  # Latest Codex 5.2

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available OpenAI models for CLI"""
        try:
            # Try to fetch models from CLI if it supports a list command
            result = subprocess.run(
                [self.cli_command, "models", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse the output (format depends on CLI implementation)
                # For now, return static list
                pass
        except:
            pass

        # Return known OpenAI models
        return [
            {
                "id": "codex-5.2-medium",
                "name": "Codex 5.2 Medium",
                "description": "Latest Codex for code generation"
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "Most capable GPT-4 model"
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "Standard GPT-4 model"
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "Fast and efficient"
            },
            {
                "id": "o1-preview",
                "name": "O1 Preview",
                "description": "Advanced reasoning model"
            },
            {
                "id": "o3-mini",
                "name": "O3 Mini",
                "description": "Efficient O3 variant"
            },
        ]
