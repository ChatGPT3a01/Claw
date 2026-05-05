"""OpenRouter provider — aggregator for 50+ models, OpenAI-compatible."""
from __future__ import annotations

from .openai_compat import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    _BASE = "https://openrouter.ai/api/v1"
    _default_model = "openrouter/auto"
    _timeout = 120

    def _headers(self) -> dict:
        h = super()._headers()
        h["HTTP-Referer"] = "https://liangclaw.edu"
        h["X-Title"] = "LiangClaw"
        return h
