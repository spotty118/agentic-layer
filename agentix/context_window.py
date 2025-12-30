"""
Virtual Shared Context Window for Agentix

Allows multiple AI providers to share context and collaborate on tasks.
This enables:
- Multi-model collaboration (e.g., Claude plans, GPT-4 codes, Gemini reviews)
- Context persistence across provider switches
- Ensemble decision making
- Cross-model validation
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class ContextMessage:
    """A message in the shared context window"""

    def __init__(
        self,
        role: str,
        content: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.role = role
        self.content = content
        self.provider = provider
        self.model = model
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "role": self.role,
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

    def to_openai_format(self) -> Dict[str, str]:
        """Convert to OpenAI message format"""
        return {
            "role": self.role,
            "content": self.content
        }


class SharedContextWindow:
    """
    Virtual shared context window that multiple AI providers can read from and write to.

    This enables collaborative multi-model workflows where different AIs can:
    - See what other models have generated
    - Build upon each other's outputs
    - Validate and review each other's work
    """

    def __init__(self, max_tokens: int = 200000):
        """
        Initialize shared context window.

        Args:
            max_tokens: Maximum tokens to keep in context (uses largest available)
        """
        self.messages: List[ContextMessage] = []
        self.max_tokens = max_tokens
        self.total_tokens = 0
        self.providers_used: Dict[str, int] = {}  # Track provider usage

    def add_message(
        self,
        role: str,
        content: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContextMessage:
        """
        Add a message to the shared context window.

        Args:
            role: Message role (system, user, assistant)
            content: Message content
            provider: AI provider that generated this message
            model: Specific model used
            metadata: Additional metadata

        Returns:
            The created ContextMessage
        """
        message = ContextMessage(role, content, provider, model, metadata)
        self.messages.append(message)

        # Track provider usage
        if provider:
            self.providers_used[provider] = self.providers_used.get(provider, 0) + 1

        # Estimate tokens (rough: ~4 chars per token)
        self.total_tokens += len(content) // 4

        # Trim if needed
        self._trim_if_needed()

        return message

    def get_messages(
        self,
        format: str = "standard",
        provider_filter: Optional[str] = None,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get messages from context window.

        Args:
            format: Output format (standard, openai, anthropic, full)
            provider_filter: Only include messages from this provider
            include_metadata: Include metadata in output

        Returns:
            List of messages in requested format
        """
        messages = self.messages

        # Filter by provider if requested
        if provider_filter:
            messages = [m for m in messages if m.provider == provider_filter]

        # Convert to requested format
        if format == "openai":
            return [m.to_openai_format() for m in messages]
        elif format == "full":
            return [m.to_dict() for m in messages]
        elif format == "standard":
            if include_metadata:
                return [{"role": m.role, "content": m.content, "provider": m.provider, "model": m.model} for m in messages]
            else:
                return [{"role": m.role, "content": m.content} for m in messages]
        else:
            return [m.to_dict() for m in messages]

    def get_recent_messages(self, count: int = 10) -> List[ContextMessage]:
        """Get the N most recent messages"""
        return self.messages[-count:]

    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context"""
        return {
            "total_messages": len(self.messages),
            "estimated_tokens": self.total_tokens,
            "max_tokens": self.max_tokens,
            "utilization": f"{(self.total_tokens / self.max_tokens * 100):.1f}%",
            "providers_used": self.providers_used,
            "oldest_message": self.messages[0].timestamp if self.messages else None,
            "newest_message": self.messages[-1].timestamp if self.messages else None
        }

    def _trim_if_needed(self):
        """Trim oldest messages if context exceeds max tokens"""
        while self.total_tokens > self.max_tokens and len(self.messages) > 1:
            # Remove oldest message (but keep system message if it's first)
            if self.messages[0].role == "system" and len(self.messages) > 1:
                removed = self.messages.pop(1)
            else:
                removed = self.messages.pop(0)

            # Update token count
            self.total_tokens -= len(removed.content) // 4

    def clear(self, keep_system: bool = True):
        """
        Clear context window.

        Args:
            keep_system: Keep system messages when clearing
        """
        if keep_system:
            system_messages = [m for m in self.messages if m.role == "system"]
            self.messages = system_messages
        else:
            self.messages = []

        self.total_tokens = sum(len(m.content) // 4 for m in self.messages)
        self.providers_used = {}

    def save_to_file(self, filepath: str):
        """Save context window to JSON file"""
        data = {
            "messages": [m.to_dict() for m in self.messages],
            "metadata": {
                "total_tokens": self.total_tokens,
                "max_tokens": self.max_tokens,
                "providers_used": self.providers_used,
                "saved_at": datetime.now().isoformat()
            }
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filepath: str):
        """Load context window from JSON file"""
        with open(filepath, "r") as f:
            data = json.load(f)

        self.messages = []
        for msg_data in data["messages"]:
            self.messages.append(ContextMessage(
                role=msg_data["role"],
                content=msg_data["content"],
                provider=msg_data.get("provider"),
                model=msg_data.get("model"),
                metadata=msg_data.get("metadata", {})
            ))

        # Restore metadata
        if "metadata" in data:
            self.total_tokens = data["metadata"].get("total_tokens", 0)
            self.providers_used = data["metadata"].get("providers_used", {})

    def create_snapshot(self) -> Dict[str, Any]:
        """Create a snapshot of current context state"""
        return {
            "messages": [m.to_dict() for m in self.messages],
            "summary": self.get_context_summary(),
            "timestamp": datetime.now().isoformat()
        }

    def get_provider_contributions(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed breakdown of each provider's contributions"""
        contributions = {}

        for provider, count in self.providers_used.items():
            provider_messages = [m for m in self.messages if m.provider == provider]
            total_tokens = sum(len(m.content) // 4 for m in provider_messages)

            contributions[provider] = {
                "message_count": count,
                "total_tokens": total_tokens,
                "percentage": f"{(count / len(self.messages) * 100):.1f}%",
                "models_used": list(set(m.model for m in provider_messages if m.model))
            }

        return contributions
