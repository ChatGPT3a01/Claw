"""Dynamic skill loader — scans directories for SKILL.md files."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SkillManifest:
    name: str
    display_name: str
    version: str
    description: str
    author: str
    tags: tuple[str, ...]

@dataclass(frozen=True)
class LoadedSkill:
    manifest: SkillManifest
    skill_md_content: str
    skill_dir: Path
    has_scripts: bool
    has_references: bool


class SkillLoader:
    """Scans skill directories and loads SKILL.md + manifest.json."""

    def __init__(self, search_paths: list[str | Path]):
        self._paths = [Path(p) for p in search_paths]

    def scan_all(self) -> list[LoadedSkill]:
        skills: list[LoadedSkill] = []
        for base in self._paths:
            if not base.exists():
                continue
            for d in sorted(base.iterdir()):
                if not d.is_dir():
                    continue
                s = self._load_one(d)
                if s:
                    skills.append(s)
        return skills

    def _load_one(self, d: Path) -> LoadedSkill | None:
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            return None
        try:
            content = skill_md.read_text(encoding="utf-8")
        except Exception:
            return None
        manifest = self._parse_manifest(d)
        return LoadedSkill(
            manifest=manifest,
            skill_md_content=content,
            skill_dir=d,
            has_scripts=(d / "scripts").is_dir(),
            has_references=(d / "references").is_dir(),
        )

    def _parse_manifest(self, d: Path) -> SkillManifest:
        mp = d / "manifest.json"
        name = d.name
        if mp.exists():
            try:
                data = json.loads(mp.read_text(encoding="utf-8"))
                return SkillManifest(
                    name=data.get("name", name),
                    display_name=data.get("displayName", name),
                    version=data.get("version", "0.0.0"),
                    description=data.get("description", ""),
                    author=data.get("author", ""),
                    tags=tuple(data.get("tags", [])),
                )
            except Exception:
                pass
        # Fallback: extract first line of SKILL.md as description
        desc = ""
        sm = d / "SKILL.md"
        if sm.exists():
            try:
                first_lines = sm.read_text(encoding="utf-8")[:500]
                for line in first_lines.splitlines():
                    stripped = line.strip().lstrip("#").strip()
                    if stripped:
                        desc = stripped[:200]
                        break
            except Exception:
                pass
        return SkillManifest(
            name=name, display_name=name, version="0.0.0",
            description=desc, author="", tags=(),
        )
