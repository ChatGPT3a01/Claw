"""Qwen / 通義千問 provider (qwen-max / qwen-plus) — DashScope OpenAI-compatible endpoint."""
from __future__ import annotations

from .openai_compat import OpenAICompatibleProvider


class QwenProvider(OpenAICompatibleProvider):
    _BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    _default_model = "qwen-max"
    _timeout = 120
