"""GrepSearch tool — search file contents by regex."""
from __future__ import annotations

import re
from pathlib import Path
from .base import BaseTool, ToolResult

_SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
}

_BINARY_EXTENSIONS = {
    ".pyc", ".pyo", ".exe", ".dll", ".so", ".dylib",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".woff", ".woff2", ".ttf", ".eot",
}


class GrepSearchTool(BaseTool):
    name = "grep_search"
    description = (
        "Search for a regex pattern in file contents. Returns matching lines with file paths "
        "and line numbers. Supports full regex syntax. Can filter by file extension. "
        "Automatically skips binary files, node_modules, .git, etc."
    )
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Regex pattern to search for (e.g., 'def main', 'import.*os', 'TODO')",
            },
            "path": {
                "type": "string",
                "description": "File or directory to search in. Default: working directory",
            },
            "file_extension": {
                "type": "string",
                "description": "Filter by extension (e.g., '.py', '.js', '.yaml')",
            },
            "case_insensitive": {
                "type": "boolean",
                "description": "Case-insensitive search. Default: false",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of matching lines. Default: 50",
            },
            "context_lines": {
                "type": "integer",
                "description": "Number of context lines before/after match. Default: 0",
            },
        },
        "required": ["pattern"],
    }
    is_read_only = True

    async def execute(self, args: dict, cwd: Path) -> ToolResult:
        pattern = args["pattern"]
        search_path = args.get("path", "")
        file_ext = args.get("file_extension", "")
        case_insensitive = args.get("case_insensitive", False)
        max_results = args.get("max_results", 50)
        context_lines = args.get("context_lines", 0)

        base = Path(search_path) if search_path else cwd
        if not base.is_absolute():
            base = cwd / base

        if not base.exists():
            return ToolResult.error(f"Path not found: {base}")

        flags = re.IGNORECASE if case_insensitive else 0
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            return ToolResult.error(f"Invalid regex pattern: {e}")

        results = []
        files_searched = 0
        files_matched = 0

        def search_file(fp: Path):
            nonlocal files_searched, files_matched
            if fp.suffix.lower() in _BINARY_EXTENSIONS:
                return
            files_searched += 1
            try:
                content = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                return

            lines = content.splitlines()
            file_has_match = False
            for i, line in enumerate(lines):
                if regex.search(line):
                    if not file_has_match:
                        files_matched += 1
                        file_has_match = True

                    try:
                        rel = fp.relative_to(cwd)
                    except ValueError:
                        rel = fp

                    if context_lines > 0:
                        start = max(0, i - context_lines)
                        end = min(len(lines), i + context_lines + 1)
                        ctx = []
                        for j in range(start, end):
                            prefix = ">" if j == i else " "
                            ctx.append(f"  {prefix} {j + 1:>5}\t{lines[j]}")
                        results.append(f"{rel}:{i + 1}:\n" + "\n".join(ctx))
                    else:
                        results.append(f"{rel}:{i + 1}:\t{line.rstrip()}")

                    if len(results) >= max_results:
                        return

        if base.is_file():
            search_file(base)
        else:
            for fp in sorted(base.rglob("*")):
                if any(skip in fp.parts for skip in _SKIP_DIRS):
                    continue
                if file_ext and fp.suffix.lower() != file_ext.lower():
                    continue
                if fp.is_file():
                    search_file(fp)
                if len(results) >= max_results:
                    break

        if not results:
            return ToolResult.ok(
                f"No matches for '{pattern}' in {base} ({files_searched} files searched)"
            )

        header = (
            f"Found {len(results)} match(es) in {files_matched} file(s) "
            f"({files_searched} searched):"
        )
        if len(results) >= max_results:
            header += f" (limited to {max_results})"

        return ToolResult.ok(header + "\n\n" + "\n".join(results))
