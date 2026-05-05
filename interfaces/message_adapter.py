"""Unified message types for all interfaces."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    """Incoming message from any interface."""
    role: str = "user"
    content: str = ""
    source: str = "api"          # "gradio" | "line" | "telegram" | "api"
    user_id: str = ""
    session_id: str = ""
    model: str | None = None     # optional model override
    metadata: dict = field(default_factory=dict)


@dataclass
class ChatResponse:
    """Outgoing response to any interface."""
    content: str = ""
    model_used: str = ""
    session_id: str = ""
    usage: dict = field(default_factory=dict)
    skill_used: str | None = None
    routed_commands: list[str] = field(default_factory=list)
    routed_tools: list[str] = field(default_factory=list)
    tool_uses: list[dict] = field(default_factory=list)
