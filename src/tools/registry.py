"""Tool Registry — manages all available tools and schema conversion."""
from __future__ import annotations

from pathlib import Path
from .base import BaseTool, ToolResult, ToolCall
from .file_read import FileReadTool
from .file_write import FileWriteTool
from .file_edit import FileEditTool
from .bash_tool import BashExecuteTool
from .glob_tool import GlobSearchTool
from .grep_tool import GrepSearchTool
from .web_fetch import WebFetchTool
from .list_dir import ListDirectoryTool


class ToolRegistry:
    """Manages tool instances and provides schema conversion for different providers."""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self):
        for tool_cls in [
            FileReadTool,
            FileWriteTool,
            FileEditTool,
            BashExecuteTool,
            GlobSearchTool,
            GrepSearchTool,
            WebFetchTool,
            ListDirectoryTool,
        ]:
            tool = tool_cls()
            self._tools[tool.name] = tool

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def all_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_openai_schemas(self) -> list[dict]:
        """Get all tool schemas in OpenAI/Groq format."""
        return [t.to_openai_schema() for t in self._tools.values()]

    def get_claude_schemas(self) -> list[dict]:
        """Get all tool schemas in Anthropic format."""
        return [t.to_claude_schema() for t in self._tools.values()]

    def get_gemini_function_declarations(self) -> list[dict]:
        """Get all tool schemas in Gemini format."""
        return [t.to_gemini_schema() for t in self._tools.values()]

    async def execute_tool(self, name: str, args: dict, cwd: Path) -> ToolResult:
        """Execute a tool by name."""
        tool = self._tools.get(name)
        if not tool:
            return ToolResult.error(f"Unknown tool: {name}")
        return await tool.execute(args, cwd)

    def list_tools(self) -> list[dict]:
        """List all tools with metadata."""
        return [
            {
                "name": t.name,
                "description": t.description[:100],
                "is_read_only": t.is_read_only,
            }
            for t in self._tools.values()
        ]
