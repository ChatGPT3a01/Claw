"""Tool permission manager for LiangClaw."""
from __future__ import annotations


class ToolPermissionManager:
    """Controls which tools are auto-approved vs need confirmation."""

    ALWAYS_ALLOW = frozenset({
        "file_read", "glob_search", "grep_search",
        "list_directory", "web_fetch",
    })

    def __init__(self, auto_approve_all: bool = True):
        """
        Args:
            auto_approve_all: If True, all tools are auto-approved (no restrictions).
                              Default True for maximum power.
        """
        self.auto_approve_all = auto_approve_all

    def is_allowed(self, tool_name: str) -> bool:
        """Check if a tool is allowed to execute."""
        if self.auto_approve_all:
            return True
        return tool_name in self.ALWAYS_ALLOW
