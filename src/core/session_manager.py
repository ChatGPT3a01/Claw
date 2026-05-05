"""Conversation session manager."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from ..utils.config import get_config


@dataclass
class Session:
    session_id: str
    user_id: str
    messages: list[dict] = field(default_factory=list)
    model: str = "gemini-3-flash"
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def recent(self, n: int = 20) -> list[dict]:
        """Return last n messages for context window."""
        return self.messages[-n:]

    def compact(self, keep: int = 10):
        """Keep only last N messages to save context."""
        if len(self.messages) > keep:
            self.messages = self.messages[-keep:]


class SessionManager:
    """Manages per-user sessions with local JSON persistence."""

    def __init__(self):
        cfg = get_config()
        self._dir = Path(cfg.session_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Session] = {}

    def get_or_create(self, user_id: str, session_id: str = "") -> Session:
        key = session_id or user_id
        if key in self._cache:
            return self._cache[key]
        # Try load from disk
        path = self._dir / f"{key}.json"
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                session = Session(
                    session_id=data["session_id"],
                    user_id=data["user_id"],
                    messages=data.get("messages", []),
                    model=data.get("model", "gemini-3-flash"),
                    total_input_tokens=data.get("total_input_tokens", 0),
                    total_output_tokens=data.get("total_output_tokens", 0),
                )
                self._cache[key] = session
                return session
            except Exception:
                pass
        session = Session(session_id=session_id or uuid4().hex[:12], user_id=user_id)
        self._cache[key] = session
        return session

    def save(self, session: Session):
        key = session.session_id or session.user_id
        path = self._dir / f"{key}.json"
        path.write_text(json.dumps({
            "session_id": session.session_id,
            "user_id": session.user_id,
            "messages": session.messages[-50:],  # keep max 50
            "model": session.model,
            "total_input_tokens": session.total_input_tokens,
            "total_output_tokens": session.total_output_tokens,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
