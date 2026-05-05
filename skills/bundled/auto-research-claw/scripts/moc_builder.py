#!/usr/bin/env python3
"""
MOC（Map of Content）目錄頁自動生成器 — AutoResearchClaw
遞迴掃描論文筆記和概念目錄，生成帶 wikilink 的索引頁。

使用方式：
    python moc_builder.py
    python moc_builder.py --vault ~/ObsidianVault --dry-run
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def load_config() -> dict:
    """載入使用者配置"""
    skill_dir = Path(__file__).parent.parent
    for name in ["user-config.local.json", "user-config.json"]:
        p = skill_dir / "config" / name
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {}


def extract_frontmatter(filepath: Path) -> dict:
    """提取 Markdown YAML frontmatter（優先用 pyyaml，回退手動解析）"""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    raw = match.group(1)

    # 優先使用 pyyaml
    try:
        import yaml
        return yaml.safe_load(raw) or {}
    except ImportError:
        pass

    # 回退：手動解析簡單 key: value
    fm = {}
    for line in raw.split("\n"):
        if ":" in line and not line.strip().startswith("-"):
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


def build_moc(directory: Path, title: str = None, depth: int = 0) -> str:
    """
    為指定目錄生成 MOC 內容

    Args:
        directory: 要掃描的目錄
        title: MOC 標題（預設使用目錄名）
        depth: 遞迴深度（用於縮排）
    """
    if not directory.exists():
        return ""

    title = title or directory.name
    lines = [f"# {title}", "", f"*自動生成於 {datetime.now().strftime('%Y-%m-%d %H:%M')}*", ""]

    # 收集子目錄和檔案
    subdirs = sorted([d for d in directory.iterdir() if d.is_dir() and not d.name.startswith(".")])
    md_files = sorted([f for f in directory.glob("*.md") if f.name != "MOC.md" and f.name != "README.md"])

    # 子目錄
    if subdirs:
        lines.append("## 子目錄")
        lines.append("")
        for subdir in subdirs:
            count = len(list(subdir.glob("*.md")))
            lines.append(f"- 📁 [[{subdir.name}/MOC|{subdir.name}]] ({count} 篇)")
        lines.append("")

    # 檔案列表
    if md_files:
        lines.append("## 筆記列表")
        lines.append("")

        # 按年份分組
        by_year = {}
        no_year = []
        for f in md_files:
            fm = extract_frontmatter(f)
            year = fm.get("year") or fm.get("year_ce") or ""
            if year:
                by_year.setdefault(str(year), []).append(f)
            else:
                no_year.append(f)

        # 按年份倒序
        for year in sorted(by_year.keys(), reverse=True):
            lines.append(f"### {year}")
            lines.append("")
            for f in by_year[year]:
                fm = extract_frontmatter(f)
                name = f.stem
                authors = fm.get("authors", fm.get("author", ""))
                venue = fm.get("venue", fm.get("school", ""))
                is_taiwan = "🇹🇼 " if fm.get("school") or fm.get("ndltd_url") else ""
                meta = f" — {authors}" if authors else ""
                meta += f" @ {venue}" if venue else ""
                lines.append(f"- {is_taiwan}[[{name}]]{meta}")
            lines.append("")

        # 無年份的
        if no_year:
            lines.append("### 其他")
            lines.append("")
            for f in no_year:
                lines.append(f"- [[{f.stem}]]")
            lines.append("")

    # 統計
    total = len(md_files)
    taiwan = sum(1 for f in md_files if extract_frontmatter(f).get("school"))
    lines.append("---")
    lines.append(f"*共 {total} 篇筆記" + (f"（含 🇹🇼 {taiwan} 篇台灣論文）" if taiwan else "") + "*")

    return "\n".join(lines)


def generate_mocs(vault_path: Path, folders: list[str], dry_run: bool = False) -> int:
    """
    為指定資料夾生成 MOC

    Args:
        vault_path: Obsidian Vault 路徑
        folders: 要處理的資料夾列表
        dry_run: 試跑模式，不實際寫入

    Returns:
        更新的 MOC 數量
    """
    updated = 0

    for folder_name in folders:
        folder = vault_path / folder_name
        if not folder.exists():
            print(f"  ⚠ 目錄不存在：{folder}", file=sys.stderr)
            continue

        # 遞迴處理所有子目錄
        dirs_to_process = [folder]
        for subdir in folder.rglob("*"):
            if subdir.is_dir() and not subdir.name.startswith("."):
                dirs_to_process.append(subdir)

        for d in dirs_to_process:
            # 只為含有 .md 檔案或子目錄的目錄生成 MOC
            has_content = any(d.glob("*.md")) or any(
                sd.is_dir() for sd in d.iterdir() if not sd.name.startswith(".")
            )
            if not has_content:
                continue

            moc_path = d / "MOC.md"
            new_content = build_moc(d)

            # 幂等：內容沒變就不寫入
            if moc_path.exists():
                old_content = moc_path.read_text(encoding="utf-8")
                # 忽略時間戳比較
                old_stripped = re.sub(r"\*自動生成於.*?\*", "", old_content)
                new_stripped = re.sub(r"\*自動生成於.*?\*", "", new_content)
                if old_stripped == new_stripped:
                    continue

            if dry_run:
                print(f"  [DRY RUN] 會更新：{moc_path}", file=sys.stderr)
            else:
                moc_path.write_text(new_content, encoding="utf-8")
                print(f"  ✅ 更新：{moc_path}", file=sys.stderr)
            updated += 1

    return updated


def main():
    parser = argparse.ArgumentParser(description="MOC 目錄頁生成器 — AutoResearchClaw")
    parser.add_argument("--vault", default=None, help="Obsidian Vault 路徑")
    parser.add_argument("--folders", nargs="+", default=None, help="要處理的資料夾")
    parser.add_argument("--dry-run", action="store_true", help="試跑模式，不寫入")
    parser.add_argument("--config", default=None, help="設定檔路徑")

    args = parser.parse_args()
    config = load_config() if not args.config else json.loads(Path(args.config).read_text(encoding="utf-8"))

    vault = Path(args.vault or config.get("paths", {}).get("obsidian_vault", "~/ObsidianVault")).expanduser()
    folders = args.folders or [
        config.get("paths", {}).get("paper_notes_folder", "論文筆記"),
        config.get("paths", {}).get("daily_papers_folder", "DailyPapers"),
    ]

    print(f"📚 MOC 生成器 — Vault: {vault}", file=sys.stderr)
    updated = generate_mocs(vault, folders, dry_run=args.dry_run)
    print(f"\n{'🔍 試跑完成' if args.dry_run else '✅ 完成'}：{updated} 個 MOC {'會被' if args.dry_run else '已'}更新", file=sys.stderr)


if __name__ == "__main__":
    main()
