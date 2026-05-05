"""FastAPI main application — mounts Gradio, LINE, Telegram webhooks."""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Ensure project root is on sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.agent import LiangClawAgent
from interfaces.message_adapter import ChatMessage, ChatResponse


# ---------- Pydantic Schemas ----------

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    model: str | None = None
    user_id: str = "api_user"

class ChatResponseSchema(BaseModel):
    content: str
    model_used: str
    session_id: str
    usage: dict = {}
    skill_used: str | None = None
    tool_uses: list[dict] = []


# ---------- Singleton agent accessor ----------

_agent: LiangClawAgent | None = None

def get_agent() -> LiangClawAgent:
    assert _agent is not None, "Agent not initialized"
    return _agent


# ---------- App Factory ----------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _agent
    _agent = LiangClawAgent()
    await _agent.initialize()
    yield
    _agent = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="Claw API",
        description="Claw — 三 AI CLI 切換器（Claude · Gemini · Codex）+ 80+ 教育技能",
        version="2.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ----- REST API -----

    @app.post("/api/chat", response_model=ChatResponseSchema)
    async def chat_endpoint(req: ChatRequest):
        agent = get_agent()
        msg = ChatMessage(
            content=req.message,
            source="api",
            user_id=req.user_id,
            session_id=req.session_id or "",
            model=req.model,
        )
        resp = await agent.chat(msg)
        return ChatResponseSchema(
            content=resp.content,
            model_used=resp.model_used,
            session_id=resp.session_id,
            usage=resp.usage,
            skill_used=resp.skill_used,
            tool_uses=resp.tool_uses,
        )

    @app.get("/api/skills")
    async def list_skills():
        agent = get_agent()
        skills = agent.skill_registry.list_skills()
        return {"total": len(skills), "skills": skills}

    @app.get("/api/models")
    async def list_models():
        agent = get_agent()
        return {"models": agent.model_router.list_available_models()}

    @app.get("/api/tools")
    async def list_tools():
        agent = get_agent()
        return {"tools": agent.tool_registry.list_tools()}

    @app.post("/api/set-workdir")
    async def set_workdir(req: dict):
        agent = get_agent()
        path = req.get("path", "")
        if path:
            agent.set_working_dir(path)
            return {"status": "ok", "working_dir": path}
        return {"status": "error", "message": "path required"}

    @app.get("/health")
    async def health():
        return {"status": "ok", "agent": "Claw", "version": "2.0.0"}

    # ----- Mount LINE / Telegram webhooks -----
    try:
        from interfaces.line_bot import create_line_router
        app.include_router(create_line_router(), prefix="/line", tags=["LINE Bot"])
    except Exception as e:
        print(f"[WARN] LINE Bot not loaded: {e}")

    try:
        from interfaces.telegram_bot import create_telegram_router
        app.include_router(create_telegram_router(), prefix="/telegram", tags=["Telegram Bot"])
    except Exception as e:
        print(f"[WARN] Telegram Bot not loaded: {e}")

    # ----- Mount Gradio UI -----
    try:
        import gradio as gr
        from interfaces.gradio_ui import build_gradio_app
        gradio_app = build_gradio_app()
        app = gr.mount_gradio_app(app, gradio_app, path="/chat")
    except Exception as e:
        print(f"[WARN] Gradio UI not loaded: {e}")

    return app
