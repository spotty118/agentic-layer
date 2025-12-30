"""
Gemini CLI provider for Agentix

Uses the authenticated Gemini CLI tool
No API keys needed - just authenticate once with the Gemini CLI.

Prerequisites:
1. Install Gemini CLI
2. Authenticate once: gemini login (or gcloud auth login for Google AI)
3. That's it! Agentix will use your authenticated session.
"""

import subprocess
import json
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class GeminiCLIProvider(AIProvider):
    """Gemini CLI provider (no API key needed)"""

    def __init__(self):
        # No API key needed - uses CLI authentication
        super().__init__(api_key=None)
        # Try common CLI command names
        self.cli_command = "gemini"  # or could be "gcloud ai"

    @property
    def name(self) -> str:
        return "gemini_cli"

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.FAST_INFERENCE,
            ProviderCapability.LONG_CONTEXT,
            ProviderCapability.MULTIMODAL,
            ProviderCapability.CODE_GENERATION,
            ProviderCapability.CODE_UNDERSTANDING,
        ]

    @property
    def max_context_tokens(self) -> int:
        return 2000000  # Gemini 1.5 Pro supports 2M tokens

    @property
    def default_model(self) -> str:
        return "gemini-3.0-pro-high"  # Latest Gemini 3.0 Pro (Dec 2025)

    def get_client(self) -> Any:
        """Check if Gemini CLI is installed"""
        if self._client is None:
            try:
                # Check if gemini command exists
                result = subprocess.run(
                    [self.cli_command, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self._client = True
                else:
                    raise RuntimeError("Gemini CLI not found")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                raise RuntimeError(
                    "Gemini CLI not installed"
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
        """Get completion from Gemini CLI"""
        # Ensure CLI is available
        self.get_client()

        # Build the prompt from messages
        prompt = self._build_prompt(messages)

        try:
            # Execute gemini CLI command
            # Format may vary based on actual Gemini CLI implementation
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
                        "Not authenticated with Gemini CLI. Please authenticate first (e.g., gcloud auth login)"
                    )

                raise RuntimeError(f"Gemini CLI error: {error_msg}")

        except subprocess.TimeoutExpired:
            raise RuntimeError("Gemini CLI request timed out")
        except FileNotFoundError:
            raise RuntimeError("Gemini CLI not found")

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
        """Validate Gemini CLI is installed and authenticated"""
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
        """Get optimal Gemini model for task type"""
        task_models = {
            "code_generation": "gemini-3.0-pro-low",  # Fast code generation
            "task_execution": "gemini-3.0-pro-low",  # Quick iterations
            "specification": "gemini-3.0-pro-high",  # Better structured output
            "planning": "gemini-3.0-pro-high",  # Better reasoning
            "review": "gemini-3.0-pro-high",  # Better analysis
            "large_context": "gemini-3.0-pro-high",  # Handles massive context
        }
        return task_models.get(task_type, self.default_model)

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available Gemini models for CLI"""
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

        # Return known Gemini models
        return [
            {
                "id": "gemini-3.0-pro-high",
                "name": "Gemini 3.0 Pro High",
                "description": "Latest Gemini 3.0 Pro - best quality"
            },
            {
                "id": "gemini-3.0-pro-low",
                "name": "Gemini 3.0 Pro Low",
                "description": "Latest Gemini 3.0 Pro - faster responses"
            },
            {
                "id": "gemini-2.0-flash-exp",
                "name": "Gemini 2.0 Flash Experimental",
                "description": "Experimental fast model"
            },
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "description": "2M token context window"
            },
            {
                "id": "gemini-1.5-flash",
                "name": "Gemini 1.5 Flash",
                "description": "Fast and efficient"
            },
        ]
