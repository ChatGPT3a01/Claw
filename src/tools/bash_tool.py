"""BashExecute tool — run shell commands."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from .base import BaseTool, ToolResult


class BashExecuteTool(BaseTool):
    name = "bash_execute"
    description = (
        "Execute a shell command and return its output. "
        "Supports any shell command: python, git, npm, pip, curl, etc. "
        "Commands run in the working directory. "
        "Timeout: 120 seconds. Use this for running scripts, installing packages, "
        "git operations, testing code, and any terminal tasks."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute (e.g., 'python main.py', 'git status', 'pip install requests')",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds. Default: 120, Max: 300",
            },
        },
        "required": ["command"],
    }
    is_read_only = False

    async def execute(self, args: dict, cwd: Path) -> ToolResult:
        command = args["command"]
        timeout = min(args.get("timeout", 120), 300)

        try:
            # Use shell=True for full shell features
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(cwd),
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return ToolResult.error(
                    f"Command timed out after {timeout}s: {command}"
                )

            stdout_text = stdout.decode("utf-8", errors="replace") if stdout else ""
            stderr_text = stderr.decode("utf-8", errors="replace") if stderr else ""

            output_parts = []
            if stdout_text:
                output_parts.append(stdout_text)
            if stderr_text:
                output_parts.append(f"[STDERR]\n{stderr_text}")

            output = "\n".join(output_parts) or "(no output)"
            exit_code = proc.returncode

            if exit_code != 0:
                output = f"[Exit code: {exit_code}]\n{output}"

            return ToolResult.ok(output)

        except Exception as e:
            return ToolResult.error(f"Error executing command: {e}")
