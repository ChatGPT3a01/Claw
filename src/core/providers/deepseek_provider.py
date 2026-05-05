"""DeepSeek provider (deepseek-chat / deepseek-reasoner) — OpenAI-compatible."""
from __future__ import annotations

from .openai_compat import OpenAICompatibleProvider


class DeepSeekProvider(OpenAICompatibleProvider):
    _BASE = "https://api.deepseek.com/v1"
    _default_model = "deepseek-chat"
    _timeout = 180  # reasoner can be slow
