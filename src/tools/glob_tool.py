"""GlobSearch tool — find files by pattern."""
from __future__ import annotations

from pathlib import Path
from .base import BaseTool, ToolResult

# Directories to skip
_SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".next", ".nuxt", "coverage",
}


class GlobSearchTool(BaseTool):
    name = "glob_search"
    description = (
        "Find files matching a glob pattern. Supports patterns like '**/*.py', 'src/**/*.ts', "
        "'*.yaml', 'test_*.py'. Returns matching file paths sorted by modification time. "
        "Automatically skips node_modules, .git, __pycache__, etc."
    )
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Glob pattern to match files (e.g., '**/*.py', 'src/**/*.ts')",
            },
            "path": {
                "type": "string",
                "description": "Directory to search in. Default: working directory",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results. Default: 100",
            },
        },
        "required": ["pattern"],
    }
    is_read_only = True

    async def execute(self, args: dict, cwd: Path) -> ToolResult:
        pattern = args["pattern"]
        search_dir = args.get("path", "")
        max_results = args.get("max_results", 100)

        base = Path(search_dir) if search_dir else cwd
        if not base.is_absolute():
            base = cwd / base

        if not base.exists():
            return ToolResult.error(f"Directory not found: {base}")

        try:
            matches = []
            for p in base.glob(pattern):
                # Skip unwanted directories
                parts = p.parts
                if any(skip in parts for skip in _SKIP_DIRS):
                    continue
                if p.is_file():
                    matches.append(p)
                if len(matches) >= max_results * 2:
                    break

            # Sort by modification time (newest first)
            matches.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            matches = matches[:max_results]

            if not matches:
                return ToolResult.ok(f"No files matching '{pattern}' in {base}")

            lines = [f"Found {len(matches)} file(s) matching '{pattern}':"]
            for p in matches:
                try:
                    rel = p.relative_to(cwd)
                except ValueError:
                    rel = p
                size = p.stat().st_size
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f}KB"
                else:
                    size_str = f"{size / 1024 / 1024:.1f}MB"
                lines.append(f"  {rel}  ({size_str})")

            return ToolResult.ok("\n".join(lines))

        except Exception as e:
            return ToolResult.error(f"Glob search error: {e}")
