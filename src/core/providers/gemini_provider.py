"""Google Gemini 3 provider (gemini-3-flash / gemini-3-pro)."""
from __future__ import annotations

from typing import AsyncIterator

from .base import ModelProvider, ModelResponse, ToolCallData


class GeminiProvider(ModelProvider):
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)

    def _build_contents(self, messages: list[dict], system_prompt: str) -> tuple[list, str | None]:
        contents = []
        sys_text = system_prompt or None
        for m in messages:
            role = m.get("role", "user")
            # Map roles
            if role in ("user", "tool"):
                api_role = "user"
            else:
                api_role = "model"

            content = m.get("content", "")
            parts = m.get("parts", [])

            if parts:
                contents.append({"role": api_role, "parts": parts})
            elif isinstance(content, str):
                contents.append({"role": api_role, "parts": [{"text": content}]})
            elif isinstance(content, list):
                contents.append({"role": api_role, "parts": content})
        return contents, sys_text

    async def generate(
        self, messages, model_id="gemini-3-flash",
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> ModelResponse:
        self._ensure_client()
        from google.genai import types
        contents, sys_text = self._build_contents(messages, system_prompt)
        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        if sys_text:
            config.system_instruction = sys_text
        resp = self._client.models.generate_content(
            model=model_id, contents=contents, config=config,
        )
        usage = resp.usage_metadata
        return ModelResponse(
            content=resp.text or "",
            model=model_id,
            input_tokens=getattr(usage, "prompt_token_count", 0),
            output_tokens=getattr(usage, "candidates_token_count", 0),
        )

    async def generate_with_tools(
        self, messages, model_id="gemini-3-flash", tools=None,
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> ModelResponse:
        self._ensure_client()
        from google.genai import types

        contents, sys_text = self._build_contents(messages, system_prompt)

        # Build Gemini tool declarations
        func_decls = []
        for t in (tools or []):
            func_decls.append(types.FunctionDeclaration(
                name=t["name"],
                description=t.get("description", ""),
                parameters=t.get("parameters", {}),
            ))

        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            tools=[types.Tool(function_declarations=func_decls)] if func_decls else None,
        )
        if sys_text:
            config.system_instruction = sys_text

        resp = self._client.models.generate_content(
            model=model_id, contents=contents, config=config,
        )

        usage = resp.usage_metadata
        tool_calls = []
        text_parts = []

        for candidate in resp.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    tool_calls.append(ToolCallData(
                        id=f"gemini_{fc.name}_{len(tool_calls)}",
                        name=fc.name,
                        arguments=dict(fc.args) if fc.args else {},
                    ))
                elif hasattr(part, "text") and part.text:
                    text_parts.append(part.text)

        return ModelResponse(
            content="".join(text_parts),
            model=model_id,
            input_tokens=getattr(usage, "prompt_token_count", 0),
            output_tokens=getattr(usage, "candidates_token_count", 0),
            finish_reason="tool_use" if tool_calls else "stop",
            tool_calls=tuple(tool_calls),
        )

    async def generate_stream(
        self, messages, model_id="gemini-3-flash",
        max_tokens=4096, temperature=0.7, system_prompt="",
    ) -> AsyncIterator[str]:
        self._ensure_client()
        from google.genai import types
        contents, sys_text = self._build_contents(messages, system_prompt)
        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        if sys_text:
            config.system_instruction = sys_text
        for chunk in self._client.models.generate_content_stream(
            model=model_id, contents=contents, config=config,
        ):
            if chunk.text:
                yield chunk.text

    async def verify_api_key(self) -> bool:
        try:
            self._ensure_client()
            list(self._client.models.list())
            return True
        except Exception:
            return False
