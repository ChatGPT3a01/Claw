"""Ollama provider — local models, OpenAI-compatible endpoint."""
from __future__ import annotations

import httpx

from .openai_compat import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    _BASE = "http://localhost:11434/v1"
    _default_model = "llama3"
    _timeout = 180  # local inference can be slow

    def __init__(self, base_url: str = "http://localhost:11434/v1"):
        # No API key needed for local Ollama
        super().__init__(api_key="ollama", base_url=base_url)

    def _headers(self) -> dict:
        return {"Content-Type": "application/json"}

    async def verify_api_key(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            base = self._BASE.rstrip("/v1")
            async with httpx.AsyncClient(timeout=5) as c:
                r = await c.get(f"{base}/api/tags")
                return r.status_code == 200
        except Exception:
            return False
