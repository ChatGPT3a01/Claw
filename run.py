#!/usr/bin/env python3
"""
Claw — Web UI 一鍵啟動腳本（FastAPI + Gradio）
Usage: python run.py [--port 8000] [--host 0.0.0.0]

提示：terminal 體驗請改用 `claw` 指令（claw.bat / claw.py）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def check_deps():
    """Quick dependency check."""
    missing = []
    for pkg in ["fastapi", "uvicorn", "gradio", "httpx", "yaml", "dotenv"]:
        mod = pkg.replace("-", "_")
        if mod == "yaml":
            mod = "yaml"
        if mod == "dotenv":
            mod = "dotenv"
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[ERROR] Missing packages: {', '.join(missing)}")
        print(f"  Run: pip install -r requirements.txt")
        sys.exit(1)


def check_env():
    """Check if at least one API key is configured."""
    from dotenv import load_dotenv
    import os
    load_dotenv(ROOT / ".env")
    keys = ["GEMINI_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY"]
    has_any = any(os.getenv(k) for k in keys)
    if not has_any:
        print("[WARN] No API keys found in .env!")
        print("  Copy .env.example to .env and fill in at least one API key.")
        print("  Starting anyway (API calls will fail)...\n")


def main():
    parser = argparse.ArgumentParser(description="Claw — 三 AI CLI 切換器（Claude / Gemini / Codex）")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    check_deps()
    check_env()

    print(r"""
    ╔════════════════════════════════════════════════╗
    ║  🦞 Claw v2.0.0  — 三 AI CLI 切換器            ║
    ║  Claude · Gemini · Codex                       ║
    ║                                                ║
    ║  Chat UI:   http://localhost:{port}/chat        ║
    ║  API Docs:  http://localhost:{port}/docs        ║
    ║  Health:    http://localhost:{port}/health      ║
    ║                                                ║
    ║  Slash 指令範例：                              ║
    ║    /cld <prompt>      呼叫 Claude Code         ║
    ║    /gld <prompt>      呼叫 Gemini CLI          ║
    ║    /cod <prompt>      呼叫 Codex CLI           ║
    ║    /cod:review        Codex 程式碼審查         ║
    ║    /gld:review        Gemini 程式碼審查        ║
    ║                                                ║
    ║  Terminal REPL：直接打 `claw` 進入互動模式     ║
    ╚════════════════════════════════════════════════╝
    """.replace("{port}", str(args.port)))

    import uvicorn
    uvicorn.run(
        "interfaces.app:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
