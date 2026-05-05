"""Tests for FastAPI endpoints and message adapter."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from interfaces.message_adapter import ChatMessage, ChatResponse


class TestMessageAdapter:
    def test_chat_message_defaults(self):
        msg = ChatMessage(content="hello")
        assert msg.role == "user"
        assert msg.source == "api"
        assert msg.model is None

    def test_chat_message_with_source(self):
        msg = ChatMessage(content="hi", source="telegram", user_id="t123")
        assert msg.source == "telegram"
        assert msg.user_id == "t123"

    def test_chat_response_defaults(self):
        resp = ChatResponse(content="回覆", model_used="gemini-3-flash", session_id="s1")
        assert resp.usage == {}
        assert resp.skill_used is None
        assert resp.routed_commands == []

    def test_chat_response_with_usage(self):
        resp = ChatResponse(
            content="ok",
            model_used="gpt-5.4",
            session_id="s1",
            usage={"input_tokens": 10, "output_tokens": 20},
            skill_used="lesson-plan-generator",
        )
        assert resp.usage["input_tokens"] == 10
        assert resp.skill_used == "lesson-plan-generator"


class TestFastAPIEndpoints:
    @pytest.fixture
    def client(self, mock_config, persona_file, skill_dir, tmp_path):
        mock_config.persona_path = str(persona_file)
        mock_config.skill_search_paths = [str(skill_dir)]
        mock_config.session_dir = str(tmp_path / "sessions")

        from src.core.turn_loop import TurnLoopResult

        mock_turn_result = TurnLoopResult(
            final_content="測試回應",
            model_used="gemini-3-flash",
            total_input_tokens=5,
            total_output_tokens=10,
            tool_uses=[],
            turns_taken=1,
        )

        with patch("src.core.agent.ModelRouter") as MockRouter, \
             patch("src.core.agent.TurnLoop") as MockTL:
            mock_router = MagicMock()
            mock_router.verify_connections = AsyncMock(return_value={"gemini": True})
            mock_router.list_available_models = MagicMock(return_value=[
                {"id": "gemini-3-flash", "display_name": "Gemini 3 Flash", "provider": "gemini", "available": True},
            ])
            MockRouter.return_value = mock_router
            MockTL.return_value.run = AsyncMock(return_value=mock_turn_result)

            from interfaces.app import create_app
            app = create_app()

            from fastapi.testclient import TestClient
            with TestClient(app) as c:
                yield c

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["agent"] == "LiangClaw"

    def test_list_models(self, client):
        r = client.get("/api/models")
        assert r.status_code == 200
        data = r.json()
        assert "models" in data

    def test_list_skills(self, client):
        r = client.get("/api/skills")
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "skills" in data

    def test_chat_endpoint(self, client):
        r = client.post("/api/chat", json={
            "message": "你好",
            "user_id": "test",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["content"] == "測試回應"
        assert data["model_used"] == "gemini-3-flash"

    def test_chat_with_model_override(self, client):
        r = client.post("/api/chat", json={
            "message": "test",
            "user_id": "test",
            "model": "gpt-5.4",
        })
        assert r.status_code == 200
