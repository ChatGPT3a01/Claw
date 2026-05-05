"""Tests for skill loader and registry."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.skills.loader import SkillLoader, SkillManifest, LoadedSkill
from src.skills.registry import SkillRegistry


class TestSkillLoader:
    def test_scan_finds_skills(self, skill_dir):
        loader = SkillLoader([str(skill_dir)])
        skills = loader.scan_all()
        assert len(skills) == 2  # lesson-plan-generator + learning-analytics-tool

    def test_ignores_dirs_without_skill_md(self, skill_dir):
        loader = SkillLoader([str(skill_dir)])
        skills = loader.scan_all()
        names = [s.manifest.name for s in skills]
        assert "no-skill-dir" not in names

    def test_manifest_parsed_from_json(self, skill_dir):
        loader = SkillLoader([str(skill_dir)])
        skills = loader.scan_all()
        lpg = [s for s in skills if s.manifest.name == "lesson-plan-generator"][0]
        assert lpg.manifest.display_name == "教案產生器"
        assert lpg.manifest.version == "1.0.0"
        assert "teaching-design" in lpg.manifest.tags

    def test_fallback_manifest(self, skill_dir):
        loader = SkillLoader([str(skill_dir)])
        skills = loader.scan_all()
        lat = [s for s in skills if s.manifest.name == "learning-analytics-tool"][0]
        # No manifest.json — should use directory name
        assert lat.manifest.display_name == "learning-analytics-tool"
        assert lat.manifest.version == "0.0.0"

    def test_empty_search_paths(self, tmp_path):
        loader = SkillLoader([str(tmp_path / "nonexistent")])
        assert loader.scan_all() == []

    def test_skill_md_content_loaded(self, skill_dir):
        loader = SkillLoader([str(skill_dir)])
        skills = loader.scan_all()
        lpg = [s for s in skills if s.manifest.name == "lesson-plan-generator"][0]
        assert "教案產生器" in lpg.skill_md_content


class TestSkillRegistry:
    @pytest.fixture
    def registry(self, skill_dir, mock_config):
        mock_config.skill_search_paths = [str(skill_dir)]
        reg = SkillRegistry([str(skill_dir)])
        import asyncio
        asyncio.get_event_loop().run_until_complete(reg.scan_and_load())
        return reg

    def test_list_skills(self, registry):
        skills = registry.list_skills()
        assert len(skills) == 2

    def test_match_by_keyword(self, registry):
        matched = registry.match("幫我設計一堂教案", limit=3)
        assert len(matched) >= 1
        assert matched[0].manifest.name == "lesson-plan-generator"

    def test_match_no_result(self, registry):
        matched = registry.match("今天天氣如何", limit=3)
        assert len(matched) == 0

    def test_get_skill_context(self, registry):
        ctx = registry.get_skill_context("lesson-plan-generator", max_chars=4000)
        assert ctx is not None
        assert "教案產生器" in ctx

    def test_get_skill_context_truncation(self, registry):
        ctx = registry.get_skill_context("lesson-plan-generator", max_chars=10)
        assert ctx is not None
        assert "已截斷" in ctx

    def test_get_nonexistent_skill(self, registry):
        assert registry.get_skill_context("not-exist") is None
