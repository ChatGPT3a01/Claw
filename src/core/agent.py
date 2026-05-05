"""LiangClawAgent — the central orchestrator with Tool Use support."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncIterator

import yaml

from ..utils.config import get_config
from ..utils.logger import get_logger
from ..claw.runtime import PortRuntime
from ..skills.registry import SkillRegistry
from ..tools.registry import ToolRegistry
from .model_router import ModelRouter
from .session_manager import SessionManager, Session
from .turn_loop import TurnLoop, TurnLoopResult
from .tool_permissions import ToolPermissionManager

log = get_logger("agent")

# Re-use message types from interfaces
from interfaces.message_adapter import ChatMessage, ChatResponse


class LiangClawAgent:
    """
    Core agent that bridges:
      claw-code PortRuntime (routing) +
      SkillRegistry (education skills) +
      ModelRouter (multi-model AI) +
      ToolRegistry (file ops, bash, search) +
      TurnLoop (model ↔ tool execution cycle) +
      SessionManager (conversation state)
    """

    def __init__(self):
        cfg = get_config()
        self.runtime = PortRuntime()
        self.model_router = ModelRouter()
        self.skill_registry = SkillRegistry(cfg.skill_search_paths)
        self.tool_registry = ToolRegistry()
        self.session_mgr = SessionManager()
        self.permission_mgr = ToolPermissionManager(auto_approve_all=True)
        self._system_prompt = ""
        self._persona_path = cfg.persona_path
        self._working_dir = Path.cwd()

    async def initialize(self) -> None:
        """Async init: load persona, scan skills, verify models."""
        self._system_prompt = self._load_persona()
        n = await self.skill_registry.scan_and_load()
        log.info("Persona loaded. %d skills available. %d tools registered.",
                 n, len(self.tool_registry.all_tools()))
        status = await self.model_router.verify_connections()
        ok = [k for k, v in status.items() if v]
        log.info("Model providers ready: %s", ", ".join(ok) or "NONE")

    def set_working_dir(self, path: str | Path):
        """Set the working directory for tool execution."""
        self._working_dir = Path(path)

    async def chat(self, message: ChatMessage) -> ChatResponse:
        """Process a single chat message using the Turn Loop for tool execution."""
        session = self.session_mgr.get_or_create(message.user_id, message.session_id)

        # 1. Route via claw-code
        routed = await asyncio.to_thread(
            self.runtime.route_prompt, message.content, 5
        )
        cmd_names = [m.name for m in routed if m.kind == "command"]
        tool_names = [m.name for m in routed if m.kind == "tool"]

        # 2. Match skills
        matched_skills = self.skill_registry.match(message.content, limit=2)
        skill_context = ""
        skill_used = None
        if matched_skills:
            skill_used = matched_skills[0].manifest.name
            ctx = self.skill_registry.get_skill_context(skill_used, max_chars=3000)
            if ctx:
                skill_context = f"\n\n## 已載入技能: {skill_used}\n{ctx}"

        # 3. Build messages for the turn loop
        session.add_user(message.content)
        system = self._system_prompt + skill_context + self._tool_system_prompt()
        api_messages = session.recent(20)

        # 4. Run turn loop (model ↔ tool execution)
        try:
            turn_loop = TurnLoop(
                model_router=self.model_router,
                tool_registry=self.tool_registry,
                permission_mgr=self.permission_mgr,
                max_turns=15,
            )
            result = await turn_loop.run(
                messages=api_messages,
                model=message.model or session.model,
                system_prompt=system,
                cwd=self._working_dir,
            )
        except Exception as e:
            log.error("Turn loop failed: %s", e)
            resp_content = f"抱歉，處理失敗：{e}"
            session.add_assistant(resp_content)
            self.session_mgr.save(session)
            return ChatResponse(
                content=resp_content,
                model_used="error",
                session_id=session.session_id,
            )

        session.add_assistant(result.final_content)
        session.total_input_tokens += result.total_input_tokens
        session.total_output_tokens += result.total_output_tokens
        self.session_mgr.save(session)

        # Format tool usage records
        tool_use_records = [
            {
                "tool": tu.tool_name,
                "args_brief": str(tu.arguments)[:100],
                "is_error": tu.is_error,
            }
            for tu in result.tool_uses
        ]

        return ChatResponse(
            content=result.final_content,
            model_used=result.model_used,
            session_id=session.session_id,
            usage={
                "input_tokens": result.total_input_tokens,
                "output_tokens": result.total_output_tokens,
            },
            skill_used=skill_used,
            routed_commands=cmd_names,
            routed_tools=tool_names,
            tool_uses=tool_use_records,
        )

    async def chat_stream(self, message: ChatMessage) -> AsyncIterator[str]:
        """Streaming version (falls back to non-streaming with tool use)."""
        # For tool use, we run the full turn loop then stream the result
        resp = await self.chat(message)
        # Yield in chunks for streaming effect
        content = resp.content
        chunk_size = 20
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]

    def _load_persona(self) -> str:
        p = Path(self._persona_path)
        if p.exists():
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            return data.get("system_prompt", "")
        return "你是阿亮老師的 AI 助教 LiangClaw。請使用繁體中文回答。"

    def _tool_system_prompt(self) -> str:
        """Additional system prompt describing available tools."""
        tools = self.tool_registry.all_tools()
        if not tools:
            return ""
        lines = [
            "\n\n## 可用工具",
            "你有以下工具可以使用來完成任務。需要時請主動使用：",
        ]
        for t in tools:
            lines.append(f"- **{t.name}**: {t.description[:80]}")
        lines.append(
            "\n使用工具時，請直接呼叫對應的 function。"
            "你可以連續多次使用工具來完成複雜任務（例如：先搜尋檔案、再讀取、再編輯）。"
        )
        return "\n".join(lines)
