"""
Google Gemini provider for Agentix

Gemini's strengths:
- Fast inference speeds
- Large context window (2M tokens with Gemini 1.5 Pro)
- Multimodal capabilities
- Good at structured output
- Best for: Fast iterations, large codebase context, multimodal tasks
"""

import os
from typing import Dict, List, Optional, Any
from .base import AIProvider, ProviderCapability


class GeminiProvider(AIProvider):
    """Google Gemini AI provider"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("GOOGLE_API_KEY"))

    @property
    def name(self) -> str:
        return "gemini"

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
        return "gemini-1.5-flash"  # Fast and cost-effective

    def get_client(self) -> Any:
        """Get or create Gemini client"""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                raise ImportError(
                    "Google Generative AI SDK not installed. "
                    "Install with: pip install google-generativeai"
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
        """Get completion from Gemini"""
        genai = self.get_client()

        # Convert messages to Gemini format
        # Gemini uses a different conversation format
        system_instruction = None
        conversation_parts = []

        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                conversation_parts.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                conversation_parts.append({"role": "model", "parts": [msg["content"]]})

        try:
            # Create model instance
            model_instance = genai.GenerativeModel(
                model_name=model or self.default_model,
                system_instruction=system_instruction
            )

            # Configure generation
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            # If we have a conversation, use chat mode
            if len(conversation_parts) > 1:
                chat = model_instance.start_chat(history=conversation_parts[:-1])
                response = chat.send_message(
                    conversation_parts[-1]["parts"][0],
                    generation_config=generation_config
                )
            else:
                # Single message, use generate_content
                content = conversation_parts[0]["parts"][0] if conversation_parts else "Continue"
                response = model_instance.generate_content(
                    content,
                    generation_config=generation_config
                )

            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate Gemini configuration"""
        if not self.api_key:
            return False
        try:
            self.get_client()
            return True
        except Exception:
            return False

    def get_optimal_model(self, task_type: str) -> str:
        """Get optimal Gemini model for task type"""
        # Map task types to best Gemini models
        task_models = {
            "code_generation": "gemini-1.5-flash",  # Fast code generation
            "task_execution": "gemini-1.5-flash",  # Quick iterations
            "specification": "gemini-1.5-pro",  # Better structured output
            "planning": "gemini-1.5-pro",  # Better reasoning
            "review": "gemini-1.5-pro",  # Better analysis
            "large_context": "gemini-1.5-pro",  # Handles massive context
        }
        return task_models.get(task_type, self.default_model)
