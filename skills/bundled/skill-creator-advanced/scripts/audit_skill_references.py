#!/usr/bin/env python3
"""Check local skill references that break after standalone packaging.

By default this script scans:
- SKILL.md
- references/**/*.md

It validates that any referenced local paths under scripts/, references/, or
assets/ actually exist inside the skill folder.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PATH_REFERENCE_PATTERN = re.compile(
    r"(?<![\w/.-])((?:scripts|references|assets)/[A-Za-z0-9_./-]*[A-Za-z0-9_-]\.[A-Za-z0-9_-]+)"
)
SOURCE_REFERENCE_GLOBS = ("SKILL.md", "references/**/*.md")


def _iter_reference_sources(skill_dir: Path) -> list[Path]:
    sources: list[Path] = []
    for pattern in SOURCE_REFERENCE_GLOBS:
        if "*" in pattern:
            sources.extend(path for path in skill_dir.glob(pattern) if path.is_file())
        else:
            path = skill_dir / pattern
            if path.is_file():
                sources.append(path)
    return sorted(set(path.resolve() for path in sources))


def _clean_token(token: str) -> str:
    cleaned = token.rstrip(".,:;`)\"'")
    while cleaned.endswith("/"):
        cleaned = cleaned[:-1]
    return cleaned


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that SKILL.md local path references exist inside the skill folder"
    )
    parser.add_argument("skill_path", nargs="?", default=".", help="Path to the skill folder")
    args = parser.parse_args()

    skill_dir = Path(args.skill_path).resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"Missing SKILL.md: {skill_md}")
        return 1

    sources = _iter_reference_sources(skill_dir)
    if not sources:
        print("No reference sources found (expected SKILL.md or references/**/*.md)")
        return 1

    missing: list[str] = []
    for source in sources:
        try:
            content = source.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            rel_source = source.relative_to(skill_dir).as_posix()
            print(f"invalid_utf8_source:{rel_source}:{exc}")
            return 1

        rel_source = source.relative_to(skill_dir).as_posix()
        for match in PATH_REFERENCE_PATTERN.finditer(content):
            prefix = content[max(0, match.start() - 24) : match.start()]
            if prefix.endswith("--out ") or prefix.endswith("--output "):
                continue
            token = _clean_token(match.group(1))
            if any(marker in token for marker in ("<", ">", "*", "{", "}")):
                continue
            if not (skill_dir / token).exists():
                missing.append(f"{rel_source}:{token}")

    missing = sorted(set(missing))
    if missing:
        for path in missing:
            print(f"missing_referenced_path:{path}")
        return 1

    print(f"Skill reference audit passed: 0 issues across {len(sources)} source file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
