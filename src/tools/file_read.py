"""FileRead tool — read file contents with optional line range."""
from __future__ import annotations

from pathlib import Path
from .base import BaseTool, ToolResult


class FileReadTool(BaseTool):
    name = "file_read"
    description = (
        "Read the contents of a file. Returns the file content with line numbers. "
        "You can optionally specify offset (starting line) and limit (number of lines). "
        "Supports text files, code files, JSON, YAML, Markdown, etc."
    )
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read (absolute or relative to working directory)",
            },
            "offset": {
                "type": "integer",
                "description": "Starting line number (1-based). Default: 1",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of lines to read. Default: 2000",
            },
        },
        "required": ["file_path"],
    }
    is_read_only = True

    async def execute(self, args: dict, cwd: Path) -> ToolResult:
        file_path = args["file_path"]
        offset = args.get("offset", 1)
        limit = args.get("limit", 2000)

        p = Path(file_path)
        if not p.is_absolute():
            p = cwd / p

        if not p.exists():
            return ToolResult.error(f"File not found: {p}")
        if not p.is_file():
            return ToolResult.error(f"Not a file: {p}")

        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = p.read_text(encoding="cp950")
            except Exception:
                return ToolResult.error(f"Cannot read file (binary or unknown encoding): {p}")
        except Exception as e:
            return ToolResult.error(f"Error reading file: {e}")

        lines = content.splitlines()
        total = len(lines)

        start = max(0, offset - 1)
        end = min(total, start + limit)
        selected = lines[start:end]

        numbered = []
        for i, line in enumerate(selected, start=start + 1):
            # Truncate very long lines
            if len(line) > 2000:
                line = line[:2000] + "..."
            numbered.append(f"{i:>6}\t{line}")

        header = f"File: {p} ({total} lines total)"
        if start > 0 or end < total:
            header += f" [showing lines {start + 1}-{end}]"

        return ToolResult.ok(f"{header}\n{'─' * 60}\n" + "\n".join(numbered))
