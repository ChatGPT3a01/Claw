"""Skill registry — matching user prompts to loaded skills."""
from __future__ import annotations

import re
from ..utils.logger import get_logger
from .loader import SkillLoader, LoadedSkill

log = get_logger("skills")

# Education-related keywords for matching
_EDU_KEYWORDS: dict[str, list[str]] = {
    "teaching-design": ["教案", "教學設計", "lesson plan", "教學活動", "PBL", "遊戲化", "gamif", "SEL", "差異化"],
    "learning-analytics": ["評量", "assessment", "學習分析", "analytics", "同儕", "peer", "學生輪廓", "profil"],
    "research-methods": ["研究設計", "research", "準實驗", "quasi", "混合研究", "mixed method", "實證"],
    "rural-education": ["偏鄉", "rural", "在地化", "localized"],
    "ai-tools": ["AI工具", "AI tool", "生成式AI", "generative AI"],
    "ict-integration": ["ICT", "資訊融入", "科技融入"],
    "math-tech": ["數學", "math", "GeoGebra", "幾何"],
}


class SkillRegistry:
    """Manages loaded skills and matches prompts to the best skill."""

    def __init__(self, search_paths: list[str]):
        self._loader = SkillLoader(search_paths)
        self._skills: dict[str, LoadedSkill] = {}

    async def scan_and_load(self) -> int:
        loaded = self._loader.scan_all()
        for s in loaded:
            self._skills[s.manifest.name] = s
        log.info("Loaded %d skills", len(self._skills))
        return len(self._skills)

    def match(self, prompt: str, limit: int = 3) -> list[LoadedSkill]:
        """Match prompt to skills by: 1) /command, 2) keyword, 3) description."""
        # 1. Exact slash-command
        cmd_match = re.match(r"^/(\S+)", prompt)
        if cmd_match:
            name = cmd_match.group(1)
            if name in self._skills:
                return [self._skills[name]]

        # 2. Keyword scoring
        prompt_lower = prompt.lower()
        scored: list[tuple[int, LoadedSkill]] = []
        for skill in self._skills.values():
            score = 0
            # Check edu keywords (match against name, tags, and description)
            for category, keywords in _EDU_KEYWORDS.items():
                name_match = category in skill.manifest.name
                tag_match = any(category in t for t in skill.manifest.tags)
                desc_match = category in skill.manifest.description.lower()
                if name_match or tag_match or desc_match:
                    for kw in keywords:
                        if kw.lower() in prompt_lower:
                            score += 10
            # Check skill name in prompt
            if skill.manifest.name.lower().replace("-", " ") in prompt_lower:
                score += 20
            # Check description
            if skill.manifest.description:
                for word in prompt_lower.split():
                    if len(word) > 2 and word in skill.manifest.description.lower():
                        score += 2
            if score > 0:
                scored.append((score, skill))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:limit]]

    def get_skill_context(self, skill_name: str, max_chars: int = 4000) -> str | None:
        skill = self._skills.get(skill_name)
        if not skill:
            return None
        content = skill.skill_md_content
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n... (已截斷，完整內容請參考 SKILL.md)"
        return content

    def list_skills(self) -> list[dict]:
        return [
            {
                "name": s.manifest.name,
                "display_name": s.manifest.display_name,
                "description": s.manifest.description[:100],
                "has_scripts": s.has_scripts,
            }
            for s in sorted(self._skills.values(), key=lambda x: x.manifest.name)
        ]
