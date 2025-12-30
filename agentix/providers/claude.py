"""
Anthropic Claude provider for Agentix

Claude's strengths:
- Excellent code understanding and analysis
- Superior long context handling (200K+ tokens)
- Precise instruction following
- Strong reasoning and planning capabilities
- Best for: Planning, refactoring, code review
"""

import os
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class ClaudeProvider(AIProvider):
    """Anthropic Claude AI provider"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY"))

    @property
    def name(self) -> str:
        return "claude"

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
        return "claude-3-5-sonnet-20241022"

    def get_client(self) -> Any:
        """Get or create Anthropic client"""
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Anthropic SDK not installed. Install with: pip install anthropic"
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
        """Get completion from Claude"""
        client = self.get_client()

        # Convert messages format to Anthropic's expected format
        # Extract system message if present
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Ensure we have at least one message and it starts with user
        if not anthropic_messages:
            anthropic_messages = [{"role": "user", "content": "Continue"}]
        elif anthropic_messages[0]["role"] != "user":
            # Claude requires first message to be from user
            anthropic_messages.insert(0, {"role": "user", "content": "Please help with the following task."})

        try:
            response = client.messages.create(
                model=model or self.default_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message or "You are a helpful coding assistant.",
                messages=anthropic_messages,
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Claude API error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate Claude configuration"""
        if not self.api_key:
            return False
        try:
            self.get_client()
            return True
        except Exception:
            return False

    def get_optimal_model(self, task_type: str) -> str:
        """Get optimal Claude model for task type"""
        # Map task types to best Claude models
        task_models = {
            "planning": "claude-3-5-sonnet-20241022",  # Best for complex reasoning
            "refactoring": "claude-3-5-sonnet-20241022",  # Best for code understanding
            "specification": "claude-3-5-sonnet-20241022",  # Best for structured output
            "code_generation": "claude-3-5-sonnet-20241022",  # Balanced performance
            "review": "claude-3-5-sonnet-20241022",  # Best for analysis
        }
        return task_models.get(task_type, self.default_model)
