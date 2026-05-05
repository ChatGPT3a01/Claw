"""Tests for model router and providers."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.providers.base import ModelProvider, ModelResponse
from src.core.model_router import ModelRouter, MODEL_REGISTRY


class TestModelRegistry:
    def test_all_models_have_provider(self):
        valid_providers = {"gemini", "openai", "groq", "claude", "deepseek", "qwen", "openrouter", "mistral", "minimax", "ollama"}
        for model_id, info in MODEL_REGISTRY.items():
            assert info["provider"] in valid_providers, f"{model_id} has invalid provider"

    def test_gemini_3_models_exist(self):
        assert "gemini-3-flash" in MODEL_REGISTRY
        assert "gemini-3-pro" in MODEL_REGISTRY

    def test_gpt_54_models_exist(self):
        assert "gpt-5.4" in MODEL_REGISTRY
        assert "gpt-5.4-pro" in MODEL_REGISTRY

    def test_no_deprecated_models(self):
        for model_id in MODEL_REGISTRY:
            assert "2.5" not in model_id, f"Deprecated model found: {model_id}"
            assert "gpt-4" not in model_id, f"Deprecated model found: {model_id}"


class TestModelRouter:
    @pytest.fixture
    def mock_provider(self, mock_model_response):
        provider = MagicMock(spec=ModelProvider)
        provider.generate = AsyncMock(return_value=mock_model_response)
        provider.verify_api_key = AsyncMock(return_value=True)

        async def stream_gen(*args, **kwargs):
            for chunk in ["你", "好", "！"]:
                yield chunk

        provider.generate_stream = stream_gen
        return provider

    @pytest.fixture
    def router(self, mock_config, mock_provider):
        r = ModelRouter()
        r._providers = {"gemini": mock_provider, "groq": mock_provider}
        return r

    @pytest.mark.asyncio
    async def test_generate_default_model(self, router):
        resp = await router.generate(
            messages=[{"role": "user", "content": "你好"}],
        )
        assert resp.content == "這是測試回應。"
        assert resp.model == "gemini-3-flash"

    @pytest.mark.asyncio
    async def test_generate_specific_model(self, router):
        resp = await router.generate(
            messages=[{"role": "user", "content": "test"}],
            model="gemini-3-flash",
        )
        assert resp.content == "這是測試回應。"

    @pytest.mark.asyncio
    async def test_fallback_on_failure(self, router, mock_model_response):
        fail_provider = MagicMock(spec=ModelProvider)
        fail_provider.generate = AsyncMock(side_effect=RuntimeError("API error"))
        ok_provider = MagicMock(spec=ModelProvider)
        ok_provider.generate = AsyncMock(return_value=mock_model_response)

        router._providers = {"gemini": fail_provider, "groq": ok_provider}
        resp = await router.generate(
            messages=[{"role": "user", "content": "test"}],
            model="gemini-3-flash",
        )
        assert resp.content == "這是測試回應。"

    @pytest.mark.asyncio
    async def test_all_fail_raises(self, router):
        fail_provider = MagicMock(spec=ModelProvider)
        fail_provider.generate = AsyncMock(side_effect=RuntimeError("fail"))
        router._providers = {"gemini": fail_provider, "groq": fail_provider}

        with pytest.raises(RuntimeError, match="All models failed"):
            await router.generate(
                messages=[{"role": "user", "content": "test"}],
            )

    @pytest.mark.asyncio
    async def test_stream(self, router):
        chunks = []
        async for c in router.generate_stream(
            messages=[{"role": "user", "content": "test"}],
            model="gemini-3-flash",
        ):
            chunks.append(c)
        assert "".join(chunks) == "你好！"

    @pytest.mark.asyncio
    async def test_verify_connections(self, router):
        status = await router.verify_connections()
        assert status["gemini"] is True

    def test_list_available_models(self, router):
        models = router.list_available_models()
        assert len(models) == len(MODEL_REGISTRY)
        gemini = [m for m in models if m["id"] == "gemini-3-flash"][0]
        assert gemini["available"] is True
        openai = [m for m in models if m["id"] == "gpt-5.4"][0]
        assert openai["available"] is False  # no openai provider mocked
