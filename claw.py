#!/usr/bin/env python3
"""
Claw — 三 AI CLI 切換器 (Claude / Gemini / Codex)

Usage:
  claw                     啟動互動式 REPL
  claw /gld 你好           單次指令模式
  claw --web               啟動 Web UI（FastAPI + Gradio）
  claw --version

進入 REPL 後支援的 slash 指令：
  /cld <prompt>            呼叫 Claude Code
  /gld <prompt>            呼叫 Gemini CLI
  /cod <prompt>            呼叫 Codex CLI
  /cod:review              Codex 程式碼審查
  /cod:rescue              委派任務給 Codex
  /<engine>:status         查看背景任務
  /<engine>:result         取得任務結果
  /<engine>:cancel         取消背景任務
  /help                    顯示說明
  /quit                    離開
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Prompt

from src.core.cli_router import (
    parse_slash,
    dispatch,
    is_cli_installed,
    install_hint,
    JobResult,
    CLI_BINARIES,
    DEFAULT_MODELS,
)


__version__ = "2.0.0"
# 強制 truecolor：cmd.exe 預設只支援 16 色，會把 RGB 降級成淺色
# force_terminal=True 確保即使 stdout 重導向也保留色彩
console = Console(color_system="truecolor", force_terminal=True, legacy_windows=False)


# ---------- Banner ----------

def render_banner() -> None:
    title = Text("🦞 Claw", style="bold #b71c1c")
    sub = Text(" — 三 AI CLI 切換器 ", style="bold #1a1a1a")
    ver = Text(f"v{__version__}", style="bold #e65100")
    author = Text("    by 阿亮老師（曾慶良）· 新興科技推廣中心", style="bold #4a148c")
    header = Text.assemble(title, sub, ver, author)
    console.print(Panel(header, border_style="#b71c1c", padding=(0, 2)))


def render_architecture() -> None:
    """啟動畫面顯示三 AI 架構樹狀圖。"""
    # 用「明確顏色」取代 dim，避免在亮色終端看不見
    # ── 深飽和色盤（亮/暗終端皆清晰）──
    C_CLD    = "bold #0d47a1"   # Claude 深藍
    C_GLD    = "bold #1b5e20"   # Gemini 深綠
    C_COD    = "bold #b71c1c"   # Codex 深紅
    C_NEW    = "bold #6a1b9a"   # 「新增」深紫
    C_PLUGIN = "bold #ad1457"   # Claw plugin 玫瑰紅
    main_text = "bold #1a1a1a"      # 主文字接近黑
    tree_color = "bold #1565c0"     # 樹狀符號深藍
    arch = Text()
    arch.append("Claude Code", style=C_CLD)
    arch.append("（主環境，永遠的起點）\n", style=main_text)
    arch.append("       ↓ 安裝 ", style=main_text)
    arch.append("Claw plugin", style=C_PLUGIN)
    arch.append("\n")
    arch.append("       ├─ ", style=tree_color)
    arch.append("/cld", style=C_CLD)
    arch.append(" <prompt>   → 直接用 Claude 處理（其實就是 Claude Code 自己）\n", style=main_text)
    arch.append("       ├─ ", style=tree_color)
    arch.append("/gld", style=C_GLD)
    arch.append(" <prompt>   → 把任務丟給 ", style=main_text)
    arch.append("Gemini CLI", style=C_GLD)
    arch.append("，回報結果\n", style=main_text)
    arch.append("       ├─ ", style=tree_color)
    arch.append("/cod", style=C_COD)
    arch.append(" <prompt>   → 把任務丟給 ", style=main_text)
    arch.append("Codex CLI", style=C_COD)
    arch.append("，回報結果\n", style=main_text)
    arch.append("       │\n", style=tree_color)
    arch.append("       └─ ", style=tree_color)
    arch.append("/cod:review", style=C_COD)
    arch.append("     → Codex 審查（仿 codex-plugin-cc）\n", style=main_text)
    arch.append("          ", style=tree_color)
    arch.append("/cod:rescue", style=C_COD)
    arch.append("     → Codex 委派\n", style=main_text)
    arch.append("          ", style=tree_color)
    arch.append("/gld:review", style=C_GLD)
    arch.append("     → Gemini 審查（", style=main_text)
    arch.append("新增", style=C_NEW)
    arch.append("）\n", style=main_text)
    arch.append("          ", style=tree_color)
    arch.append("/gld:rescue", style=C_GLD)
    arch.append("     → Gemini 委派（", style=main_text)
    arch.append("新增", style=C_NEW)
    arch.append("）", style=main_text)

    console.print(Panel(arch, title="[bold #4a148c]Claw 架構[/bold #4a148c]",
                        border_style="#4a148c", padding=(1, 2)))


def render_command_panel() -> None:
    table = Table(show_header=True, header_style="bold #4a148c", box=None, padding=(0, 2))
    table.add_column("指令", style="bold #0d47a1", no_wrap=True)
    table.add_column("引擎", style="bold #1b5e20")
    table.add_column("說明", style="bold #1a1a1a")

    table.add_row("/cld <prompt>", "Claude Code", "Anthropic（預設 sonnet-4-6 / --pro opus-4-7）")
    table.add_row("/gld <prompt>", "Gemini CLI", "Google（預設 3-flash / --pro 3.1-pro）")
    table.add_row("/cod <prompt>", "Codex CLI", "OpenAI（預設 gpt-5.4 / --pro gpt-5.4-pro）")

    console.print(Panel(table, title="[bold #1b5e20]三 AI 切換指令[/bold #1b5e20]",
                        border_style="#1b5e20"))

    advanced = Table(show_header=True, header_style="bold #4a148c", box=None, padding=(0, 2))
    advanced.add_column("指令", style="bold #0d47a1", no_wrap=True)
    advanced.add_column("說明", style="bold #1a1a1a")

    advanced.add_row("/use cld|gld|cod", "切換主引擎（之後直接打字就送主引擎）")
    advanced.add_row("/cod:review [--base main]", "Codex 程式碼審查（可加 --background）")
    advanced.add_row("/cod:adversarial-review", "對抗式審查，挑戰設計決策")
    advanced.add_row("/cod:rescue <task>", "委派任務給 Codex 修 bug、追問題")
    advanced.add_row("/gld:review [--base main]", "Gemini 程式碼審查（1M context 看全專案）")
    advanced.add_row("/gld:rescue <task>", "委派任務給 Gemini")
    advanced.add_row("/<eng>:status [job_id]", "查看背景任務進度（eng = cld/gld/cod）")
    advanced.add_row("/<eng>:result [job_id]", "取得已完成任務結果")
    advanced.add_row("/<eng>:cancel [job_id]", "取消背景任務")
    advanced.add_row("/help", "完整指令說明")
    advanced.add_row("/skills", "列出可用技能（80+）")
    advanced.add_row("/web", "在瀏覽器開啟 Gradio UI")
    advanced.add_row("/quit  或  /exit", "離開 Claw")

    console.print(Panel(advanced, title="[bold #e65100]進階指令[/bold #e65100]",
                        border_style="#e65100"))


def render_health() -> None:
    """Show which engine CLIs are installed."""
    table = Table(show_header=True, header_style="bold #4a148c", box=None, padding=(0, 2))
    table.add_column("引擎", style="bold #0d47a1")
    table.add_column("狀態", style="bold #1a1a1a")
    table.add_column("安裝指令", style="bold #b71c1c")

    for eng, binary in CLI_BINARIES.items():
        installed = is_cli_installed(eng)
        if installed:
            table.add_row(f"{eng} ({binary})", "[bold #1b5e20]✓ 已安裝[/bold #1b5e20]", "—")
        else:
            table.add_row(f"{eng} ({binary})", "[bold #b71c1c]✗ 未安裝[/bold #b71c1c]", install_hint(eng))

    console.print(Panel(table, title="[bold #0d47a1]CLI 安裝檢查[/bold #0d47a1]",
                        border_style="#0d47a1"))


# ---------- Output formatting ----------

def render_job(job: JobResult) -> None:
    icon = {"completed": "✓", "running": "⟳", "failed": "✗", "cancelled": "⊘"}.get(
        job.status, "?"
    )
    color = {"completed": "green", "running": "yellow", "failed": "red", "cancelled": "dim"}.get(
        job.status, "white"
    )
    title = f"[{color}]{icon} {job.engine.upper()} job {job.job_id}[/{color}] — {job.status}"

    body_parts: list[str] = []
    if job.stdout:
        body_parts.append(job.stdout.strip())
    if job.stderr and job.status != "completed":
        body_parts.append(f"[bold #b71c1c]stderr:[/bold #b71c1c]\n{job.stderr.strip()}")
    if not body_parts:
        body_parts.append("[bold #1a1a1a](no output yet)[/bold #1a1a1a]")

    console.print(Panel("\n\n".join(body_parts), title=title, border_style=color))


def render_jobs(jobs: list[JobResult]) -> None:
    if not jobs:
        console.print("[bold #1a1a1a]沒有任務紀錄[/bold #1a1a1a]")
        return
    table = Table(show_header=True, header_style="bold magenta", padding=(0, 1))
    table.add_column("Job ID", style="cyan")
    table.add_column("Engine")
    table.add_column("Status")
    table.add_column("Prompt", overflow="ellipsis", max_width=50)
    for j in jobs:
        if not j:
            continue
        table.add_row(j.job_id, j.engine, j.status, (j.prompt or "")[:60])
    console.print(table)


# ---------- REPL ----------

DEFAULT_ENGINE = "cld"  # 啟動預設主引擎


def _engine_color(engine: str) -> str:
    """主引擎對應深飽和色（用於說明文字、訊息）。"""
    return {
        "cld": "#0d47a1",   # Claude 深藍
        "gld": "#1b5e20",   # Gemini 深綠
        "cod": "#b71c1c",   # Codex 深紅
    }.get(engine, "#1a1a1a")


def _engine_prompt_style(engine: str) -> str:
    """REPL prompt 用「黑字 + 亮飽和底」最大對比，cmd.exe 也清楚。"""
    bg = {
        "cld": "#64b5f6",   # 亮藍底
        "gld": "#81c784",   # 亮綠底
        "cod": "#ffb74d",   # 亮橘底
    }.get(engine, "#e0e0e0")
    return f"bold #000000 on {bg}"


def repl() -> None:
    render_banner()
    render_architecture()
    render_command_panel()
    render_health()

    current_engine = DEFAULT_ENGINE
    console.print(
        f"[bold #1a1a1a]目前主引擎：[bold {_engine_color(current_engine)}]{current_engine.upper()}"
        f"[/bold {_engine_color(current_engine)}][/bold #1a1a1a] [bold #1a1a1a]—[/bold #1a1a1a] "
        f"[bold #1a1a1a]直接輸入文字會送到主引擎，用[/bold #1a1a1a] "
        f"[bold #e65100]/use cld|gld|cod[/bold #e65100] "
        f"[bold #1a1a1a]切換，或用[/bold #1a1a1a] "
        f"[bold #e65100]/cld /gld /cod[/bold #e65100] "
        f"[bold #1a1a1a]一次性指定。[/bold #1a1a1a]\n"
    )

    while True:
        # prompt: 黑字 + 亮飽和底（cmd.exe 也能清楚渲染）+ 自控冒號顏色
        style = _engine_prompt_style(current_engine)
        prompt_label = f"[{style}] claw·{current_engine} [/{style}][bold #e65100] ▸ [/bold #e65100]"
        try:
            console.print(prompt_label, end="")
            line = input().strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold #1a1a1a]再見！[/bold #1a1a1a]")
            return

        if not line:
            continue

        if line in ("/quit", "/exit", ":q", "exit", "quit"):
            console.print("[bold #1a1a1a]再見！[/bold #1a1a1a]")
            return

        if line == "/help":
            render_command_panel()
            continue

        if line == "/health":
            render_health()
            continue

        if line == "/skills":
            _show_skills()
            continue

        if line == "/web":
            _launch_web()
            continue

        # /use cld|gld|cod — 切換主引擎
        if line.startswith("/use"):
            parts = line.split(maxsplit=1)
            if len(parts) < 2 or parts[1].strip() not in ("cld", "gld", "cod"):
                console.print(
                    "[bold #e65100]用法：/use cld | /use gld | /use cod[/bold #e65100]"
                )
                continue
            current_engine = parts[1].strip()
            console.print(
                f"[bold #1b5e20]✓ 主引擎已切換為[/bold #1b5e20] "
                f"[bold {_engine_color(current_engine)}]{current_engine.upper()}[/bold {_engine_color(current_engine)}]"
            )
            continue

        # 不帶 / 的純文字 → 自動加上目前主引擎前綴
        if not line.startswith("/"):
            line = f"/{current_engine} {line}"

        parsed = parse_slash(line)
        if parsed is None:
            console.print(f"[bold #b71c1c]無法解析指令：{line}[/bold #b71c1c]")
            console.print("[bold #1a1a1a]輸入 /help 查看支援的指令[/bold #1a1a1a]")
            continue

        with console.status(f"[bold #0d47a1]{parsed.engine.upper()} 處理中…[/bold #0d47a1]", spinner="dots"):
            result = dispatch(parsed)

        if isinstance(result, JobResult):
            render_job(result)
        elif isinstance(result, list):
            render_jobs(result)
        elif isinstance(result, dict):
            console.print(result)


def _show_skills() -> None:
    skills_dir = ROOT / "skills" / "bundled"
    if not skills_dir.exists():
        console.print("[bold #e65100]找不到 skills/bundled 目錄[/bold #e65100]")
        return
    skills = sorted([p.name for p in skills_dir.iterdir() if p.is_dir()])
    table = Table(title=f"可用技能 ({len(skills)})", show_header=False, padding=(0, 2))
    table.add_column("Skill", style="cyan")
    for chunk in [skills[i : i + 3] for i in range(0, len(skills), 3)]:
        while len(chunk) < 3:
            chunk.append("")
        table.add_row(*chunk)
    console.print(table)


def _launch_web() -> None:
    console.print("[bold #0d47a1]啟動 Web UI… (http://localhost:8000/chat)[/bold #0d47a1]")
    import subprocess
    subprocess.Popen([sys.executable, str(ROOT / "run.py")])


# ---------- One-shot mode ----------

def one_shot(args: list[str]) -> int:
    line = " ".join(args)
    parsed = parse_slash(line)
    if parsed is None:
        console.print(f"[bold #b71c1c]無法解析指令：{line}[/bold #b71c1c]")
        return 2
    result = dispatch(parsed)
    if isinstance(result, JobResult):
        render_job(result)
        return 0 if result.status == "completed" else 1
    if isinstance(result, list):
        render_jobs(result)
        return 0
    if isinstance(result, dict):
        console.print(result)
        return 0
    return 0


# ---------- Entry ----------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="claw",
        description="Claw — 三 AI CLI 切換器（Claude / Gemini / Codex）",
        add_help=False,
    )
    parser.add_argument("--version", action="store_true", help="顯示版本")
    parser.add_argument("--web", action="store_true", help="啟動 Web UI（FastAPI + Gradio）")
    parser.add_argument("--help", "-h", action="store_true", help="顯示說明")
    parser.add_argument("rest", nargs=argparse.REMAINDER, help="一次性指令")
    args = parser.parse_args()

    if args.version:
        console.print(f"Claw v{__version__}")
        return 0

    if args.help:
        render_banner()
        render_architecture()
        render_command_panel()
        return 0

    if args.web:
        import subprocess
        return subprocess.call([sys.executable, str(ROOT / "run.py")])

    if args.rest:
        return one_shot(args.rest)

    repl()
    return 0


if __name__ == "__main__":
    sys.exit(main())
