#!/usr/bin/env python3
"""
Prompt 模板載入與展開器 — AutoResearchClaw

載入 prompts.yaml，自動展開 blocks 引用，填入使用者變數。

使用方式：
    from prompt_loader import PromptLoader
    loader = PromptLoader()
    prompt = loader.render("daily_review", {"date": "2026-03-31", "count": 30, "papers_json": "..."})

    # 取得特定 variant
    prompt = loader.render("paper_draft", {"topic": "...", ...}, variant="apa")
"""

import re
import sys
from pathlib import Path
from typing import Optional


def _load_yaml(path: Path) -> dict:
    """載入 YAML（優先 pyyaml，回退手動解析）"""
    text = path.read_text(encoding="utf-8")

    try:
        import yaml
        return yaml.safe_load(text) or {}
    except ImportError:
        pass

    # 回退：基本解析（僅支援頂層 key-value 和多行字串）
    print("  ⚠ pyyaml 未安裝，使用簡易解析器（建議 pip install pyyaml）", file=sys.stderr)
    result = {}
    current_key = None
    current_value = []

    for line in text.split("\n"):
        if line.startswith("#") or not line.strip():
            continue
        if not line.startswith(" ") and ":" in line:
            if current_key:
                result[current_key] = "\n".join(current_value).strip()
            key, _, val = line.partition(":")
            current_key = key.strip()
            current_value = [val.strip().lstrip("|").strip()]
        elif current_key:
            current_value.append(line)

    if current_key:
        result[current_key] = "\n".join(current_value).strip()

    return result


class PromptLoader:
    """載入並展開 prompts.yaml 的提示詞模板"""

    def __init__(self, config_dir: Path = None):
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        self.config_dir = config_dir
        self._data = None
        self._blocks = None

    @property
    def data(self) -> dict:
        if self._data is None:
            self._data = _load_yaml(self.config_dir / "prompts.yaml")
        return self._data

    @property
    def blocks(self) -> dict:
        if self._blocks is None:
            self._blocks = self.data.get("blocks", {})
        return self._blocks

    def list_prompts(self) -> list[str]:
        """列出所有可用的提示詞 key"""
        return [k for k in self.data if k != "blocks"]

    def get_raw(self, key: str) -> dict:
        """取得原始提示詞定義（含 system/user/variants）"""
        prompt_def = self.data.get(key)
        if prompt_def is None:
            raise KeyError(f"提示詞 '{key}' 不存在。可用：{self.list_prompts()}")
        return prompt_def

    def _expand_blocks(self, text: str) -> str:
        """展開 {block_name} 引用"""
        def replacer(match):
            block_name = match.group(1)
            if block_name in self.blocks:
                return self.blocks[block_name].strip()
            return match.group(0)  # 非 block 的 placeholder 保留原樣

        return re.sub(r"\{(\w+)\}", replacer, text)

    def _fill_variables(self, text: str, variables: dict) -> str:
        """填入使用者變數"""
        for key, value in variables.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text

    def render(
        self,
        prompt_key: str,
        variables: dict = None,
        variant: str = None,
    ) -> dict:
        """
        渲染完整提示詞

        Args:
            prompt_key: 提示詞 key（如 "daily_review", "paper_draft"）
            variables: 要填入的變數字典
            variant: paper_draft 等有 variants 的提示詞需指定變體

        Returns:
            {"system": str, "user": str, "max_tokens": int}
        """
        variables = variables or {}
        raw = self.get_raw(prompt_key)

        system_text = raw.get("system", "")
        user_text = raw.get("user", "")
        max_tokens = raw.get("max_tokens", 4096)

        # 處理 variants（如 paper_draft 的 conference/apa/apa_journal）
        if variant and "variants" in raw:
            variant_data = raw["variants"].get(variant)
            if variant_data is None:
                available = list(raw["variants"].keys())
                raise KeyError(f"變體 '{variant}' 不存在。可用：{available}")
            # 將 variant 的 format_instruction 加入 system
            format_inst = variant_data.get("format_instruction", "")
            if format_inst:
                system_text += "\n\n" + format_inst
            # variant 可能覆蓋 max_tokens
            max_tokens = variant_data.get("max_tokens", max_tokens)

        # Step 1: 展開 blocks 引用
        system_text = self._expand_blocks(system_text)
        user_text = self._expand_blocks(user_text)

        # Step 2: 填入使用者變數
        system_text = self._fill_variables(system_text, variables)
        user_text = self._fill_variables(user_text, variables)

        return {
            "system": system_text.strip(),
            "user": user_text.strip(),
            "max_tokens": max_tokens,
        }

    def render_messages(
        self,
        prompt_key: str,
        variables: dict = None,
        variant: str = None,
    ) -> list[dict]:
        """
        渲染為 OpenAI 相容的 messages 格式

        Returns:
            [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        rendered = self.render(prompt_key, variables, variant)
        messages = []
        if rendered["system"]:
            messages.append({"role": "system", "content": rendered["system"]})
        if rendered["user"]:
            messages.append({"role": "user", "content": rendered["user"]})
        return messages


def validate_config(config_path: Path = None) -> list[str]:
    """
    驗證 user-config.json 的必要欄位

    Returns:
        錯誤訊息列表（空列表 = 驗證通過）
    """
    import json

    if config_path is None:
        config_dir = Path(__file__).parent.parent / "config"
        for name in ["user-config.local.json", "user-config.json"]:
            p = config_dir / name
            if p.exists():
                config_path = p
                break

    if config_path is None or not config_path.exists():
        return ["找不到設定檔"]

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"JSON 格式錯誤：{e}"]

    errors = []

    # 必要路徑
    paths = config.get("paths", {})
    if not paths.get("obsidian_vault"):
        errors.append("缺少 paths.obsidian_vault")

    # daily_papers 必要欄位
    dp = config.get("daily_papers", {})
    if not dp.get("keywords"):
        errors.append("缺少 daily_papers.keywords（至少需要 1 個關鍵字）")
    if not dp.get("arxiv_categories"):
        errors.append("缺少 daily_papers.arxiv_categories（至少需要 1 個類別）")

    # taiwan 設定驗證
    tw = config.get("taiwan", {})
    if tw.get("enabled", True):
        repos = tw.get("institutional_repositories", {})
        if repos.get("enabled") and not repos.get("endpoints"):
            errors.append("taiwan.institutional_repositories.enabled=true 但沒有 endpoints")

    # deep_research 格式驗證
    dr = config.get("deep_research", {})
    valid_formats = {"apa", "apa_journal", "neurips", "icml", "iclr"}
    fmt = dr.get("paper_format", "apa")
    if fmt not in valid_formats:
        errors.append(f"deep_research.paper_format='{fmt}' 無效，可用：{valid_formats}")

    # LLM 設定
    llm = config.get("llm", {})
    if not llm.get("model"):
        errors.append("缺少 llm.model")

    return errors


if __name__ == "__main__":
    # 範例：驗證設定檔
    print("🔍 驗證設定檔...", file=sys.stderr)
    errors = validate_config()
    if errors:
        print("❌ 設定檔有問題：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✅ 設定檔驗證通過", file=sys.stderr)

    # 範例：列出所有提示詞
    loader = PromptLoader()
    print(f"\n📋 可用提示詞：{loader.list_prompts()}", file=sys.stderr)

    # 範例：渲染一個提示詞
    rendered = loader.render("daily_review", {
        "date": "2026-03-31",
        "count": "30",
        "papers_json": "[...]",
    })
    print(f"\n--- daily_review system ---\n{rendered['system'][:200]}...", file=sys.stderr)
    print(f"\n--- daily_review user ---\n{rendered['user'][:200]}...", file=sys.stderr)
