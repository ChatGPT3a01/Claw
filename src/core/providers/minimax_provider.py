"""MiniMax provider (minimax-text-01) — non-standard API, independent implementation."""
from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from .base import ModelProvider, ModelResponse, ToolCallData

_BASE = "https://api.minimax.chat/v1"


class MiniMaxProvider(ModelProvider):
    def __init__(self, api_key: str, group_id: str = ""):
        self._api_key = api_key
        self._group_id = group_id

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def generate(
        self, messages, model_id="MiniMax-Text-01",
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> ModelResponse:
        payload = self._build(messages, model_id, max_tokens, temperature, system_prompt)
        url = f"{_BASE}/text/chatcompletion_v2"
        if self._group_id:
            url += f"?GroupId={self._group_id}"

        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(url, headers=self._headers(), json=payload)
            r.raise_for_status()
            data = r.json()

        # MiniMax returns choices similar to OpenAI
        choices = data.get("choices", [{}])
        choice = choices[0] if choices else {}
        message = choice.get("message", {})
        usage = data.get("usage", {})

        return ModelResponse(
            content=message.get("content") or "",
            model=model_id,
            input_tokens=usage.get("prompt_tokens", usage.get("total_tokens", 0)),
            output_tokens=usage.get("completion_tokens", 0),
        )

    async def generate_with_tools(
        self, messages, model_id="MiniMax-Text-01", tools=None,
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> ModelResponse:
        payload = self._build(messages, model_id, max_tokens, temperature, system_prompt)
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]
            payload["tool_choice"] = "auto"

        url = f"{_BASE}/text/chatcompletion_v2"
        if self._group_id:
            url += f"?GroupId={self._group_id}"

        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(url, headers=self._headers(), json=payload)
            r.raise_for_status()
            data = r.json()

        choices = data.get("choices", [{}])
        choice = choices[0] if choices else {}
        message = choice.get("message", {})
        usage = data.get("usage", {})
        finish_reason = choice.get("finish_reason", "stop")

        tool_calls = []
        if message.get("tool_calls"):
            for tc in message["tool_calls"]:
                fn = tc.get("function", {})
                try:
                    args = json.loads(fn.get("arguments", "{}"))
                except (json.JSONDecodeError, KeyError):
                    args = {}
                tool_calls.append(ToolCallData(
                    id=tc.get("id", f"minimax_{fn.get('name', '')}"),
                    name=fn.get("name", ""),
                    arguments=args,
                ))

        return ModelResponse(
            content=message.get("content") or "",
            model=model_id,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason="tool_use" if tool_calls else finish_reason,
            tool_calls=tuple(tool_calls),
        )

    async def generate_stream(
        self, messages, model_id="MiniMax-Text-01",
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> AsyncIterator[str]:
        payload = self._build(messages, model_id, max_tokens, temperature, system_prompt)
        payload["stream"] = True

        url = f"{_BASE}/text/chatcompletion_v2"
        if self._group_id:
            url += f"?GroupId={self._group_id}"

        async with httpx.AsyncClient(timeout=120) as c:
            async with c.stream("POST", url, headers=self._headers(), json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            choices = chunk.get("choices", [{}])
                            delta = choices[0].get("delta", {})
                            if text := delta.get("content"):
                                yield text
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue

    async def verify_api_key(self) -> bool:
        try:
            # Simple test call with minimal payload
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(
                    f"{_BASE}/text/chatcompletion_v2",
                    headers=self._headers(),
                    json={"model": "MiniMax-Text-01", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
                )
                return r.status_code in (200, 401, 403)  # 401/403 means key format valid
        except Exception:
            return False

    def _build(self, messages, model_id, max_tokens, temperature, system_prompt):
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.extend(messages)
        return {
            "model": model_id,
            "messages": msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
