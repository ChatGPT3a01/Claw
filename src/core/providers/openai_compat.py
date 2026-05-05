"""OpenAI-compatible provider base — shared by DeepSeek, Qwen, OpenRouter, Mistral, Ollama."""
from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from .base import ModelProvider, ModelResponse, ToolCallData


class OpenAICompatibleProvider(ModelProvider):
    """Base for any provider that exposes an OpenAI-compatible API.

    Subclasses only need to set ``_BASE`` and optionally override
    ``_headers()`` or ``_default_model``.
    """

    _BASE: str = ""
    _default_model: str = ""
    _timeout: int = 120

    def __init__(self, api_key: str, base_url: str | None = None):
        self._api_key = api_key
        if base_url:
            self._BASE = base_url.rstrip("/")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    # ---- generate ----

    async def generate(
        self, messages, model_id=None,
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> ModelResponse:
        mid = model_id or self._default_model
        payload = self._build(messages, mid, max_tokens, temperature, system_prompt, stream=False)
        async with httpx.AsyncClient(timeout=self._timeout) as c:
            r = await c.post(f"{self._BASE}/chat/completions", headers=self._headers(), json=payload)
            r.raise_for_status()
            data = r.json()
        choice = data["choices"][0]
        usage = data.get("usage", {})
        return ModelResponse(
            content=choice["message"].get("content") or "",
            model=mid,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
        )

    # ---- generate_with_tools ----

    async def generate_with_tools(
        self, messages, model_id=None, tools=None,
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> ModelResponse:
        mid = model_id or self._default_model
        payload = self._build(messages, mid, max_tokens, temperature, system_prompt, stream=False)
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=self._timeout) as c:
            r = await c.post(f"{self._BASE}/chat/completions", headers=self._headers(), json=payload)
            r.raise_for_status()
            data = r.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})
        message = choice["message"]
        finish_reason = choice.get("finish_reason", "stop")

        tool_calls = []
        if message.get("tool_calls"):
            for tc in message["tool_calls"]:
                if tc["type"] == "function":
                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except (json.JSONDecodeError, KeyError):
                        args = {}
                    tool_calls.append(ToolCallData(
                        id=tc["id"],
                        name=tc["function"]["name"],
                        arguments=args,
                    ))

        return ModelResponse(
            content=message.get("content") or "",
            model=mid,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason="tool_use" if finish_reason == "tool_calls" else finish_reason,
            tool_calls=tuple(tool_calls),
        )

    # ---- stream ----

    async def generate_stream(
        self, messages, model_id=None,
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> AsyncIterator[str]:
        mid = model_id or self._default_model
        payload = self._build(messages, mid, max_tokens, temperature, system_prompt, stream=True)
        async with httpx.AsyncClient(timeout=self._timeout) as c:
            async with c.stream("POST", f"{self._BASE}/chat/completions",
                                headers=self._headers(), json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0].get("delta", {})
                            if text := delta.get("content"):
                                yield text
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue

    # ---- verify ----

    async def verify_api_key(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{self._BASE}/models", headers=self._headers())
                return r.status_code == 200
        except Exception:
            return False

    # ---- helpers ----

    def _build(self, messages, model_id, max_tokens, temperature, system_prompt, stream):
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.extend(messages)
        return {
            "model": model_id,
            "messages": msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
        }
