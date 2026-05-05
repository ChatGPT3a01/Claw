"""Anthropic Claude provider (claude-opus-4-6 / claude-sonnet-4-6) via httpx."""
from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from .base import ModelProvider, ModelResponse, ToolCallData

_BASE = "https://api.anthropic.com/v1"
_API_VERSION = "2023-06-01"


class ClaudeProvider(ModelProvider):
    def __init__(self, api_key: str):
        self._api_key = api_key

    def _headers(self):
        return {
            "x-api-key": self._api_key,
            "anthropic-version": _API_VERSION,
            "content-type": "application/json",
        }

    async def generate(
        self, messages, model_id="claude-sonnet-4-6",
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> ModelResponse:
        payload = self._build(messages, model_id, max_tokens, temperature, system_prompt, False)
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{_BASE}/messages", headers=self._headers(), json=payload)
            r.raise_for_status()
            data = r.json()
        text = "".join(b["text"] for b in data.get("content", []) if b["type"] == "text")
        usage = data.get("usage", {})
        return ModelResponse(
            content=text,
            model=model_id,
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            finish_reason=data.get("stop_reason", "end_turn"),
        )

    async def generate_with_tools(
        self, messages, model_id="claude-sonnet-4-6", tools=None,
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> ModelResponse:
        payload = self._build(messages, model_id, max_tokens, temperature, system_prompt, False)
        if tools:
            payload["tools"] = tools  # Claude format: [{"name":..., "input_schema":...}]

        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{_BASE}/messages", headers=self._headers(), json=payload)
            r.raise_for_status()
            data = r.json()

        usage = data.get("usage", {})
        stop_reason = data.get("stop_reason", "end_turn")

        text_parts = []
        tool_calls = []
        for block in data.get("content", []):
            if block["type"] == "text":
                text_parts.append(block["text"])
            elif block["type"] == "tool_use":
                tool_calls.append(ToolCallData(
                    id=block["id"],
                    name=block["name"],
                    arguments=block.get("input", {}),
                ))

        return ModelResponse(
            content="".join(text_parts),
            model=model_id,
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            finish_reason="tool_use" if stop_reason == "tool_use" else "stop",
            tool_calls=tuple(tool_calls),
        )

    async def generate_stream(
        self, messages, model_id="claude-sonnet-4-6",
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> AsyncIterator[str]:
        payload = self._build(messages, model_id, max_tokens, temperature, system_prompt, True)
        async with httpx.AsyncClient(timeout=120) as c:
            async with c.stream("POST", f"{_BASE}/messages", headers=self._headers(), json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            if event.get("type") == "content_block_delta":
                                text = event.get("delta", {}).get("text", "")
                                if text:
                                    yield text
                        except json.JSONDecodeError:
                            pass

    async def verify_api_key(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(
                    f"{_BASE}/messages",
                    headers=self._headers(),
                    json={"model": "claude-haiku-4-5-20251001", "max_tokens": 1, "messages": [{"role": "user", "content": "hi"}]},
                )
                return r.status_code in (200, 400)
        except Exception:
            return False

    def _build(self, messages, model_id, max_tokens, temperature, system_prompt, stream):
        payload: dict = {
            "model": model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if stream:
            payload["stream"] = True
        return payload
