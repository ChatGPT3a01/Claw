"""Abstract base for all model providers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator


@dataclass
class ToolCallData:
    """Represents a tool call from the model."""
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ModelResponse:
    """Standardised model response."""
    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str = "stop"  # "stop" | "tool_use"
    tool_calls: tuple[ToolCallData, ...] = ()
    metadata: dict = field(default_factory=dict)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class ModelProvider(ABC):
    """ABC that every provider must implement."""

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        model_id: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: str = "",
    ) -> ModelResponse: ...

    async def generate_with_tools(
        self,
        messages: list[dict],
        model_id: str,
        tools: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: str = "",
    ) -> ModelResponse:
        """Generate with function calling / tool use support.

        Default implementation falls back to generate() without tools.
        Providers should override this to support function calling.
        """
        return await self.generate(
            messages, model_id, max_tokens, temperature, system_prompt
        )

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[dict],
        model_id: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: str = "",
    ) -> AsyncIterator[str]: ...

    @abstractmethod
    async def verify_api_key(self) -> bool: ...
