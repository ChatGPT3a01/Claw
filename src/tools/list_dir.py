"""ListDirectory tool — list directory contents."""
from __future__ import annotations

from pathlib import Path
from .base import BaseTool, ToolResult


class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = (
        "List the contents of a directory. Shows files and subdirectories "
        "with their sizes. Useful for understanding project structure."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path to list. Default: working directory",
            },
            "recursive": {
                "type": "boolean",
                "description": "If true, list recursively (tree view, max 3 levels). Default: false",
            },
        },
        "required": [],
    }
    is_read_only = True

    async def execute(self, args: dict, cwd: Path) -> ToolResult:
        dir_path = args.get("path", "")
        recursive = args.get("recursive", False)

        base = Path(dir_path) if dir_path else cwd
        if not base.is_absolute():
            base = cwd / base

        if not base.exists():
            return ToolResult.error(f"Directory not found: {base}")
        if not base.is_dir():
            return ToolResult.error(f"Not a directory: {base}")

        try:
            if recursive:
                lines = [f"Directory tree: {base}\n"]
                self._tree(base, lines, prefix="", depth=0, max_depth=3)
            else:
                entries = sorted(base.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                lines = [f"Directory: {base} ({len(entries)} entries)\n"]
                for entry in entries:
                    if entry.is_dir():
                        lines.append(f"  📁 {entry.name}/")
                    else:
                        size = entry.stat().st_size
                        lines.append(f"  📄 {entry.name}  ({self._fmt_size(size)})")

            return ToolResult.ok("\n".join(lines))
        except PermissionError:
            return ToolResult.error(f"Permission denied: {base}")
        except Exception as e:
            return ToolResult.error(f"Error listing directory: {e}")

    def _tree(self, path: Path, lines: list, prefix: str, depth: int, max_depth: int):
        if depth >= max_depth:
            return
        _skip = {
            "node_modules", ".git", "__pycache__", ".venv", "venv",
            ".tox", ".mypy_cache", ".pytest_cache",
        }
        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            lines.append(f"{prefix}[permission denied]")
            return

        dirs = [e for e in entries if e.is_dir() and e.name not in _skip]
        files = [e for e in entries if e.is_file()]

        for f in files:
            lines.append(f"{prefix}📄 {f.name}")

        for i, d in enumerate(dirs):
            is_last = (i == len(dirs) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}📁 {d.name}/")
            extension = "    " if is_last else "│   "
            self._tree(d, lines, prefix + extension, depth + 1, max_depth)

    @staticmethod
    def _fmt_size(size: int) -> str:
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f}KB"
        else:
            return f"{size / 1024 / 1024:.1f}MB"
