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
console = Console()


# ---------- Banner ----------

def render_banner() -> None:
    title = Text("🦞 Claw", style="bold cyan")
    sub = Text(" — 三 AI CLI 切換器 ", style="dim")
    ver = Text(f"v{__version__}", style="bold yellow")
    header = Text.assemble(title, sub, ver)
    console.print(Panel(header, border_style="cyan", padding=(0, 2)))


def render_architecture() -> None:
    """啟動畫面顯示三 AI 架構樹狀圖。"""
    # 用「明確顏色」取代 dim，避免在亮色終端看不見
    main_text = "bold default"      # 主文字：終端預設色 + 粗體（亮/暗主題都對比強）
    tree_color = "bright_blue"      # 樹狀符號用亮藍，亮/暗主題都看得到
    arch = Text()
    arch.append("Claude Code", style="bold cyan")
    arch.append("（主環境，永遠的起點）\n", style=main_text)
    arch.append("       ↓ 安裝 ", style=main_text)
    arch.append("Claw plugin", style="bold magenta")
    arch.append("\n")
    arch.append("       ├─ ", style=tree_color)
    arch.append("/cld", style="bold cyan")
    arch.append(" <prompt>   → 直接用 Claude 處理（其實就是 Claude Code 自己）\n", style=main_text)
    arch.append("       ├─ ", style=tree_color)
    arch.append("/gld", style="bold green")
    arch.append(" <prompt>   → 把任務丟給 ", style=main_text)
    arch.append("Gemini CLI", style="bold green")
    arch.append("，回報結果\n", style=main_text)
    arch.append("       ├─ ", style=tree_color)
    arch.append("/cod", style="bold yellow")
    arch.append(" <prompt>   → 把任務丟給 ", style=main_text)
    arch.append("Codex CLI", style="bold yellow")
    arch.append("，回報結果\n", style=main_text)
    arch.append("       │\n", style=tree_color)
    arch.append("       └─ ", style=tree_color)
    arch.append("/cod:review", style="bold yellow")
    arch.append("     → Codex 審查（仿 codex-plugin-cc）\n", style=main_text)
    arch.append("          ", style=tree_color)
    arch.append("/cod:rescue", style="bold yellow")
    arch.append("     → Codex 委派\n", style=main_text)
    arch.append("          ", style=tree_color)
    arch.append("/gld:review", style="bold green")
    arch.append("     → Gemini 審查（", style=main_text)
    arch.append("新增", style="bold magenta")
    arch.append("）\n", style=main_text)
    arch.append("          ", style=tree_color)
    arch.append("/gld:rescue", style="bold green")
    arch.append("     → Gemini 委派（", style=main_text)
    arch.append("新增", style="bold magenta")
    arch.append("）", style=main_text)

    console.print(Panel(arch, title="[bold]Claw 架構[/bold]", border_style="magenta", padding=(1, 2)))


def render_command_panel() -> None:
    table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
    table.add_column("指令", style="bold cyan", no_wrap=True)
    table.add_column("引擎", style="bold green")
    table.add_column("說明", style="bold default")

    table.add_row("/cld <prompt>", "Claude Code", "Anthropic（預設 sonnet-4-6 / --pro opus-4-7）")
    table.add_row("/gld <prompt>", "Gemini CLI", "Google（預設 3-flash / --pro 3.1-pro）")
    table.add_row("/cod <prompt>", "Codex CLI", "OpenAI（預設 gpt-5.4 / --pro gpt-5.4-pro）")

    console.print(Panel(table, title="[bold]三 AI 切換指令[/bold]", border_style="green"))

    advanced = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
    advanced.add_column("指令", style="bold cyan", no_wrap=True)
    advanced.add_column("說明", style="bold default")

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

    console.print(Panel(advanced, title="[bold]進階指令[/bold]", border_style="yellow"))


def render_health() -> None:
    """Show which engine CLIs are installed."""
    table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
    table.add_column("引擎", style="bold cyan")
    table.add_column("狀態", style="bold default")
    table.add_column("安裝指令", style="bold yellow")

    for eng, binary in CLI_BINARIES.items():
        installed = is_cli_installed(eng)
        if installed:
            table.add_row(f"{eng} ({binary})", "[green]✓ 已安裝[/green]", "—")
        else:
            table.add_row(f"{eng} ({binary})", "[red]✗ 未安裝[/red]", install_hint(eng))

    console.print(Panel(table, title="[bold]CLI 安裝檢查[/bold]", border_style="blue"))


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
        body_parts.append(f"[red]stderr:[/red]\n{job.stderr.strip()}")
    if not body_parts:
        body_parts.append("[dim](no output yet)[/dim]")

    console.print(Panel("\n\n".join(body_parts), title=title, border_style=color))


def render_jobs(jobs: list[JobResult]) -> None:
    if not jobs:
        console.print("[dim]沒有任務紀錄[/dim]")
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
    return {"cld": "cyan", "gld": "green", "cod": "yellow"}.get(engine, "white")


def repl() -> None:
    render_banner()
    render_architecture()
    render_command_panel()
    render_health()

    current_engine = DEFAULT_ENGINE
    console.print(
        f"[bold default]目前主引擎：[bold {_engine_color(current_engine)}]{current_engine.upper()}[/bold {_engine_color(current_engine)}][/bold default] — "
        f"[bold default]直接輸入文字會送到主引擎，用[/bold default] [bold yellow]/use cld|gld|cod[/bold yellow] [bold default]切換，"
        f"或用[/bold default] [bold yellow]/cld /gld /cod[/bold yellow] [bold default]一次性指定。[/bold default]\n"
    )

    while True:
        prompt_label = f"[bold {_engine_color(current_engine)}]claw·{current_engine}[/bold {_engine_color(current_engine)}]"
        try:
            line = Prompt.ask(prompt_label).strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]再見！[/dim]")
            return

        if not line:
            continue

        if line in ("/quit", "/exit", ":q", "exit", "quit"):
            console.print("[dim]再見！[/dim]")
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
                    "[yellow]用法：/use cld | /use gld | /use cod[/yellow]"
                )
                continue
            current_engine = parts[1].strip()
            console.print(
                f"[green]✓ 主引擎已切換為 [bold {_engine_color(current_engine)}]{current_engine.upper()}[/bold {_engine_color(current_engine)}][/green]"
            )
            continue

        # 不帶 / 的純文字 → 自動加上目前主引擎前綴
        if not line.startswith("/"):
            line = f"/{current_engine} {line}"

        parsed = parse_slash(line)
        if parsed is None:
            console.print(f"[red]無法解析指令：{line}[/red]")
            console.print("[dim]輸入 /help 查看支援的指令[/dim]")
            continue

        with console.status(f"[cyan]{parsed.engine.upper()} 處理中…[/cyan]", spinner="dots"):
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
        console.print("[yellow]找不到 skills/bundled 目錄[/yellow]")
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
    console.print("[cyan]啟動 Web UI… (http://localhost:8000/chat)[/cyan]")
    import subprocess
    subprocess.Popen([sys.executable, str(ROOT / "run.py")])


# ---------- One-shot mode ----------

def one_shot(args: list[str]) -> int:
    line = " ".join(args)
    parsed = parse_slash(line)
    if parsed is None:
        console.print(f"[red]無法解析指令：{line}[/red]")
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
