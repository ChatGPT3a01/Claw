"""Base tool definitions for LiangClaw agent."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ToolCall:
    """Represents a tool call request from the model."""
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    """Result of executing a tool."""
    output: str
    is_error: bool = False
    truncated: bool = False

    @staticmethod
    def error(msg: str) -> "ToolResult":
        return ToolResult(output=msg, is_error=True)

    @staticmethod
    def ok(output: str, max_chars: int = 50000) -> "ToolResult":
        if len(output) > max_chars:
            return ToolResult(
                output=output[:max_chars] + f"\n\n... (已截斷，原始長度 {len(output)} 字元)",
                truncated=True,
            )
        return ToolResult(output=output)


class BaseTool(ABC):
    """Abstract base class for all LiangClaw tools."""

    name: str = ""
    description: str = ""
    parameters: dict = {}
    is_read_only: bool = True

    @abstractmethod
    async def execute(self, args: dict, cwd: Path) -> ToolResult:
        """Execute the tool with given arguments."""
        ...

    def to_openai_schema(self) -> dict:
        """Convert to OpenAI/Groq function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_claude_schema(self) -> dict:
        """Convert to Anthropic tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }

    def to_gemini_schema(self) -> dict:
        """Convert to Gemini function declaration format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
