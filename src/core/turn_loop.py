"""Turn Loop — the core agent execution loop.

Implements the model → tool_call → execute → feedback → repeat cycle,
similar to Claude Code's queryLoop.
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger
from ..tools.base import ToolResult
from ..tools.registry import ToolRegistry
from .providers.base import ModelResponse, ToolCallData
from .model_router import ModelRouter, MODEL_REGISTRY
from .tool_permissions import ToolPermissionManager

log = get_logger("turn_loop")


@dataclass
class ToolUseRecord:
    """Record of a single tool use."""
    tool_name: str
    arguments: dict[str, Any]
    result: str
    is_error: bool


@dataclass
class TurnLoopResult:
    """Result of the complete turn loop execution."""
    final_content: str
    model_used: str
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    tool_uses: list[ToolUseRecord] = field(default_factory=list)
    turns_taken: int = 0


class TurnLoop:
    """Orchestrates the model ↔ tool execution loop.

    Flow:
    1. Call model with tool schemas
    2. If model returns tool_calls → execute tools → feed results back → goto 1
    3. If model returns text → done
    """

    def __init__(
        self,
        model_router: ModelRouter,
        tool_registry: ToolRegistry,
        permission_mgr: ToolPermissionManager | None = None,
        max_turns: int = 15,
    ):
        self.model_router = model_router
        self.tool_registry = tool_registry
        self.permission_mgr = permission_mgr or ToolPermissionManager(auto_approve_all=True)
        self.max_turns = max_turns

    async def run(
        self,
        messages: list[dict],
        model: str | None = None,
        system_prompt: str = "",
        cwd: Path | None = None,
    ) -> TurnLoopResult:
        """Run the turn loop until completion or max turns."""
        working_dir = cwd or Path.cwd()
        model_id = model or self.model_router.default_model
        provider_name = MODEL_REGISTRY.get(model_id, {}).get("provider", "")

        # Get tool schemas in the right format
        tool_schemas = self._get_schemas_for_provider(provider_name)

        # Working copy of messages
        msgs = list(messages)
        total_in = 0
        total_out = 0
        tool_uses: list[ToolUseRecord] = []

        for turn in range(self.max_turns):
            log.info("Turn %d/%d (model=%s)", turn + 1, self.max_turns, model_id)

            # Call model with tools
            resp = await self._call_model(msgs, model_id, tool_schemas, system_prompt, provider_name)
            total_in += resp.input_tokens
            total_out += resp.output_tokens

            # No tool calls → we're done
            if not resp.has_tool_calls:
                return TurnLoopResult(
                    final_content=resp.content,
                    model_used=resp.model,
                    total_input_tokens=total_in,
                    total_output_tokens=total_out,
                    tool_uses=tool_uses,
                    turns_taken=turn + 1,
                )

            # Execute tool calls
            log.info("Model requested %d tool call(s)", len(resp.tool_calls))

            # Add assistant message with tool calls
            msgs.append(self._format_assistant_tool_msg(resp, provider_name))

            # Execute each tool and collect results
            tool_results = await self._execute_tools(resp.tool_calls, working_dir, tool_uses)

            # Add tool results back to messages
            for tc, result in zip(resp.tool_calls, tool_results):
                msgs.append(self._format_tool_result_msg(tc, result, provider_name))

        # Max turns reached
        return TurnLoopResult(
            final_content="已達到最大工具呼叫輪數限制。以下是目前的進度摘要。",
            model_used=model_id,
            total_input_tokens=total_in,
            total_output_tokens=total_out,
            tool_uses=tool_uses,
            turns_taken=self.max_turns,
        )

    def _get_schemas_for_provider(self, provider_name: str) -> list[dict]:
        if provider_name == "claude":
            return self.tool_registry.get_claude_schemas()
        elif provider_name == "gemini":
            return self.tool_registry.get_gemini_function_declarations()
        else:  # openai, groq
            return self.tool_registry.get_openai_schemas()

    async def _call_model(
        self, msgs, model_id, tool_schemas, system_prompt, provider_name,
    ) -> ModelResponse:
        """Call model with fallback chain."""
        chain = [model_id] + self.model_router._fallback_chain
        seen = set()
        unique = [m for m in chain if m and m not in seen and not seen.add(m)]

        last_err = None
        for m in unique:
            pair = self.model_router._get_provider(m)
            if not pair:
                continue
            prov, mid = pair
            prov_name = MODEL_REGISTRY.get(m, {}).get("provider", "")
            schemas = self._get_schemas_for_provider(prov_name)
            try:
                return await prov.generate_with_tools(
                    messages=msgs, model_id=mid, tools=schemas,
                    system_prompt=system_prompt,
                )
            except Exception as e:
                log.warning("Model %s failed: %s", m, e)
                last_err = e
        raise RuntimeError(f"All models failed. Last error: {last_err}")

    async def _execute_tools(
        self,
        tool_calls: tuple[ToolCallData, ...],
        cwd: Path,
        records: list[ToolUseRecord],
    ) -> list[ToolResult]:
        """Execute tool calls. Read-only tools run in parallel, others serial."""
        results: list[ToolResult] = []

        # Separate read-only and write tools
        read_calls = []
        write_calls = []
        for tc in tool_calls:
            tool = self.tool_registry.get(tc.name)
            if tool and tool.is_read_only:
                read_calls.append(tc)
            else:
                write_calls.append(tc)

        # Execute read-only tools in parallel
        if read_calls:
            tasks = [self._run_one_tool(tc, cwd, records) for tc in read_calls]
            read_results = await asyncio.gather(*tasks)
            results.extend(read_results)

        # Execute write tools serially
        for tc in write_calls:
            r = await self._run_one_tool(tc, cwd, records)
            results.append(r)

        return results

    async def _run_one_tool(
        self, tc: ToolCallData, cwd: Path, records: list[ToolUseRecord],
    ) -> ToolResult:
        """Execute a single tool call."""
        if not self.permission_mgr.is_allowed(tc.name):
            result = ToolResult.error(f"Tool '{tc.name}' is not allowed by permission policy.")
        else:
            log.info("Executing tool: %s(%s)", tc.name, _brief_args(tc.arguments))
            result = await self.tool_registry.execute_tool(tc.name, tc.arguments, cwd)

        records.append(ToolUseRecord(
            tool_name=tc.name,
            arguments=tc.arguments,
            result=result.output[:500],  # Keep record brief
            is_error=result.is_error,
        ))
        return result

    def _format_assistant_tool_msg(self, resp: ModelResponse, provider: str) -> dict:
        """Format the assistant's tool call message for the conversation."""
        if provider == "claude":
            content = []
            if resp.content:
                content.append({"type": "text", "text": resp.content})
            for tc in resp.tool_calls:
                content.append({
                    "type": "tool_use",
                    "id": tc.id,
                    "name": tc.name,
                    "input": tc.arguments,
                })
            return {"role": "assistant", "content": content}

        elif provider == "gemini":
            parts = []
            if resp.content:
                parts.append({"text": resp.content})
            for tc in resp.tool_calls:
                parts.append({
                    "functionCall": {"name": tc.name, "args": tc.arguments}
                })
            return {"role": "model", "parts": parts}

        else:  # openai, groq
            msg: dict = {"role": "assistant", "content": resp.content or None}
            tool_calls = []
            for tc in resp.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments, ensure_ascii=False),
                    },
                })
            if tool_calls:
                msg["tool_calls"] = tool_calls
            return msg

    def _format_tool_result_msg(
        self, tc: ToolCallData, result: ToolResult, provider: str,
    ) -> dict:
        """Format tool execution result for the conversation."""
        output = result.output
        if result.is_error:
            output = f"[ERROR] {output}"

        if provider == "claude":
            return {
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": output,
                    "is_error": result.is_error,
                }],
            }

        elif provider == "gemini":
            return {
                "role": "user",
                "parts": [{
                    "functionResponse": {
                        "name": tc.name,
                        "response": {"result": output},
                    }
                }],
            }

        else:  # openai, groq
            return {
                "role": "tool",
                "tool_call_id": tc.id,
                "content": output,
            }


def _brief_args(args: dict, max_len: int = 80) -> str:
    """Brief representation of tool arguments for logging."""
    s = json.dumps(args, ensure_ascii=False)
    return s[:max_len] + "..." if len(s) > max_len else s
