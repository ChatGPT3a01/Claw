"""FileEdit tool — find and replace text in files."""
from __future__ import annotations

from pathlib import Path
from .base import BaseTool, ToolResult


class FileEditTool(BaseTool):
    name = "file_edit"
    description = (
        "Edit a file by replacing specific text. Finds the exact old_string in the file "
        "and replaces it with new_string. The old_string must be unique in the file "
        "(unless replace_all is true). Use this for targeted edits rather than rewriting entire files."
    )
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to edit",
            },
            "old_string": {
                "type": "string",
                "description": "The exact text to find and replace (must match exactly including whitespace)",
            },
            "new_string": {
                "type": "string",
                "description": "The text to replace it with",
            },
            "replace_all": {
                "type": "boolean",
                "description": "If true, replace all occurrences. Default: false",
            },
        },
        "required": ["file_path", "old_string", "new_string"],
    }
    is_read_only = False

    async def execute(self, args: dict, cwd: Path) -> ToolResult:
        file_path = args["file_path"]
        old_string = args["old_string"]
        new_string = args["new_string"]
        replace_all = args.get("replace_all", False)

        p = Path(file_path)
        if not p.is_absolute():
            p = cwd / p

        if not p.exists():
            return ToolResult.error(f"File not found: {p}")

        try:
            content = p.read_text(encoding="utf-8")
        except Exception as e:
            return ToolResult.error(f"Error reading file: {e}")

        count = content.count(old_string)
        if count == 0:
            return ToolResult.error(
                f"old_string not found in {p}. Make sure the text matches exactly."
            )

        if count > 1 and not replace_all:
            return ToolResult.error(
                f"old_string found {count} times in {p}. "
                f"Set replace_all=true to replace all, or provide more context to make it unique."
            )

        if replace_all:
            new_content = content.replace(old_string, new_string)
            replaced = count
        else:
            new_content = content.replace(old_string, new_string, 1)
            replaced = 1

        try:
            p.write_text(new_content, encoding="utf-8")
            return ToolResult.ok(f"Replaced {replaced} occurrence(s) in {p}")
        except Exception as e:
            return ToolResult.error(f"Error writing file: {e}")
