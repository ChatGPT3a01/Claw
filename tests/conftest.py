"""Shared fixtures for LiangClaw tests."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Ensure project root is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def mock_config(monkeypatch, tmp_path):
    """Provide a minimal AppConfig for tests."""
    from src.utils.config import AppConfig

    cfg = AppConfig(
        gemini_api_key="test-gemini-key",
        openai_api_key="",
        groq_api_key="test-groq-key",
        anthropic_api_key="",
        default_model="gemini-3-flash",
        fallback_chain=["gemini-3-flash", "llama-3.3-70b-versatile"],
        skill_search_paths=[str(tmp_path / "skills")],
        persona_path=str(tmp_path / "persona.yaml"),
        session_dir=str(tmp_path / "sessions"),
    )

    import src.utils.config as config_mod
    monkeypatch.setattr(config_mod, "_config", cfg)
    return cfg


@pytest.fixture
def skill_dir(tmp_path):
    """Create a temp skill directory with a sample skill."""
    skill_root = tmp_path / "skills"
    s1 = skill_root / "lesson-plan-generator"
    s1.mkdir(parents=True)
    (s1 / "SKILL.md").write_text(
        "# lesson-plan-generator\n\n"
        "教案產生器：根據教學目標自動生成教案。\n\n"
        "關鍵字：教案, 教學設計, lesson plan\n",
        encoding="utf-8",
    )
    (s1 / "manifest.json").write_text(
        '{"name":"lesson-plan-generator","displayName":"教案產生器",'
        '"version":"1.0.0","description":"自動生成教案",'
        '"author":"test","tags":["teaching-design"]}',
        encoding="utf-8",
    )

    s2 = skill_root / "learning-analytics-tool"
    s2.mkdir(parents=True)
    (s2 / "SKILL.md").write_text(
        "# learning-analytics-tool\n\n學習分析工具。\n",
        encoding="utf-8",
    )

    # A directory without SKILL.md (should be ignored)
    (skill_root / "no-skill-dir").mkdir()

    return skill_root


@pytest.fixture
def persona_file(tmp_path):
    """Create a temp persona YAML."""
    p = tmp_path / "persona.yaml"
    p.write_text(
        'system_prompt: "你是測試用 AI 助教。"\n',
        encoding="utf-8",
    )
    return p


@pytest.fixture
def mock_model_response():
    """A mock ModelResponse for provider tests."""
    from src.core.providers.base import ModelResponse
    return ModelResponse(
        content="這是測試回應。",
        model="gemini-3-flash",
        input_tokens=10,
        output_tokens=20,
    )
