"""Mistral provider (mistral-large-latest / mistral-small-latest) — OpenAI-compatible."""
from __future__ import annotations

from .openai_compat import OpenAICompatibleProvider


class MistralProvider(OpenAICompatibleProvider):
    _BASE = "https://api.mistral.ai/v1"
    _default_model = "mistral-large-latest"
    _timeout = 120
