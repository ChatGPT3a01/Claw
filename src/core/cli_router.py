"""
Claw CLI Router — 統一介面呼叫三家官方 AI CLI（Claude / Gemini / Codex）。

支援：
- /cld : Anthropic Claude Code CLI
- /gld : Google Gemini CLI
- /cod : OpenAI Codex CLI（含 review / rescue / status / result / cancel 進階子指令）

設計原則：
- subprocess 包裝官方二進位檔，不重新實作 LLM 邏輯
- 背景任務用 job_id 紀錄到 .claw/jobs/，可查詢狀態與結果
- 模型路由：根據旗標切換 flash/pro、mini/full
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# ---------- Paths ----------

ROOT = Path(__file__).resolve().parents[2]
JOBS_DIR = ROOT / ".claw" / "jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)


# ---------- Default model mapping ----------

DEFAULT_MODELS = {
    "cld": {"default": "claude-sonnet-4-6", "pro": "claude-opus-4-7"},
    "gld": {"default": "gemini-3-flash-preview", "pro": "gemini-3.1-pro-preview"},
    "cod": {"default": "gpt-5.4", "pro": "gpt-5.4-pro", "mini": "gpt-5.4-mini"},
}

CLI_BINARIES = {
    "cld": "claude",   # @anthropic-ai/claude-code
    "gld": "gemini",   # @google/gemini-cli
    "cod": "codex",    # @openai/codex
}


# ---------- Data ----------

@dataclass
class JobResult:
    job_id: str
    engine: str
    command: str
    prompt: str
    status: str  # running / completed / failed / cancelled
    started_at: float
    finished_at: Optional[float] = None
    return_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    session_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def save(self) -> None:
        path = JOBS_DIR / f"{self.job_id}.json"
        path.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, job_id: str) -> Optional["JobResult"]:
        path = JOBS_DIR / f"{job_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)


# ---------- Detection ----------

def is_cli_installed(engine: str) -> bool:
    """Check if the engine's official CLI is on PATH."""
    binary = CLI_BINARIES.get(engine)
    if not binary:
        return False
    return shutil.which(binary) is not None


def install_hint(engine: str) -> str:
    """Return install command if missing."""
    hints = {
        "cld": "npm install -g @anthropic-ai/claude-code",
        "gld": "npm install -g @google/gemini-cli",
        "cod": "npm install -g @openai/codex",
    }
    return hints.get(engine, "")


# ---------- Model resolution ----------

def resolve_model(engine: str, flags: dict) -> Optional[str]:
    """Pick model based on flags. Returns None if no override needed."""
    if flags.get("model"):
        return flags["model"]
    table = DEFAULT_MODELS.get(engine, {})
    if flags.get("pro"):
        return table.get("pro")
    if flags.get("mini"):
        return table.get("mini")
    return table.get("default")


# ---------- Foreground execution ----------

def run_foreground(engine: str, prompt: str, flags: dict) -> JobResult:
    """Run the engine CLI synchronously and return the result."""
    job = JobResult(
        job_id=_make_id(engine),
        engine=engine,
        command="run",
        prompt=prompt,
        status="running",
        started_at=time.time(),
    )

    if not is_cli_installed(engine):
        job.status = "failed"
        job.stderr = (
            f"Engine '{engine}' CLI not found. Install with:\n  {install_hint(engine)}"
        )
        job.finished_at = time.time()
        job.save()
        return job

    cmd = _build_cmd(engine, prompt, flags)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=flags.get("timeout", 600),
        )
        job.stdout = proc.stdout
        job.stderr = proc.stderr
        job.return_code = proc.returncode
        job.status = "completed" if proc.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        job.status = "failed"
        job.stderr = "Timeout exceeded."
    except FileNotFoundError as e:
        job.status = "failed"
        job.stderr = str(e)

    job.finished_at = time.time()
    job.save()
    return job


# ---------- Background execution ----------

def run_background(engine: str, prompt: str, flags: dict) -> JobResult:
    """Spawn the engine CLI as a background process and return immediately."""
    job = JobResult(
        job_id=_make_id(engine),
        engine=engine,
        command="run",
        prompt=prompt,
        status="running",
        started_at=time.time(),
    )

    if not is_cli_installed(engine):
        job.status = "failed"
        job.stderr = f"Engine '{engine}' CLI not found. Install: {install_hint(engine)}"
        job.finished_at = time.time()
        job.save()
        return job

    cmd = _build_cmd(engine, prompt, flags)
    out_path = JOBS_DIR / f"{job.job_id}.stdout"
    err_path = JOBS_DIR / f"{job.job_id}.stderr"

    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008  # DETACHED_PROCESS

    proc = subprocess.Popen(
        cmd,
        stdout=open(out_path, "w", encoding="utf-8"),
        stderr=open(err_path, "w", encoding="utf-8"),
        stdin=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    job.metadata["pid"] = proc.pid
    job.metadata["stdout_path"] = str(out_path)
    job.metadata["stderr_path"] = str(err_path)
    job.save()
    return job


# ---------- Job management ----------

def list_jobs(limit: int = 20) -> list[JobResult]:
    files = sorted(JOBS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [JobResult.load(f.stem) for f in files[:limit] if JobResult.load(f.stem)]


def get_job(job_id: str) -> Optional[JobResult]:
    return JobResult.load(job_id)


def refresh_job(job_id: str) -> Optional[JobResult]:
    """Refresh a background job: read live stdout/stderr files and check process."""
    job = JobResult.load(job_id)
    if job is None:
        return None
    if job.status != "running":
        return job

    pid = job.metadata.get("pid")
    if pid and not _pid_alive(pid):
        out = Path(job.metadata.get("stdout_path", ""))
        err = Path(job.metadata.get("stderr_path", ""))
        job.stdout = out.read_text(encoding="utf-8", errors="replace") if out.exists() else ""
        job.stderr = err.read_text(encoding="utf-8", errors="replace") if err.exists() else ""
        job.status = "completed"
        job.finished_at = time.time()
        job.save()
    return job


def cancel_job(job_id: str) -> bool:
    job = JobResult.load(job_id)
    if job is None or job.status != "running":
        return False
    pid = job.metadata.get("pid")
    if not pid:
        return False
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
        else:
            os.kill(pid, 15)
        job.status = "cancelled"
        job.finished_at = time.time()
        job.save()
        return True
    except Exception:
        return False


# ---------- Codex advanced subcommands ----------

def codex_review(base: Optional[str] = None, background: bool = False,
                 adversarial: bool = False, focus: str = "") -> JobResult:
    """Run /cod:review or /cod:adversarial-review."""
    flags = {"background": background}
    if base:
        flags["base"] = base
    cmd_label = "adversarial-review" if adversarial else "review"
    prompt_parts = [f"Run codex {cmd_label}"]
    if base:
        prompt_parts.append(f"against base={base}")
    if focus:
        prompt_parts.append(f"focus: {focus}")
    prompt = " ".join(prompt_parts)

    flags["subcommand"] = cmd_label
    flags["focus"] = focus
    if background:
        return run_background("cod", prompt, flags)
    return run_foreground("cod", prompt, flags)


def codex_rescue(prompt: str, background: bool = False, resume: bool = False,
                 fresh: bool = False, model: Optional[str] = None,
                 effort: Optional[str] = None) -> JobResult:
    flags = {
        "subcommand": "rescue",
        "background": background,
        "resume": resume,
        "fresh": fresh,
    }
    if model:
        flags["model"] = "gpt-5.3-codex-spark" if model == "spark" else model
    if effort:
        flags["effort"] = effort
    if background:
        return run_background("cod", prompt, flags)
    return run_foreground("cod", prompt, flags)


# ---------- Internal helpers ----------

def _make_id(engine: str) -> str:
    return f"{engine}-{uuid.uuid4().hex[:8]}"


def _pid_alive(pid: int) -> bool:
    if sys.platform == "win32":
        out = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True
        )
        return str(pid) in out.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _build_cmd(engine: str, prompt: str, flags: dict) -> list[str]:
    """Build the actual CLI command for each engine."""
    binary_name = CLI_BINARIES[engine]
    # Resolve to full path so Windows .CMD shims work via subprocess
    binary = shutil.which(binary_name) or binary_name
    model = resolve_model(engine, flags)

    if engine == "cld":
        cmd = [binary]
        if model:
            cmd += ["--model", model]
        cmd += ["-p", prompt]
        return cmd

    if engine == "gld":
        cmd = [binary]
        if model:
            cmd += ["--model", model]
        cmd += ["-p", prompt]
        return cmd

    if engine == "cod":
        sub = flags.get("subcommand")
        cmd = [binary]
        if sub == "review":
            cmd += ["review", "--skip-git-repo-check"]
            if flags.get("base"):
                cmd += ["--base", flags["base"]]
        elif sub == "adversarial-review":
            cmd += ["adversarial-review", "--skip-git-repo-check"]
            if flags.get("base"):
                cmd += ["--base", flags["base"]]
            if flags.get("focus"):
                cmd += [flags["focus"]]
        elif sub == "rescue":
            cmd += ["rescue", "--skip-git-repo-check"]
            if flags.get("resume"):
                cmd += ["--resume"]
            if flags.get("fresh"):
                cmd += ["--fresh"]
            if flags.get("effort"):
                cmd += ["--effort", flags["effort"]]
            cmd += [prompt]
        else:
            cmd += ["exec", "--skip-git-repo-check"]
            if model:
                cmd += ["--model", model]
            cmd += [prompt]
        return cmd

    raise ValueError(f"Unknown engine: {engine}")


# ---------- Slash command parser ----------

@dataclass
class ParsedCommand:
    engine: str               # cld / gld / cod
    subcommand: Optional[str] # None / review / rescue / status / result / cancel / adversarial-review
    prompt: str
    flags: dict


def parse_slash(raw: str) -> Optional[ParsedCommand]:
    """
    Parse a slash command line.

    Examples:
      /cld 寫個排序                        → engine=cld, prompt=寫個排序
      /gld --pro 看一下整個專案             → engine=gld, flags=pro, prompt=看一下整個專案
      /cod:review --base main              → engine=cod, sub=review, base=main
      /cod:rescue --background 修 bug      → engine=cod, sub=rescue, background=True, prompt=修 bug
    """
    raw = raw.strip()
    if not raw.startswith("/"):
        return None

    head, _, rest = raw[1:].partition(" ")
    if ":" in head:
        engine, sub = head.split(":", 1)
    else:
        engine, sub = head, None

    if engine not in CLI_BINARIES:
        return None

    try:
        tokens = shlex.split(rest, posix=(sys.platform != "win32"))
    except ValueError:
        tokens = rest.split()

    flags = {"background": False, "pro": False, "mini": False, "resume": False, "fresh": False}
    prompt_parts: list[str] = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("--background", "--bg"):
            flags["background"] = True
        elif t == "--wait":
            flags["wait"] = True
        elif t == "--pro":
            flags["pro"] = True
        elif t == "--mini":
            flags["mini"] = True
        elif t == "--resume":
            flags["resume"] = True
        elif t == "--fresh":
            flags["fresh"] = True
        elif t == "--base" and i + 1 < len(tokens):
            flags["base"] = tokens[i + 1]; i += 1
        elif t == "--model" and i + 1 < len(tokens):
            flags["model"] = tokens[i + 1]; i += 1
        elif t == "--effort" and i + 1 < len(tokens):
            flags["effort"] = tokens[i + 1]; i += 1
        else:
            prompt_parts.append(t)
        i += 1

    return ParsedCommand(
        engine=engine,
        subcommand=sub,
        prompt=" ".join(prompt_parts),
        flags=flags,
    )


def dispatch(parsed: ParsedCommand) -> JobResult | dict | list:
    """Route a parsed command to the right handler."""
    eng = parsed.engine
    sub = parsed.subcommand

    if sub == "status":
        if parsed.prompt:
            j = refresh_job(parsed.prompt.strip())
            return [j] if j else []
        return [j for j in list_jobs() if j and j.engine == eng]

    if sub == "result":
        target = parsed.prompt.strip()
        if not target:
            jobs = [j for j in list_jobs() if j and j.engine == eng]
            target = jobs[0].job_id if jobs else ""
        j = refresh_job(target) if target else None
        return j or {"error": "no job found"}

    if sub == "cancel":
        target = parsed.prompt.strip()
        if not target:
            jobs = [j for j in list_jobs() if j and j.engine == eng and j.status == "running"]
            target = jobs[0].job_id if jobs else ""
        ok = cancel_job(target) if target else False
        return {"cancelled": ok, "job_id": target}

    if eng == "cod" and sub in ("review", "adversarial-review"):
        return codex_review(
            base=parsed.flags.get("base"),
            background=parsed.flags.get("background", False),
            adversarial=(sub == "adversarial-review"),
            focus=parsed.prompt,
        )

    if eng == "cod" and sub == "rescue":
        return codex_rescue(
            prompt=parsed.prompt,
            background=parsed.flags.get("background", False),
            resume=parsed.flags.get("resume", False),
            fresh=parsed.flags.get("fresh", False),
            model=parsed.flags.get("model"),
            effort=parsed.flags.get("effort"),
        )

    # /gld:review and /gld:rescue — Gemini 版（新增，仿 Codex 機制）
    if eng == "gld" and sub == "review":
        prompt = parsed.prompt or "Review the current branch / uncommitted changes for bugs, design issues, and risks."
        if parsed.flags.get("base"):
            prompt = f"Review changes vs base={parsed.flags['base']}. {prompt}"
        if parsed.flags.get("background"):
            return run_background("gld", prompt, parsed.flags)
        return run_foreground("gld", prompt, parsed.flags)

    if eng == "gld" and sub == "rescue":
        prompt = parsed.prompt or "Investigate the latest issue in this repo and propose a fix."
        if parsed.flags.get("background"):
            return run_background("gld", prompt, parsed.flags)
        return run_foreground("gld", prompt, parsed.flags)

    # Default: plain prompt
    if parsed.flags.get("background"):
        return run_background(eng, parsed.prompt, parsed.flags)
    return run_foreground(eng, parsed.prompt, parsed.flags)
