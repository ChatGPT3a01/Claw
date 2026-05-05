"""Tests for LiangClawAgent core flow."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.providers.base import ModelResponse
from src.core.turn_loop import TurnLoopResult
from interfaces.message_adapter import ChatMessage, ChatResponse


def _make_turn_loop_result(content="這是測試回應。", model="gemini-3-flash"):
    """Helper to create a mock TurnLoopResult."""
    return TurnLoopResult(
        final_content=content,
        model_used=model,
        total_input_tokens=10,
        total_output_tokens=20,
        tool_uses=[],
        turns_taken=1,
    )


class TestAgent:
    @pytest.fixture
    def agent(self, mock_config, persona_file, skill_dir, tmp_path):
        mock_config.persona_path = str(persona_file)
        mock_config.skill_search_paths = [str(skill_dir)]
        mock_config.session_dir = str(tmp_path / "sessions")

        from src.core.agent import LiangClawAgent
        a = LiangClawAgent()
        return a

    @pytest.fixture
    def initialized_agent(self, agent):
        """Agent with mocked model router and TurnLoop."""
        agent.model_router = MagicMock()
        agent.model_router.verify_connections = AsyncMock(return_value={"gemini": True})

        import asyncio
        asyncio.get_event_loop().run_until_complete(agent.initialize())

        return agent

    @pytest.mark.asyncio
    async def test_initialize_loads_persona(self, initialized_agent):
        assert "測試用" in initialized_agent._system_prompt

    @pytest.mark.asyncio
    async def test_chat_returns_response(self, initialized_agent):
        mock_result = _make_turn_loop_result()
        with patch("src.core.agent.TurnLoop") as MockTL:
            MockTL.return_value.run = AsyncMock(return_value=mock_result)
            msg = ChatMessage(content="你好", user_id="test_user")
            resp = await initialized_agent.chat(msg)
        assert isinstance(resp, ChatResponse)
        assert resp.content == "這是測試回應。"
        assert resp.model_used == "gemini-3-flash"

    @pytest.mark.asyncio
    async def test_chat_saves_session(self, initialized_agent, tmp_path):
        mock_result = _make_turn_loop_result()
        with patch("src.core.agent.TurnLoop") as MockTL:
            MockTL.return_value.run = AsyncMock(return_value=mock_result)
            msg = ChatMessage(content="存檔測試", user_id="save_test")
            await initialized_agent.chat(msg)
        session = initialized_agent.session_mgr.get_or_create("save_test")
        assert len(session.messages) >= 2  # user + assistant

    @pytest.mark.asyncio
    async def test_chat_skill_matching(self, initialized_agent):
        mock_result = _make_turn_loop_result()
        with patch("src.core.agent.TurnLoop") as MockTL:
            MockTL.return_value.run = AsyncMock(return_value=mock_result)
            msg = ChatMessage(content="幫我設計教案", user_id="skill_test")
            resp = await initialized_agent.chat(msg)
        assert resp.skill_used == "lesson-plan-generator"

    @pytest.mark.asyncio
    async def test_chat_model_error_handled(self, initialized_agent):
        with patch("src.core.agent.TurnLoop") as MockTL:
            MockTL.return_value.run = AsyncMock(
                side_effect=RuntimeError("API 爆了")
            )
            msg = ChatMessage(content="test", user_id="err_test")
            resp = await initialized_agent.chat(msg)
        assert "失敗" in resp.content
        assert resp.model_used == "error"

    @pytest.mark.asyncio
    async def test_chat_with_model_override(self, initialized_agent):
        mock_result = _make_turn_loop_result(model="gpt-5.4")
        with patch("src.core.agent.TurnLoop") as MockTL:
            MockTL.return_value.run = AsyncMock(return_value=mock_result)
            msg = ChatMessage(content="test", user_id="model_test", model="gpt-5.4")
            resp = await initialized_agent.chat(msg)
            # Verify model was passed to TurnLoop.run()
            call_kwargs = MockTL.return_value.run.call_args
            assert call_kwargs.kwargs.get("model") == "gpt-5.4" or \
                   "gpt-5.4" in str(call_kwargs)


class TestSessionManager:
    def test_create_and_retrieve(self, mock_config, tmp_path):
        mock_config.session_dir = str(tmp_path / "sessions")
        from src.core.session_manager import SessionManager
        mgr = SessionManager()

        s = mgr.get_or_create("user1")
        s.add_user("hello")
        s.add_assistant("hi")
        mgr.save(s)

        # New manager should load from disk
        mgr2 = SessionManager()
        s2 = mgr2.get_or_create("user1", s.session_id)
        assert len(s2.messages) == 2
        assert s2.messages[0]["content"] == "hello"

    def test_session_recent(self, mock_config, tmp_path):
        mock_config.session_dir = str(tmp_path / "sessions")
        from src.core.session_manager import Session
        s = Session(session_id="test", user_id="u1")
        for i in range(30):
            s.add_user(f"msg {i}")
        recent = s.recent(5)
        assert len(recent) == 5
        assert recent[-1]["content"] == "msg 29"

    def test_session_compact(self, mock_config, tmp_path):
        mock_config.session_dir = str(tmp_path / "sessions")
        from src.core.session_manager import Session
        s = Session(session_id="test", user_id="u1")
        for i in range(30):
            s.add_user(f"msg {i}")
        s.compact(keep=5)
        assert len(s.messages) == 5
