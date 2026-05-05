"""FileWrite tool — create or overwrite files."""
from __future__ import annotations

from pathlib import Path
from .base import BaseTool, ToolResult


class FileWriteTool(BaseTool):
    name = "file_write"
    description = (
        "Write content to a file. Creates the file and any parent directories if they don't exist. "
        "If the file already exists, it will be overwritten. "
        "Use this for creating new files or completely replacing file contents."
    )
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to write (absolute or relative to working directory)",
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file",
            },
        },
        "required": ["file_path", "content"],
    }
    is_read_only = False

    async def execute(self, args: dict, cwd: Path) -> ToolResult:
        file_path = args["file_path"]
        content = args["content"]

        p = Path(file_path)
        if not p.is_absolute():
            p = cwd / p

        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            lines = content.count("\n") + (1 if content else 0)
            return ToolResult.ok(f"Successfully wrote {len(content)} chars ({lines} lines) to {p}")
        except Exception as e:
            return ToolResult.error(f"Error writing file: {e}")
