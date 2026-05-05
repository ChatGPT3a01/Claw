"""
Build student-facing zip package for Claw v2.0.
Excludes caches, runtime jobs, secrets, and dev-only files.
"""
from __future__ import annotations

import datetime
import fnmatch
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent

VERSION = "2.0.0"
DATE = datetime.datetime.now().strftime("%Y%m%d")
ZIP_NAME = f"Claw_v{VERSION}_學員版_{DATE}.zip"
OUT_PATH = PARENT / ZIP_NAME

EXCLUDE_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".ruff_cache",
}

EXCLUDE_FILE_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.log",
    ".DS_Store",
    "Thumbs.db",
    ".env",
    "*.tmp",
]

EXCLUDE_RELATIVE_PATHS = {
    Path(".claw") / "jobs",
    Path("build_student_zip.py"),
}


def should_skip_dir(path: Path) -> bool:
    if path.name in EXCLUDE_DIRS:
        return True
    rel = path.relative_to(ROOT)
    if rel in EXCLUDE_RELATIVE_PATHS:
        return True
    return False


def should_skip_file(path: Path) -> bool:
    name = path.name
    for pattern in EXCLUDE_FILE_PATTERNS:
        if fnmatch.fnmatch(name, pattern):
            return True
    rel = path.relative_to(ROOT)
    if rel in EXCLUDE_RELATIVE_PATHS:
        return True
    return False


def collect_files() -> list[Path]:
    files: list[Path] = []
    skipped_dirs: list[Path] = []

    for path in ROOT.rglob("*"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.is_dir():
            if should_skip_dir(path):
                skipped_dirs.append(path)
            continue
        if should_skip_file(path):
            continue
        rel = path.relative_to(ROOT)
        if any(str(rel).startswith(str(p)) for p in EXCLUDE_RELATIVE_PATHS):
            continue
        files.append(path)

    return files


def main() -> int:
    if OUT_PATH.exists():
        print(f"[!] Removing existing: {OUT_PATH.name}")
        OUT_PATH.unlink()

    print(f"[*] Source: {ROOT}")
    print(f"[*] Output: {OUT_PATH}")
    print(f"[*] Collecting files...")
    files = collect_files()
    print(f"[*] Found {len(files)} files to package.")

    arcroot = f"Claw_v{VERSION}"
    total_bytes = 0
    with zipfile.ZipFile(OUT_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for i, f in enumerate(files, 1):
            rel = f.relative_to(ROOT)
            arcname = f"{arcroot}/{rel.as_posix()}"
            zf.write(f, arcname)
            total_bytes += f.stat().st_size
            if i % 200 == 0:
                print(f"    ... {i}/{len(files)}")

    out_size_mb = OUT_PATH.stat().st_size / (1024 * 1024)
    src_size_mb = total_bytes / (1024 * 1024)
    ratio = (1 - OUT_PATH.stat().st_size / total_bytes) * 100 if total_bytes else 0

    print()
    print(f"[OK] Package created: {OUT_PATH.name}")
    print(f"     Source size:   {src_size_mb:.2f} MB")
    print(f"     Zip size:      {out_size_mb:.2f} MB")
    print(f"     Compression:   {ratio:.1f}%")
    print(f"     File count:    {len(files)}")
    print(f"     Location:      {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
