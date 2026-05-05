"""Configuration loader — .env + YAML."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _root(*parts: str) -> Path:
    return _PROJECT_ROOT.joinpath(*parts)


load_dotenv(_root(".env"))


@dataclass
class AppConfig:
    """Resolved application config (env + yaml merged)."""

    # AI Keys — 原有
    gemini_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""
    anthropic_api_key: str = ""

    # AI Keys — 新增 (v3)
    deepseek_api_key: str = ""
    dashscope_api_key: str = ""
    openrouter_api_key: str = ""
    mistral_api_key: str = ""
    minimax_api_key: str = ""
    minimax_group_id: str = ""
    ollama_base_url: str = "http://localhost:11434/v1"

    # LINE
    line_channel_access_token: str = ""
    line_channel_secret: str = ""

    # Telegram
    telegram_bot_token: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Models
    default_model: str = "gemini-3-flash"
    fallback_chain: list[str] = field(default_factory=lambda: [
        "gemini-3-flash", "llama-3.3-70b-versatile",
    ])

    # Skills
    skill_search_paths: list[str] = field(default_factory=lambda: [
        "C:/Users/user/.claude/skills",
        str(_root("skills", "bundled")),
    ])

    # Persona
    persona_path: str = str(_root("config", "personas", "aliang.yaml"))

    # Session
    session_dir: str = str(_root("data", "sessions"))


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def load_config() -> AppConfig:
    """Load config from .env + config/default.yaml."""
    yaml_path = _root("config", "default.yaml")
    yaml_cfg: dict = {}
    if yaml_path.exists():
        yaml_cfg = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}

    models_cfg = yaml_cfg.get("models", {})
    skills_cfg = yaml_cfg.get("skills", {})
    app_cfg = yaml_cfg.get("app", {})

    return AppConfig(
        gemini_api_key=_env("GEMINI_API_KEY"),
        openai_api_key=_env("OPENAI_API_KEY"),
        groq_api_key=_env("GROQ_API_KEY"),
        anthropic_api_key=_env("ANTHROPIC_API_KEY"),
        deepseek_api_key=_env("DEEPSEEK_API_KEY"),
        dashscope_api_key=_env("DASHSCOPE_API_KEY"),
        openrouter_api_key=_env("OPENROUTER_API_KEY"),
        mistral_api_key=_env("MISTRAL_API_KEY"),
        minimax_api_key=_env("MINIMAX_API_KEY"),
        minimax_group_id=_env("MINIMAX_GROUP_ID"),
        ollama_base_url=_env("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        line_channel_access_token=_env("LINE_CHANNEL_ACCESS_TOKEN"),
        line_channel_secret=_env("LINE_CHANNEL_SECRET"),
        telegram_bot_token=_env("TELEGRAM_BOT_TOKEN"),
        host=_env("HOST", app_cfg.get("host", "0.0.0.0")),
        port=int(_env("PORT", str(app_cfg.get("port", 8000)))),
        debug=_env("DEBUG", str(app_cfg.get("debug", False))).lower() in ("true", "1"),
        default_model=models_cfg.get("default", "gemini-3-flash"),
        fallback_chain=models_cfg.get("fallback_chain", ["gemini-3-flash", "llama-3.3-70b-versatile"]),
        skill_search_paths=skills_cfg.get("search_paths", [
            "C:/Users/user/.claude/skills",
            str(_root("skills", "bundled")),
        ]),
        persona_path=str(_root("config", "personas", "aliang.yaml")),
        session_dir=str(_root("data", "sessions")),
    )


# Singleton
_config: AppConfig | None = None


def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = load_config()
    return _config
