"""Gradio Chat UI for Claw — 三 AI CLI 切換器（Claude / Gemini / Codex）。"""
from __future__ import annotations

import sys
from pathlib import Path

import gradio as gr

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.cli_router import (
    parse_slash,
    dispatch,
    JobResult,
    is_cli_installed,
    install_hint,
    CLI_BINARIES,
)


# ---------- Static markdown blocks ----------

ARCHITECTURE_MD = """
### 🦞 Claw 架構

```
Claude Code（主環境，永遠的起點）
       ↓ 安裝 Claw plugin
       ├─ /cld <prompt>   → 直接用 Claude 處理（其實就是 Claude Code 自己）
       ├─ /gld <prompt>   → 把任務丟給 Gemini CLI，回報結果
       ├─ /cod <prompt>   → 把任務丟給 Codex CLI，回報結果
       │
       └─ /cod:review     → Codex 審查（仿 codex-plugin-cc）
          /cod:rescue     → Codex 委派
          /gld:review     → Gemini 審查（新增）
          /gld:rescue     → Gemini 委派（新增）
```
"""

COMMANDS_MD = """
### 三 AI 切換指令

| 指令 | 引擎 | 說明 |
|------|------|------|
| `/cld <prompt>` | **Claude Code** | Anthropic（預設 sonnet-4-6 / `--pro` opus-4-7） |
| `/gld <prompt>` | **Gemini CLI** | Google（預設 3-flash / `--pro` 3.1-pro） |
| `/cod <prompt>` | **Codex CLI** | OpenAI（預設 gpt-5.4 / `--pro` gpt-5.4-pro） |

### 進階指令

| 指令 | 說明 |
|------|------|
| `/cod:review [--base main]` | Codex 程式碼審查（可加 `--background`） |
| `/cod:adversarial-review` | 對抗式審查，挑戰設計決策 |
| `/cod:rescue <task>` | 委派任務給 Codex 修 bug |
| `/gld:review [--base main]` | Gemini 審查（1M context 看全專案） |
| `/gld:rescue <task>` | 委派任務給 Gemini |
| `/<eng>:status [job_id]` | 查看背景任務進度 |
| `/<eng>:result [job_id]` | 取得已完成任務結果 |
| `/<eng>:cancel [job_id]` | 取消背景任務 |
"""


def _format_job(job: JobResult) -> str:
    icon = {"completed": "✅", "running": "⟳", "failed": "❌", "cancelled": "⊘"}.get(
        job.status, "?"
    )
    parts = [f"{icon} **{job.engine.upper()}** job `{job.job_id}` — {job.status}"]
    if job.stdout:
        parts.append(f"\n```\n{job.stdout.strip()}\n```")
    if job.stderr and job.status != "completed":
        parts.append(f"\n**stderr:**\n```\n{job.stderr.strip()}\n```")
    return "\n".join(parts)


def _format_jobs(jobs: list[JobResult]) -> str:
    if not jobs:
        return "_沒有任務紀錄_"
    rows = ["| Job ID | Engine | Status | Prompt |", "|---|---|---|---|"]
    for j in jobs:
        if not j:
            continue
        rows.append(f"| `{j.job_id}` | {j.engine} | {j.status} | {(j.prompt or '')[:60]} |")
    return "\n".join(rows)


def _check_engines_md() -> str:
    rows = ["### CLI 安裝檢查\n", "| 引擎 | 狀態 | 安裝指令 |", "|---|---|---|"]
    for eng, binary in CLI_BINARIES.items():
        installed = is_cli_installed(eng)
        if installed:
            rows.append(f"| `{eng}` ({binary}) | ✅ 已安裝 | — |")
        else:
            rows.append(f"| `{eng}` ({binary}) | ❌ 未安裝 | `{install_hint(eng)}` |")
    return "\n".join(rows)


def build_gradio_app() -> gr.Blocks:
    with gr.Blocks(title="Claw — 三 AI CLI 切換器") as demo:

        gr.Markdown(
            "# 🦞 Claw — 三 AI CLI 切換器\n"
            "Claude · Gemini · Codex 一鍵切換 | Slash 指令路由 | Tool Use | 80+ 教育技能"
        )

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="對話區（支援 /cld /gld /cod 指令）",
                    height=520,
                    show_copy_button=True,
                    type="messages",
                )
                with gr.Row():
                    msg_input = gr.Textbox(
                        label="輸入訊息",
                        placeholder="例：/gld --pro 看一下整個專案有什麼問題  或  /cod:review --background",
                        scale=4,
                        lines=2,
                    )
                    send_btn = gr.Button("送出", variant="primary", scale=1)

                with gr.Accordion("🦞 Claw 架構", open=True):
                    gr.Markdown(ARCHITECTURE_MD)

                with gr.Accordion("📖 完整指令說明", open=False):
                    gr.Markdown(COMMANDS_MD)

                with gr.Accordion("🩺 引擎安裝檢查", open=False):
                    health_md = gr.Markdown(_check_engines_md())
                    refresh_btn = gr.Button("重新檢查", size="sm")
                    refresh_btn.click(fn=lambda: _check_engines_md(), outputs=health_md)

            with gr.Column(scale=1):
                model_dd = gr.Dropdown(
                    choices=[
                        "auto (跟著 slash 指令)",
                        "claude-sonnet-4-6",
                        "claude-opus-4-7",
                        "gemini-3-flash-preview",
                        "gemini-3.1-pro-preview",
                        "gpt-5.4",
                        "gpt-5.4-pro",
                        "llama-3.3-70b-versatile",
                    ],
                    value="auto (跟著 slash 指令)",
                    label="預設模型（純 prompt 走 API 模式時用）",
                )
                workdir_input = gr.Textbox(
                    label="工作目錄",
                    placeholder="例：D:/projects/my-app",
                    value="",
                )
                gr.Markdown("### 範例指令")
                gr.Markdown(
                    "- `/cld 寫個 Python 排序`\n"
                    "- `/gld --pro 看一下整個專案`\n"
                    "- `/cod:review --base main`\n"
                    "- `/cod:rescue 修 CI 失敗`\n"
                    "- `/gld:review` （新增）\n"
                    "- `/cod:status` 看背景任務\n"
                    "- 一般訊息（不帶 /）走 API 模式\n"
                )
                status_md = gr.Markdown("### 狀態\n等待輸入...")

        # ---- Event handlers ----

        async def respond(message: str, history: list, model_name: str, workdir: str):
            if not message.strip():
                return "", history, "### 狀態\n請輸入訊息"

            history = history or []
            history.append({"role": "user", "content": message})

            # ---- Slash 指令模式：走 cli_router ----
            if message.strip().startswith("/"):
                parsed = parse_slash(message.strip())
                if parsed is None:
                    history.append({
                        "role": "assistant",
                        "content": f"❌ 無法解析指令：`{message}`\n\n輸入展開「📖 完整指令說明」查看支援的指令。",
                    })
                    return "", history, "### 狀態\n指令解析失敗"

                status = f"### 狀態\n引擎: {parsed.engine.upper()}\n處理中..."
                try:
                    result = dispatch(parsed)
                    if isinstance(result, JobResult):
                        content = _format_job(result)
                        engine_status = result.status
                    elif isinstance(result, list):
                        content = _format_jobs(result)
                        engine_status = "ok"
                    elif isinstance(result, dict):
                        content = f"```json\n{result}\n```"
                        engine_status = "ok"
                    else:
                        content = str(result)
                        engine_status = "ok"

                    history.append({"role": "assistant", "content": content})
                    status = (
                        f"### 狀態\n引擎: {parsed.engine.upper()}\n"
                        f"子指令: {parsed.subcommand or '—'}\n結果: {engine_status}"
                    )
                except Exception as e:
                    history.append({"role": "assistant", "content": f"❌ 執行錯誤：{e}"})
                    status = f"### 狀態\n錯誤: {e}"

                return "", history, status

            # ---- 非 slash：走原本的 /api/chat ----
            import httpx
            status = f"### 狀態\n模型: {model_name}\n處理中..."
            actual_model = None if model_name.startswith("auto") else model_name

            try:
                if workdir.strip():
                    async with httpx.AsyncClient(timeout=5) as client:
                        await client.post(
                            "http://localhost:8000/api/set-workdir",
                            json={"path": workdir.strip()},
                        )

                async with httpx.AsyncClient(timeout=180) as client:
                    r = await client.post(
                        "http://localhost:8000/api/chat",
                        json={
                            "message": message,
                            "model": actual_model,
                            "user_id": "gradio_user",
                        },
                    )
                    r.raise_for_status()
                    data = r.json()

                content = data["content"]
                tool_uses = data.get("tool_uses", [])
                if tool_uses:
                    tool_info = "\n\n---\n**工具使用記錄：**\n"
                    for tu in tool_uses:
                        icon = "❌" if tu.get("is_error") else "✅"
                        tool_info += f"- {icon} `{tu['tool']}` {tu.get('args_brief', '')[:60]}\n"
                    content += tool_info

                history.append({"role": "assistant", "content": content})
                usage = data.get("usage", {})
                skill = data.get("skill_used", "無")
                status = (
                    f"### 狀態\n"
                    f"模型: {data['model_used']}\n"
                    f"技能: {skill}\n"
                    f"工具呼叫: {len(tool_uses)} 次\n"
                    f"Token: {usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out"
                )
            except Exception as e:
                history.append({"role": "assistant", "content": f"錯誤：{e}"})
                status = f"### 狀態\n錯誤: {e}"

            return "", history, status

        send_btn.click(
            fn=respond,
            inputs=[msg_input, chatbot, model_dd, workdir_input],
            outputs=[msg_input, chatbot, status_md],
        )
        msg_input.submit(
            fn=respond,
            inputs=[msg_input, chatbot, model_dd, workdir_input],
            outputs=[msg_input, chatbot, status_md],
        )

    return demo
