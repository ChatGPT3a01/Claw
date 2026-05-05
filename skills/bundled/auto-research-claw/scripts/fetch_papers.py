#!/usr/bin/env python3
"""
多來源論文抓取模組 — AutoResearchClaw
整合 arXiv、HuggingFace Daily/Trending、台灣 NDLTD

使用方式：
    python fetch_papers.py --days 1
    python fetch_papers.py --days 3 --categories cs.AI cs.LG --include-taiwan
    python fetch_papers.py --config ../config/user-config.json
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

# ═══════════════════════════════════════════════════════════
# 資料模型
# ═══════════════════════════════════════════════════════════

@dataclass
class Paper:
    """統一論文資料結構"""
    title: str = ""
    authors: list = field(default_factory=list)
    abstract: str = ""
    url: str = ""
    pdf_url: str = ""
    arxiv_id: str = ""
    doi: str = ""
    categories: list = field(default_factory=list)
    published: str = ""
    source: str = ""  # arxiv / huggingface_daily / huggingface_trending / ndltd
    score: float = 0.0
    is_taiwan: bool = False
    extra: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


# ═══════════════════════════════════════════════════════════
# 來源 1：arXiv API
# ═══════════════════════════════════════════════════════════

class ArxivFetcher:
    """arXiv API 論文抓取"""

    API_URL = "http://export.arxiv.org/api/query"
    ATOM_NS = "{http://www.w3.org/2005/Atom}"

    def fetch(
        self,
        categories: list[str],
        keywords: list[str] = None,
        logic: str = "OR",
        days: int = 1,
        max_results: int = 100,
    ) -> list[Paper]:
        """
        從 arXiv 抓取論文

        Args:
            categories: arXiv 類別，如 ["cs.AI", "cs.LG"]
            keywords: 搜尋關鍵字
            logic: 關鍵字邏輯 AND/OR
            days: 抓取最近幾天
            max_results: 最大回傳數
        """
        # 建構查詢
        cat_query = " OR ".join(f"cat:{c}" for c in categories)
        query_parts = [f"({cat_query})"]

        if keywords:
            kw_parts = [f'all:"{kw}"' for kw in keywords]
            kw_query = f" {logic} ".join(kw_parts)
            query_parts.append(f"({kw_query})")

        search_query = " AND ".join(query_parts)

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "lastUpdatedDate",
            "sortOrder": "descending",
        }

        url = f"{self.API_URL}?{urllib.parse.urlencode(params)}"
        print(f"🔍 arXiv 查詢：{categories} ...", file=sys.stderr)

        # 重試機制：最多 2 次重試，間隔 5 秒
        max_retries = 2
        root = None
        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "AutoResearchClaw/1.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    root = ET.fromstring(resp.read())
                break  # 成功，跳出重試
            except Exception as e:
                if attempt < max_retries:
                    print(f"  ⚠ arXiv 第 {attempt + 1} 次失敗，{5} 秒後重試：{e}", file=sys.stderr)
                    time.sleep(5)
                else:
                    print(f"  ❌ arXiv 查詢失敗（已重試 {max_retries} 次）：{e}", file=sys.stderr)
                    return []

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        papers = []

        for entry in root.findall(f"{self.ATOM_NS}entry"):
            # 解析發布日期
            published_str = entry.findtext(f"{self.ATOM_NS}published", "")
            if published_str:
                try:
                    pub_date = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                    if pub_date < cutoff:
                        continue
                except ValueError:
                    pass

            # 解析 arXiv ID
            entry_id = entry.findtext(f"{self.ATOM_NS}id", "")
            arxiv_id = entry_id.split("/abs/")[-1] if "/abs/" in entry_id else ""

            # 解析 PDF URL
            pdf_url = ""
            for link in entry.findall(f"{self.ATOM_NS}link"):
                if link.get("title") == "pdf":
                    pdf_url = link.get("href", "")
                    break

            # 解析類別
            cats = [
                c.get("term", "")
                for c in entry.findall(f"{self.ATOM_NS}category")
            ]

            paper = Paper(
                title=entry.findtext(f"{self.ATOM_NS}title", "").strip().replace("\n", " "),
                authors=[
                    a.findtext(f"{self.ATOM_NS}name", "")
                    for a in entry.findall(f"{self.ATOM_NS}author")
                ],
                abstract=entry.findtext(f"{self.ATOM_NS}summary", "").strip().replace("\n", " "),
                url=entry_id,
                pdf_url=pdf_url,
                arxiv_id=arxiv_id,
                categories=cats,
                published=published_str,
                source="arxiv",
            )
            papers.append(paper)

        print(f"  ✅ arXiv 回傳 {len(papers)} 篇", file=sys.stderr)
        return papers


# ═══════════════════════════════════════════════════════════
# 來源 2：HuggingFace Daily Papers + Trending
# ═══════════════════════════════════════════════════════════

class HuggingFaceFetcher:
    """HuggingFace Daily Papers 和 Trending 抓取"""

    DAILY_URL = "https://huggingface.co/api/daily_papers"
    TRENDING_URL = "https://huggingface.co/api/trending"

    @staticmethod
    def _request_with_retry(url: str, label: str, max_retries: int = 2, delay: int = 3):
        """帶重試的 HTTP 請求"""
        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "AutoResearchClaw/1.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    return json.loads(resp.read())
            except Exception as e:
                if attempt < max_retries:
                    print(f"  ⚠ {label} 第 {attempt + 1} 次失敗，{delay} 秒後重試：{e}", file=sys.stderr)
                    time.sleep(delay)
                else:
                    print(f"  ❌ {label} 失敗（已重試 {max_retries} 次）：{e}", file=sys.stderr)
                    return None

    def fetch_daily(self, days: int = 1) -> list[Paper]:
        """抓取 HuggingFace Daily Papers"""
        papers = []
        for day_offset in range(days):
            date = (datetime.now(timezone.utc) - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            url = f"{self.DAILY_URL}?date={date}"
            print(f"🔍 HuggingFace Daily Papers ({date}) ...", file=sys.stderr)

            data = self._request_with_retry(url, f"HuggingFace Daily ({date})")
            if data is None:
                continue

            for item in data if isinstance(data, list) else []:
                paper_data = item.get("paper", item)
                arxiv_id = paper_data.get("id", "")
                paper = Paper(
                    title=paper_data.get("title", ""),
                    authors=[a.get("name", "") for a in paper_data.get("authors", [])],
                    abstract=paper_data.get("summary", ""),
                    url=f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
                    pdf_url=f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else "",
                    arxiv_id=arxiv_id,
                    published=paper_data.get("publishedAt", ""),
                    source="huggingface_daily",
                    extra={"upvotes": item.get("paper", {}).get("upvotes", 0)},
                )
                if paper.title:
                    papers.append(paper)

            time.sleep(0.5)  # 禮貌延遲

        print(f"  ✅ HuggingFace Daily 回傳 {len(papers)} 篇", file=sys.stderr)
        return papers

    def fetch_trending(self) -> list[Paper]:
        """抓取 HuggingFace Trending Papers"""
        print(f"🔍 HuggingFace Trending ...", file=sys.stderr)
        data = self._request_with_retry(self.TRENDING_URL, "HuggingFace Trending")
        if data is None:
            return []

        papers = []
        for item in data if isinstance(data, list) else []:
            if item.get("type") != "paper":
                continue
            paper = Paper(
                title=item.get("title", ""),
                url=f"https://huggingface.co/papers/{item.get('id', '')}",
                arxiv_id=item.get("id", ""),
                source="huggingface_trending",
                extra={"likes": item.get("likes", 0)},
            )
            if paper.title:
                papers.append(paper)

        print(f"  ✅ HuggingFace Trending 回傳 {len(papers)} 篇", file=sys.stderr)
        return papers


# ═══════════════════════════════════════════════════════════
# 評分與篩選
# ═══════════════════════════════════════════════════════════

class PaperScorer:
    """論文關鍵字評分"""

    def __init__(self, config: dict):
        self.keywords = [kw.lower() for kw in config.get("keywords", [])]
        self.negative_keywords = [kw.lower() for kw in config.get("negative_keywords", [])]
        self.domain_boost = [kw.lower() for kw in config.get("domain_boost_keywords", [])]
        self.taiwan_bonus = config.get("taiwan", {}).get("bonus_score", 2)
        self.min_score = config.get("min_score", 2)

    def score(self, paper: Paper) -> float:
        """計算論文分數"""
        text = f"{paper.title} {paper.abstract}".lower()
        score = 0.0

        # 負向關鍵字（一票否決）
        for kw in self.negative_keywords:
            if kw in text:
                return -999

        # 正向關鍵字
        for kw in self.keywords:
            if kw in paper.title.lower():
                score += 3  # 標題匹配權重高
            elif kw in text:
                score += 1

        # 領域加分
        for kw in self.domain_boost:
            if kw in text:
                score += 2

        # HuggingFace 熱度加分
        upvotes = paper.extra.get("upvotes", 0) or paper.extra.get("likes", 0)
        if upvotes >= 50:
            score += 3
        elif upvotes >= 20:
            score += 2
        elif upvotes >= 5:
            score += 1

        # 台灣論文加分
        if paper.is_taiwan:
            score += self.taiwan_bonus

        return score


# ═══════════════════════════════════════════════════════════
# 去重
# ═══════════════════════════════════════════════════════════

class Deduplicator:
    """論文去重（跨天 + 跨來源）"""

    def __init__(self, history_path: Path):
        self.history_path = history_path
        self.history = self._load()

    def _load(self) -> dict:
        if self.history_path.exists():
            try:
                return json.loads(self.history_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"seen": {}, "last_cleanup": ""}

    def save(self):
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.write_text(
            json.dumps(self.history, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def is_seen(self, paper: Paper) -> bool:
        """檢查論文是否已推薦過"""
        key = self._make_key(paper)
        return key in self.history.get("seen", {})

    def mark_seen(self, paper: Paper):
        """標記論文為已推薦"""
        key = self._make_key(paper)
        self.history.setdefault("seen", {})[key] = datetime.now().isoformat()

    def cleanup(self, days: int = 30):
        """清理超過 N 天的記錄"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        self.history["seen"] = {
            k: v for k, v in self.history.get("seen", {}).items()
            if v > cutoff
        }
        self.history["last_cleanup"] = datetime.now().isoformat()

    @staticmethod
    def _make_key(paper: Paper) -> str:
        if paper.arxiv_id:
            return f"arxiv:{paper.arxiv_id}"
        if paper.doi:
            return f"doi:{paper.doi}"
        # 用標題正規化作為 key
        return "title:" + re.sub(r"\s+", "", paper.title.lower())


# ═══════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════

def load_config(config_path: str = None) -> dict:
    """載入設定檔"""
    if config_path and Path(config_path).exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        # 嘗試預設路徑
        skill_dir = Path(__file__).parent.parent
        for name in ["user-config.local.json", "user-config.json"]:
            p = skill_dir / "config" / name
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    config = json.load(f)
                break
        else:
            config = {}
    return config


def get_temp_dir() -> Path:
    """取得暫存目錄（跨平台）"""
    if sys.platform == "win32":
        tmp = Path.home() / "tmp"
    else:
        tmp = Path("/tmp")
    tmp.mkdir(parents=True, exist_ok=True)
    return tmp


def main():
    parser = argparse.ArgumentParser(description="多來源論文抓取 — AutoResearchClaw")
    parser.add_argument("--days", "-d", type=int, default=1, help="抓取最近幾天（預設 1）")
    parser.add_argument("--categories", "-c", nargs="+", default=None, help="arXiv 類別")
    parser.add_argument("--keywords", "-k", nargs="+", default=None, help="搜尋關鍵字")
    parser.add_argument("--include-taiwan", action="store_true", default=True, help="包含台灣論文")
    parser.add_argument("--no-taiwan", action="store_true", help="不包含台灣論文")
    parser.add_argument("--top-n", "-n", type=int, default=30, help="最終保留篇數")
    parser.add_argument("--config", default=None, help="設定檔路徑")
    parser.add_argument("--output", "-o", default=None, help="輸出路徑（預設 ~/tmp/ 或 /tmp/）")
    parser.add_argument("--no-dedup", action="store_true", help="停用跨天去重")

    args = parser.parse_args()
    config = load_config(args.config)
    dp_config = config.get("daily_papers", {})

    # 參數合併（CLI 優先）
    categories = args.categories or dp_config.get("arxiv_categories", ["cs.AI", "cs.LG"])
    keywords = args.keywords or dp_config.get("keywords", [])
    top_n = args.top_n or dp_config.get("top_n", 30)
    include_taiwan = not args.no_taiwan and dp_config.get("include_taiwan_theses", True)

    # 抓取
    all_papers = []

    # 1. arXiv
    arxiv = ArxivFetcher()
    all_papers.extend(arxiv.fetch(categories=categories, keywords=keywords, days=args.days))

    # 2. HuggingFace
    hf = HuggingFaceFetcher()
    all_papers.extend(hf.fetch_daily(days=args.days))
    if args.days <= 1:
        all_papers.extend(hf.fetch_trending())

    # 3. 台灣論文
    if include_taiwan:
        tw_config = config.get("taiwan", {})
        tw_keywords = tw_config.get("keywords_zh", [])
        if tw_keywords or keywords:
            try:
                _script_dir = str(Path(__file__).parent)
                if _script_dir not in sys.path:
                    sys.path.insert(0, _script_dir)
                from taiwan_academic_search import TaiwanAcademicSearch
                tw_searcher = TaiwanAcademicSearch(tw_config)
                for kw in (tw_keywords or keywords)[:3]:  # 最多用 3 個關鍵字
                    tw_result = tw_searcher.search(keyword=kw, sources=["ndltd"], top_n=10)
                    for r in tw_result.get("results", []):
                        paper = Paper(
                            title=r.get("title", ""),
                            authors=[r.get("author", "")],
                            abstract=r.get("abstract", ""),
                            url=r.get("url", "") or r.get("handle_url", ""),
                            published=str(r.get("year_ce", "")),
                            source="ndltd",
                            is_taiwan=True,
                            extra={
                                "school": r.get("school", ""),
                                "department": r.get("department", ""),
                                "advisor": r.get("advisor", ""),
                                "degree": r.get("degree", ""),
                                "year_roc": r.get("year_roc", 0),
                            },
                        )
                        all_papers.append(paper)
            except ImportError:
                print("  ⚠ 台灣論文模組未安裝，跳過", file=sys.stderr)

    # 去重
    before = len(all_papers)
    if not args.no_dedup:
        vault = Path(config.get("paths", {}).get("obsidian_vault", "~/ObsidianVault")).expanduser()
        dp_folder = config.get("paths", {}).get("daily_papers_folder", "DailyPapers")
        history_path = vault / dp_folder / ".history.json"
        dedup = Deduplicator(history_path)
        dedup.cleanup(dp_config.get("dedup_window_days", 30))
        all_papers = [p for p in all_papers if not dedup.is_seen(p)]
        print(f"📋 去重：{before} → {len(all_papers)} 篇", file=sys.stderr)

    # 評分
    scorer = PaperScorer({**dp_config, "taiwan": config.get("taiwan", {})})
    for paper in all_papers:
        paper.score = scorer.score(paper)

    # 過濾低分 + 排序
    min_score = dp_config.get("min_score", 0)
    all_papers = [p for p in all_papers if p.score >= min_score]
    all_papers.sort(key=lambda p: p.score, reverse=True)
    top_papers = all_papers[:top_n]

    # 標記為已推薦
    if not args.no_dedup:
        for p in top_papers:
            dedup.mark_seen(p)
        dedup.save()

    # 輸出
    output_path = args.output or str(get_temp_dir() / "daily_papers_top30.json")
    result = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "days": args.days,
        "total_fetched": before,
        "after_dedup": len(all_papers),
        "top_n": len(top_papers),
        "papers": [p.to_dict() for p in top_papers],
    }

    Path(output_path).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ 完成！Top {len(top_papers)} 篇已儲存至 {output_path}", file=sys.stderr)

    # 統計摘要
    sources = {}
    for p in top_papers:
        sources[p.source] = sources.get(p.source, 0) + 1
    tw_count = sum(1 for p in top_papers if p.is_taiwan)
    print(f"📊 來源分布：{sources}", file=sys.stderr)
    if tw_count:
        print(f"🇹🇼 台灣論文：{tw_count} 篇", file=sys.stderr)


if __name__ == "__main__":
    main()
