"""Multi-model router with fallback chain."""
from __future__ import annotations

from typing import AsyncIterator

from ..utils.config import get_config
from ..utils.logger import get_logger
from .providers import (
    ModelProvider, ModelResponse,
    GeminiProvider, OpenAIProvider, GroqProvider, ClaudeProvider,
    DeepSeekProvider, QwenProvider, OpenRouterProvider,
    MistralProvider, OllamaProvider, MiniMaxProvider,
)

log = get_logger("model_router")

# 2026-04 model registry — 10 providers, 18+ models
MODEL_REGISTRY: dict[str, dict] = {
    # Gemini
    "gemini-3-flash":          {"provider": "gemini",      "display": "Gemini 3 Flash"},
    "gemini-3-pro":            {"provider": "gemini",      "display": "Gemini 3 Pro"},
    # OpenAI
    "gpt-5.4":                 {"provider": "openai",      "display": "GPT-5.4"},
    "gpt-5.4-pro":             {"provider": "openai",      "display": "GPT-5.4 Pro (最強)"},
    # Groq (免費)
    "llama-3.3-70b-versatile": {"provider": "groq",        "display": "Llama 3.3 70B (Groq, 免費)"},
    "qwen-3-32b":              {"provider": "groq",        "display": "Qwen 3 32B (Groq)"},
    # Claude
    "claude-opus-4-6":         {"provider": "claude",      "display": "Claude Opus 4.6"},
    "claude-sonnet-4-6":       {"provider": "claude",      "display": "Claude Sonnet 4.6"},
    # DeepSeek
    "deepseek-chat":           {"provider": "deepseek",    "display": "DeepSeek V3 (便宜)"},
    "deepseek-reasoner":       {"provider": "deepseek",    "display": "DeepSeek R1 (推理)"},
    # Qwen / 通義千問
    "qwen-max":                {"provider": "qwen",        "display": "通義千問 Max"},
    "qwen-plus":               {"provider": "qwen",        "display": "通義千問 Plus (便宜)"},
    # OpenRouter (聚合平台)
    "openrouter/auto":         {"provider": "openrouter",  "display": "OpenRouter Auto (50+ 模型)"},
    # Mistral
    "mistral-large-latest":    {"provider": "mistral",     "display": "Mistral Large"},
    "mistral-small-latest":    {"provider": "mistral",     "display": "Mistral Small (便宜)"},
    # MiniMax
    "minimax-text-01":         {"provider": "minimax",     "display": "MiniMax Text 01 (多模態)"},
    # Ollama (本地)
    "ollama/llama3":           {"provider": "ollama",      "display": "Ollama Llama3 (本地免費)"},
}


class ModelRouter:
    """Routes generation requests to the appropriate provider with fallback."""

    def __init__(self, default_model: str | None = None):
        cfg = get_config()
        self.default_model = default_model or cfg.default_model
        self._fallback_chain = cfg.fallback_chain
        self._providers: dict[str, ModelProvider] = {}
        self._init_providers(cfg)

    def _init_providers(self, cfg):
        if cfg.gemini_api_key:
            self._providers["gemini"] = GeminiProvider(cfg.gemini_api_key)
        if cfg.openai_api_key:
            self._providers["openai"] = OpenAIProvider(cfg.openai_api_key)
        if cfg.groq_api_key:
            self._providers["groq"] = GroqProvider(cfg.groq_api_key)
        if cfg.anthropic_api_key:
            self._providers["claude"] = ClaudeProvider(cfg.anthropic_api_key)
        if cfg.deepseek_api_key:
            self._providers["deepseek"] = DeepSeekProvider(cfg.deepseek_api_key)
        if cfg.dashscope_api_key:
            self._providers["qwen"] = QwenProvider(cfg.dashscope_api_key)
        if cfg.openrouter_api_key:
            self._providers["openrouter"] = OpenRouterProvider(cfg.openrouter_api_key)
        if cfg.mistral_api_key:
            self._providers["mistral"] = MistralProvider(cfg.mistral_api_key)
        if cfg.minimax_api_key:
            self._providers["minimax"] = MiniMaxProvider(cfg.minimax_api_key, cfg.minimax_group_id)
        if cfg.ollama_base_url:
            self._providers["ollama"] = OllamaProvider(cfg.ollama_base_url)

    def _get_provider(self, model: str) -> tuple[ModelProvider, str] | None:
        info = MODEL_REGISTRY.get(model)
        if not info:
            return None
        provider = self._providers.get(info["provider"])
        if not provider:
            return None
        return provider, model

    async def generate(
        self,
        messages: list[dict],
        model: str | None = None,
        system_prompt: str = "",
        **kwargs,
    ) -> ModelResponse:
        chain = [model] if model else []
        chain.extend(self._fallback_chain)
        # deduplicate while preserving order
        seen: set[str] = set()
        unique = []
        for m in chain:
            if m and m not in seen:
                seen.add(m)
                unique.append(m)

        last_err: Exception | None = None
        for m in unique:
            pair = self._get_provider(m)
            if not pair:
                continue
            prov, model_id = pair
            try:
                return await prov.generate(messages, model_id, system_prompt=system_prompt, **kwargs)
            except Exception as e:
                log.warning("Model %s failed: %s — trying next", m, e)
                last_err = e
        raise RuntimeError(f"All models failed. Last error: {last_err}")

    async def generate_with_tools(
        self,
        messages: list[dict],
        model: str | None = None,
        tools: list[dict] | None = None,
        system_prompt: str = "",
        **kwargs,
    ) -> ModelResponse:
        """Generate with function calling support + fallback."""
        chain = [model] if model else []
        chain.extend(self._fallback_chain)
        seen: set[str] = set()
        unique = [m for m in chain if m and m not in seen and not seen.add(m)]

        last_err: Exception | None = None
        for m in unique:
            pair = self._get_provider(m)
            if not pair:
                continue
            prov, model_id = pair
            try:
                return await prov.generate_with_tools(
                    messages, model_id, tools=tools,
                    system_prompt=system_prompt, **kwargs,
                )
            except Exception as e:
                log.warning("Model %s failed: %s — trying next", m, e)
                last_err = e
        raise RuntimeError(f"All models failed. Last error: {last_err}")

    async def generate_stream(
        self,
        messages: list[dict],
        model: str | None = None,
        system_prompt: str = "",
        **kwargs,
    ) -> AsyncIterator[str]:
        target = model or self.default_model
        pair = self._get_provider(target)
        if not pair:
            raise ValueError(f"Model {target} not available")
        prov, model_id = pair
        async for chunk in prov.generate_stream(messages, model_id, system_prompt=system_prompt, **kwargs):
            yield chunk

    async def verify_connections(self) -> dict[str, bool]:
        results = {}
        for name, prov in self._providers.items():
            results[name] = await prov.verify_api_key()
            log.info("Provider %s: %s", name, "OK" if results[name] else "FAILED")
        return results

    def list_available_models(self) -> list[dict]:
        out = []
        for model_id, info in MODEL_REGISTRY.items():
            available = info["provider"] in self._providers
            out.append({
                "id": model_id,
                "display_name": info["display"],
                "provider": info["provider"],
                "available": available,
            })
        return out
