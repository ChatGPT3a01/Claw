#!/usr/bin/env python3
"""
台灣學術論文搜尋模組 — AutoResearchClaw
支援 NDLTD 開放資料、NDLTD Web 搜尋、各大學 OAI-PMH 機構典藏、Crossref API

使用方式：
    python taiwan_academic_search.py --keyword "深度學習" --school "臺灣大學" --year-range 2020-2025
    python taiwan_academic_search.py --keyword "natural language processing" --degree 博士 --top-n 20
    python taiwan_academic_search.py --keyword "教育科技" --source ndltd --output results.json
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import urllib.request
import urllib.parse
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

# ═══════════════════════════════════════════════════════════
# 資料模型
# ═══════════════════════════════════════════════════════════

@dataclass
class TaiwanThesis:
    """台灣博碩士論文資料結構"""
    title: str = ""
    title_en: str = ""
    author: str = ""
    advisor: str = ""
    school: str = ""
    department: str = ""
    degree: str = ""  # 碩士/博士
    year_roc: int = 0  # 民國年
    year_ce: int = 0   # 西元年
    abstract: str = ""
    abstract_en: str = ""
    keywords: list = field(default_factory=list)
    url: str = ""
    handle_url: str = ""
    doi: str = ""
    source: str = ""  # ndltd_opendata / ndltd_web / oai_pmh / crossref
    score: float = 0.0

    def to_dict(self):
        return asdict(self)

    @property
    def display_year(self):
        if self.year_ce:
            return f"民國{self.year_roc}年（{self.year_ce}）"
        return f"民國{self.year_roc}年" if self.year_roc else "未知"


def roc_to_ce(roc_year: int) -> int:
    """民國年轉西元年"""
    return roc_year + 1911


def ce_to_roc(ce_year: int) -> int:
    """西元年轉民國年"""
    return ce_year - 1911


# ═══════════════════════════════════════════════════════════
# 來源 1：NDLTD 開放資料（CSV 下載，2013-2023）
# ═══════════════════════════════════════════════════════════

class NDLTDOpenData:
    """
    國家圖書館 NDLTD 開放資料 CSV
    來源：https://data.gov.tw/dataset/14024
    URL 格式：https://ndltd.ncl.edu.tw/opendata/{民國年}ndltd.csv
    涵蓋：民國 102-112 年（2013-2023）
    欄位：論文名稱, 論文名稱(外文), 學校名稱, 系所名稱, 畢業學年度, 學位類別, 作者, 指導教授, 博碩士論文網址
    """

    BASE_URL = "https://ndltd.ncl.edu.tw/opendata/"
    CACHE_DIR = Path.home() / ".cache" / "auto-research-claw" / "ndltd"
    YEAR_RANGE = range(102, 113)  # 民國 102-112

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else self.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _download_csv(self, roc_year: int) -> Path:
        """下載指定民國年的 CSV 檔案，有快取機制"""
        cache_path = self.cache_dir / f"{roc_year}ndltd.csv"
        if cache_path.exists():
            # 快取 7 天有效
            age = datetime.now().timestamp() - cache_path.stat().st_mtime
            if age < 7 * 24 * 3600:
                return cache_path

        url = f"{self.BASE_URL}{roc_year}ndltd.csv"
        print(f"  下載 NDLTD 開放資料：民國 {roc_year} 年 ...", file=sys.stderr)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AutoResearchClaw/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            cache_path.write_bytes(data)
            return cache_path
        except urllib.error.URLError as e:
            print(f"  ⚠ 下載失敗（民國 {roc_year} 年）：{e}", file=sys.stderr)
            return None

    def _parse_csv(self, csv_path: Path) -> list[TaiwanThesis]:
        """解析 CSV 為 TaiwanThesis 列表"""
        results = []
        try:
            raw = csv_path.read_bytes()
            # 嘗試 UTF-8 BOM / UTF-8 / Big5
            for encoding in ["utf-8-sig", "utf-8", "big5"]:
                try:
                    text = raw.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                return results

            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                roc_year = int(row.get("畢業學年度", 0) or 0)
                thesis = TaiwanThesis(
                    title=row.get("論文名稱", "").strip(),
                    title_en=row.get("論文名稱(外文)", "").strip(),
                    school=row.get("學校名稱", "").strip(),
                    department=row.get("系所名稱", "").strip(),
                    degree=row.get("學位類別", "").strip(),
                    year_roc=roc_year,
                    year_ce=roc_to_ce(roc_year) if roc_year else 0,
                    author=row.get("作者", "").strip(),
                    advisor=row.get("指導教授", "").strip(),
                    handle_url=row.get("博碩士論文網址", "").strip(),
                    url=row.get("博碩士論文網址", "").strip(),
                    source="ndltd_opendata",
                )
                if thesis.title:
                    results.append(thesis)
        except Exception as e:
            print(f"  ⚠ 解析 CSV 失敗：{e}", file=sys.stderr)
        return results

    def search(
        self,
        keyword: str = "",
        school: str = "",
        department: str = "",
        advisor: str = "",
        degree: str = "",
        year_range: tuple = None,
        top_n: int = 50,
    ) -> list[TaiwanThesis]:
        """
        搜尋 NDLTD 開放資料

        Args:
            keyword: 搜尋關鍵字（搜尋標題、英文標題）
            school: 學校篩選
            department: 系所篩選
            advisor: 指導教授篩選
            degree: 學位類別（碩士/博士）
            year_range: (起始民國年, 結束民國年) 或 (起始西元年, 結束西元年)
            top_n: 最多回傳幾篇
        """
        # 自動偵測西元年/民國年
        if year_range:
            start, end = year_range
            if start > 1900:  # 西元年
                start, end = ce_to_roc(start), ce_to_roc(end)
            years = range(max(start, 102), min(end, 112) + 1)
        else:
            years = self.YEAR_RANGE

        all_theses = []
        for year in years:
            csv_path = self._download_csv(year)
            if csv_path:
                all_theses.extend(self._parse_csv(csv_path))

        # 篩選
        results = []
        keyword_lower = keyword.lower() if keyword else ""
        for t in all_theses:
            if keyword_lower and keyword_lower not in t.title.lower() and keyword_lower not in t.title_en.lower():
                continue
            if school and school not in t.school:
                continue
            if department and department not in t.department:
                continue
            if advisor and advisor not in t.advisor:
                continue
            if degree and degree != t.degree:
                continue
            results.append(t)

        # 排序：博士優先，年份新的優先
        results.sort(key=lambda t: (t.degree == "博士", t.year_roc), reverse=True)
        return results[:top_n]


# ═══════════════════════════════════════════════════════════
# 來源 2：NDLTD Web 搜尋（含摘要，全年份）
# ═══════════════════════════════════════════════════════════

class NDLTDWebSearch:
    """
    NDLTD Web 搜尋（透過 URL 建構搜尋查詢）
    注意：此方法可能被 CAPTCHA 阻擋，建議作為備用方案
    主要用於生成搜尋 URL 讓使用者在瀏覽器中開啟
    """

    BASE = "https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi"

    # 欄位代碼對照
    FIELD_MAP = {
        "title": "ti",
        "author": "au",
        "advisor": "ad",
        "keyword": "kw",
        "abstract": "ab",
        "all": "ALLFIELD",
    }

    @classmethod
    def build_search_url(cls, keyword: str, field: str = "all") -> str:
        """建構 NDLTD 搜尋 URL（供使用者在瀏覽器中開啟）"""
        field_code = cls.FIELD_MAP.get(field, "ALLFIELD")
        query = urllib.parse.quote(keyword)
        return (
            f"{cls.BASE}?o=dnclcdr"
            f"&s={field_code}%3D%22{query}%22"
            f"&searchmode=basic"
        )

    @classmethod
    def build_advanced_search_url(
        cls,
        keywords: list[str],
        fields: list[str] = None,
        logic: str = "AND",
    ) -> str:
        """建構進階搜尋 URL"""
        if fields is None:
            fields = ["all"] * len(keywords)

        parts = []
        for kw, f in zip(keywords, fields):
            fc = cls.FIELD_MAP.get(f, "ALLFIELD")
            parts.append(f'{fc}="{kw}"')

        query = f" {logic} ".join(parts)
        encoded = urllib.parse.quote(query)
        return (
            f"{cls.BASE}?o=dnclcdr"
            f"&s={encoded}"
            f"&searchmode=basic"
        )

    @classmethod
    def build_id_url(cls, thesis_id: str) -> str:
        """用論文系統 ID 查詢（如 110NTHU5650010）"""
        return (
            f"{cls.BASE}?o=dnclcdr"
            f"&s=id%3D%22{thesis_id}%22"
            f"&searchmode=basic"
        )

    @classmethod
    def resolve_short_url(cls, short_code: str) -> str:
        """短連結解析"""
        return f"https://ndltd.ncl.edu.tw/r/{short_code}"


# ═══════════════════════════════════════════════════════════
# 來源 3：各大學 OAI-PMH 機構典藏
# ═══════════════════════════════════════════════════════════

class InstitutionalRepository:
    """
    透過 OAI-PMH 協議查詢各大學機構典藏
    使用 Dublin Core (oai_dc) 元資料格式
    """

    # 預設端點
    ENDPOINTS = {
        "臺灣大學": "https://tdr.lib.ntu.edu.tw/oai/request",
        "清華大學": "https://etd.lib.nthu.edu.tw/oai/request",
        "成功大學": "https://etds.lib.ncku.edu.tw/oai/request",
        "陽明交通大學": "https://etd.lib.nycu.edu.tw/oai/request",
        "政治大學": "https://thesis.lib.nccu.edu.tw/oai/request",
        "中央大學": "https://ir.lib.ncu.edu.tw/oai/request",
        "中山大學": "https://etd.lib.nsysu.edu.tw/oai/request",
        "臺灣師範大學": "https://etds.lib.ntnu.edu.tw/oai/request",
    }

    DC_NS = "http://purl.org/dc/elements/1.1/"
    OAI_NS = "http://www.openarchives.org/OAI/2.0/"

    def __init__(self, endpoints: dict = None):
        self.endpoints = endpoints or self.ENDPOINTS

    def _oai_request(self, base_url: str, params: dict) -> Optional[ET.Element]:
        """發送 OAI-PMH 請求"""
        query = urllib.parse.urlencode(params)
        url = f"{base_url}?{query}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AutoResearchClaw/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return ET.fromstring(resp.read())
        except Exception as e:
            print(f"  ⚠ OAI-PMH 請求失敗 ({base_url}): {e}", file=sys.stderr)
            return None

    def _dc_text(self, record: ET.Element, field: str) -> str:
        """從 Dublin Core 記錄中提取欄位"""
        el = record.find(f".//{{{self.DC_NS}}}{field}")
        return el.text.strip() if el is not None and el.text else ""

    def _dc_texts(self, record: ET.Element, field: str) -> list[str]:
        """從 Dublin Core 記錄中提取多值欄位"""
        return [
            el.text.strip()
            for el in record.findall(f".//{{{self.DC_NS}}}{field}")
            if el.text
        ]

    def _parse_records(self, root: ET.Element, school: str) -> list[TaiwanThesis]:
        """從 OAI-PMH 回應中解析論文記錄"""
        results = []
        records = root.findall(f".//{{{self.OAI_NS}}}record")
        for record in records:
            metadata = record.find(f"{{{self.OAI_NS}}}metadata")
            if metadata is None:
                continue

            titles = self._dc_texts(metadata, "title")
            title_zh = titles[0] if titles else ""
            title_en = titles[1] if len(titles) > 1 else ""

            descriptions = self._dc_texts(metadata, "description")
            abstract = descriptions[0] if descriptions else ""

            creators = self._dc_texts(metadata, "creator")
            author = creators[0] if creators else ""
            advisor = creators[1] if len(creators) > 1 else ""

            subjects = self._dc_texts(metadata, "subject")

            date_str = self._dc_text(metadata, "date")
            year_ce = 0
            if date_str:
                match = re.search(r"(\d{4})", date_str)
                if match:
                    year_ce = int(match.group(1))

            identifier = self._dc_text(metadata, "identifier")
            url = identifier if identifier.startswith("http") else ""

            thesis = TaiwanThesis(
                title=title_zh,
                title_en=title_en,
                author=author,
                advisor=advisor,
                school=school,
                department="",
                degree="",
                year_roc=ce_to_roc(year_ce) if year_ce else 0,
                year_ce=year_ce,
                abstract=abstract[:500],
                keywords=subjects,
                url=url,
                source="oai_pmh",
            )
            if thesis.title:
                results.append(thesis)
        return results

    def list_records(
        self,
        school: str,
        from_date: str = None,
        until_date: str = None,
        max_records: int = 50,
    ) -> list[TaiwanThesis]:
        """
        列出指定學校的論文記錄（支援 resumptionToken 分頁）

        Args:
            school: 學校名稱（需在 ENDPOINTS 中）
            from_date: 起始日期（YYYY-MM-DD）
            until_date: 結束日期（YYYY-MM-DD）
            max_records: 最多回傳筆數
        """
        base_url = self.endpoints.get(school)
        if not base_url:
            print(f"  ⚠ 未找到 {school} 的 OAI-PMH 端點", file=sys.stderr)
            return []

        params = {
            "verb": "ListRecords",
            "metadataPrefix": "oai_dc",
        }
        if from_date:
            params["from"] = from_date
        if until_date:
            params["until"] = until_date

        print(f"  查詢 {school} 機構典藏 ...", file=sys.stderr)

        all_results = []
        max_pages = 3  # 最多分頁 3 次，避免記憶體爆炸

        for page in range(max_pages):
            root = self._oai_request(base_url, params)
            if root is None:
                break

            all_results.extend(self._parse_records(root, school))

            # 達到上限就停止
            if len(all_results) >= max_records:
                break

            # 檢查是否有 resumptionToken
            token_el = root.find(f".//{{{self.OAI_NS}}}resumptionToken")
            if token_el is not None and token_el.text:
                params = {"verb": "ListRecords", "resumptionToken": token_el.text}
            else:
                break

        return all_results[:max_records]

    def search_all(
        self,
        schools: list[str] = None,
        from_date: str = None,
        until_date: str = None,
        max_per_school: int = 20,
    ) -> list[TaiwanThesis]:
        """搜尋多所大學的機構典藏"""
        if schools is None:
            schools = list(self.endpoints.keys())

        all_results = []
        for school in schools:
            results = self.list_records(school, from_date, until_date, max_per_school)
            all_results.extend(results)

        return all_results


# ═══════════════════════════════════════════════════════════
# 來源 4：Crossref API（有 DOI 的台灣論文）
# ═══════════════════════════════════════════════════════════

class CrossrefSearch:
    """
    透過 Crossref REST API 搜尋有 DOI 的台灣學位論文
    台灣大學 DOI prefix: 10.6342
    """

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self, mailto: str = ""):
        self.mailto = mailto

    def search(
        self,
        keyword: str,
        rows: int = 20,
        type_filter: str = "dissertation",
    ) -> list[TaiwanThesis]:
        """搜尋 Crossref"""
        params = {
            "query": keyword,
            "rows": rows,
            "filter": f"type:{type_filter}",
        }
        if self.mailto:
            params["mailto"] = self.mailto

        query = urllib.parse.urlencode(params)
        url = f"{self.BASE_URL}?{query}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"AutoResearchClaw/1.0 (mailto:{self.mailto})"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            print(f"  ⚠ Crossref 搜尋失敗：{e}", file=sys.stderr)
            return []

        results = []
        for item in data.get("message", {}).get("items", []):
            titles = item.get("title", [])
            title = titles[0] if titles else ""
            authors = item.get("author", [])
            author_name = f"{authors[0].get('given', '')} {authors[0].get('family', '')}" if authors else ""

            date_parts = item.get("issued", {}).get("date-parts", [[]])
            year_ce = date_parts[0][0] if date_parts and date_parts[0] else 0

            doi = item.get("DOI", "")
            url = f"https://doi.org/{doi}" if doi else ""

            # 判斷是否為台灣論文（DOI prefix 或機構名）
            is_taiwan = doi.startswith("10.6342") or any(
                tw in str(item.get("institution", []))
                for tw in ["Taiwan", "臺灣", "台灣", "National"]
            )
            if not is_taiwan and keyword.lower() not in title.lower():
                continue

            thesis = TaiwanThesis(
                title=title,
                author=author_name.strip(),
                year_ce=year_ce,
                year_roc=ce_to_roc(year_ce) if year_ce else 0,
                doi=doi,
                url=url,
                source="crossref",
            )
            if thesis.title:
                results.append(thesis)

        return results


# ═══════════════════════════════════════════════════════════
# 來源 5：Handle System API
# ═══════════════════════════════════════════════════════════

class HandleResolver:
    """
    透過 Handle.net REST API 解析 NDLTD 論文連結
    NDLTD Handle prefix: 11296
    """

    API_BASE = "https://hdl.handle.net/api/handles"

    @classmethod
    def resolve(cls, handle_or_url: str) -> dict:
        """
        解析 Handle 連結

        Args:
            handle_or_url: Handle ID (11296/xxxxx) 或完整 URL

        Returns:
            {"handle": "11296/xxx", "url": "https://ndltd.ncl.edu.tw/r/xxx"}
        """
        # 從 URL 提取 Handle
        handle = handle_or_url
        if "hdl.handle.net" in handle:
            handle = handle.split("hdl.handle.net/")[-1]
        elif "ndltd.ncl.edu.tw/r/" in handle:
            short = handle.split("/r/")[-1]
            return {"handle": f"11296/{short}", "url": f"https://ndltd.ncl.edu.tw/r/{short}"}

        url = f"{cls.API_BASE}/{handle}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AutoResearchClaw/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

            resolved_url = ""
            for val in data.get("values", []):
                if val.get("type") == "URL":
                    resolved_url = val.get("data", {}).get("value", "")
                    break

            return {"handle": handle, "url": resolved_url}
        except Exception as e:
            print(f"  ⚠ Handle 解析失敗：{e}", file=sys.stderr)
            return {"handle": handle, "url": ""}


# ═══════════════════════════════════════════════════════════
# 統一搜尋入口
# ═══════════════════════════════════════════════════════════

class TaiwanAcademicSearch:
    """統一搜尋入口，整合所有台灣學術論文來源"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.ndltd = NDLTDOpenData()
        self.oai = InstitutionalRepository()
        self.crossref = CrossrefSearch(mailto=self.config.get("crossref_mailto", ""))

    def search(
        self,
        keyword: str,
        school: str = "",
        department: str = "",
        advisor: str = "",
        degree: str = "",
        year_range: tuple = None,
        sources: list[str] = None,
        top_n: int = 50,
    ) -> dict:
        """
        統一搜尋

        Args:
            keyword: 搜尋關鍵字
            school: 學校篩選
            department: 系所篩選
            advisor: 指導教授篩選
            degree: 學位（碩士/博士）
            year_range: (起始年, 結束年)，自動判斷民國/西元
            sources: 指定來源 ["ndltd", "oai", "crossref", "web"]，None=全部
            top_n: 最多回傳筆數

        Returns:
            {"results": [...], "stats": {...}, "search_urls": {...}}
        """
        if sources is None:
            sources = ["ndltd", "oai", "crossref", "web"]

        all_results = []
        stats = {"total": 0, "by_source": {}}

        # 1. NDLTD 開放資料
        if "ndltd" in sources:
            print("🔍 搜尋 NDLTD 開放資料 ...", file=sys.stderr)
            ndltd_results = self.ndltd.search(
                keyword=keyword, school=school, department=department,
                advisor=advisor, degree=degree, year_range=year_range,
                top_n=top_n,
            )
            all_results.extend(ndltd_results)
            stats["by_source"]["ndltd_opendata"] = len(ndltd_results)

        # 2. OAI-PMH 機構典藏
        if "oai" in sources:
            print("🔍 搜尋各大學機構典藏 ...", file=sys.stderr)
            schools_to_search = [school] if school and school in self.oai.endpoints else None
            from_date = f"{year_range[0]}-01-01" if year_range and year_range[0] > 1900 else None
            until_date = f"{year_range[1]}-12-31" if year_range and year_range[1] > 1900 else None
            oai_results = self.oai.search_all(
                schools=schools_to_search, from_date=from_date,
                until_date=until_date, max_per_school=10,
            )
            # 用關鍵字過濾 OAI 結果
            if keyword:
                kw_lower = keyword.lower()
                oai_results = [
                    t for t in oai_results
                    if kw_lower in t.title.lower()
                    or kw_lower in t.title_en.lower()
                    or kw_lower in t.abstract.lower()
                    or any(kw_lower in k.lower() for k in t.keywords)
                ]
            all_results.extend(oai_results)
            stats["by_source"]["oai_pmh"] = len(oai_results)

        # 3. Crossref
        if "crossref" in sources:
            print("🔍 搜尋 Crossref ...", file=sys.stderr)
            cr_results = self.crossref.search(keyword=keyword, rows=min(top_n, 20))
            all_results.extend(cr_results)
            stats["by_source"]["crossref"] = len(cr_results)

        # 4. NDLTD Web 搜尋 URL（不直接抓取，提供連結）
        search_urls = {}
        if "web" in sources:
            search_urls["ndltd_basic"] = NDLTDWebSearch.build_search_url(keyword)
            if " " in keyword or "," in keyword:
                kws = re.split(r"[,\s]+", keyword)
                search_urls["ndltd_advanced"] = NDLTDWebSearch.build_advanced_search_url(kws)

        # 去重（以標題相似度）
        seen_titles = set()
        unique_results = []
        for t in all_results:
            norm_title = re.sub(r"\s+", "", t.title.lower())
            if norm_title and norm_title not in seen_titles:
                seen_titles.add(norm_title)
                unique_results.append(t)

        # 排序：博士 > 碩士，年份新 > 舊
        unique_results.sort(
            key=lambda t: (t.degree == "博士", t.year_ce or t.year_roc + 1911),
            reverse=True,
        )

        stats["total"] = len(unique_results)
        final = unique_results[:top_n]

        return {
            "results": [t.to_dict() for t in final],
            "stats": stats,
            "search_urls": search_urls,
        }

    def generate_report(self, search_result: dict, keyword: str) -> str:
        """生成 Markdown 搜尋報告"""
        results = search_result["results"]
        stats = search_result["stats"]
        urls = search_result.get("search_urls", {})

        lines = [
            f"# 🇹🇼 台灣學術論文搜尋報告",
            f"",
            f"**搜尋關鍵字**：{keyword}",
            f"**搜尋時間**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**搜尋結果**：共 {stats['total']} 篇（去重後）",
            f"",
            f"## 來源分布",
            f"",
        ]

        for source, count in stats.get("by_source", {}).items():
            source_names = {
                "ndltd_opendata": "NDLTD 開放資料",
                "oai_pmh": "大學機構典藏 (OAI-PMH)",
                "crossref": "Crossref (DOI)",
            }
            lines.append(f"- {source_names.get(source, source)}: {count} 篇")

        lines.append("")

        if urls:
            lines.append("## 線上搜尋連結（可在瀏覽器中開啟）")
            lines.append("")
            for name, url in urls.items():
                label = {"ndltd_basic": "NDLTD 基本搜尋", "ndltd_advanced": "NDLTD 進階搜尋"}.get(name, name)
                lines.append(f"- [{label}]({url})")
            lines.append("")

        lines.append("## 搜尋結果")
        lines.append("")

        # 表格
        lines.append("| # | 標題 | 學校 | 系所 | 作者 | 學位 | 年份 | 來源 |")
        lines.append("|---|------|------|------|------|------|------|------|")

        for i, r in enumerate(results, 1):
            title = r["title"][:40] + "..." if len(r["title"]) > 40 else r["title"]
            url = r.get("url") or r.get("handle_url") or ""
            title_link = f"[{title}]({url})" if url else title
            year = r.get("year_ce") or (r.get("year_roc", 0) + 1911) if r.get("year_roc") else ""
            source_emoji = {"ndltd_opendata": "📚", "oai_pmh": "🏛️", "crossref": "🔗"}.get(r.get("source", ""), "")
            lines.append(
                f"| {i} | {title_link} | {r.get('school', '')} | {r.get('department', '')} "
                f"| {r.get('author', '')} | {r.get('degree', '')} | {year} | {source_emoji} |"
            )

        lines.append("")
        lines.append("## 詳細資訊")
        lines.append("")

        for i, r in enumerate(results[:10], 1):  # 前 10 篇詳細
            lines.append(f"### {i}. {r['title']}")
            if r.get("title_en"):
                lines.append(f"*{r['title_en']}*")
            lines.append("")
            if r.get("school"):
                lines.append(f"- **學校**：{r['school']}")
            if r.get("department"):
                lines.append(f"- **系所**：{r['department']}")
            if r.get("author"):
                lines.append(f"- **作者**：{r['author']}")
            if r.get("advisor"):
                lines.append(f"- **指導教授**：{r['advisor']}")
            if r.get("degree"):
                lines.append(f"- **學位**：{r['degree']}")
            year_ce = r.get("year_ce") or (r.get("year_roc", 0) + 1911) if r.get("year_roc") else 0
            year_roc = r.get("year_roc", 0)
            if year_ce:
                lines.append(f"- **年份**：民國 {year_roc} 年（{year_ce}）")
            if r.get("abstract"):
                lines.append(f"- **摘要**：{r['abstract'][:200]}...")
            if r.get("keywords"):
                lines.append(f"- **關鍵字**：{', '.join(r['keywords'])}")
            url = r.get("url") or r.get("handle_url") or ""
            if url:
                lines.append(f"- **連結**：{url}")
            if r.get("doi"):
                lines.append(f"- **DOI**：{r['doi']}")
            lines.append(f"- **來源**：{r.get('source', '')}")
            lines.append("")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="台灣學術論文搜尋 — AutoResearchClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  python taiwan_academic_search.py --keyword "深度學習"
  python taiwan_academic_search.py --keyword "自然語言處理" --school "臺灣大學" --degree 博士
  python taiwan_academic_search.py --keyword "machine learning" --year-range 2020-2025 --output results.json
  python taiwan_academic_search.py --keyword "教育科技" --source ndltd oai --top-n 20
        """,
    )
    parser.add_argument("--keyword", "-k", required=True, help="搜尋關鍵字（中英文皆可）")
    parser.add_argument("--school", "-s", default="", help="學校篩選")
    parser.add_argument("--department", "-d", default="", help="系所篩選")
    parser.add_argument("--advisor", "-a", default="", help="指導教授篩選")
    parser.add_argument("--degree", default="", choices=["碩士", "博士", ""], help="學位類別")
    parser.add_argument("--year-range", "-y", default="", help="年份範圍（如 2020-2025 或 109-112）")
    parser.add_argument("--source", nargs="+", default=None, choices=["ndltd", "oai", "crossref", "web"],
                        help="指定搜尋來源")
    parser.add_argument("--top-n", "-n", type=int, default=50, help="最多回傳筆數（預設 50）")
    parser.add_argument("--output", "-o", default="", help="輸出檔案路徑（.json 或 .md）")
    parser.add_argument("--format", choices=["json", "markdown", "both"], default="markdown",
                        help="輸出格式（預設 markdown）")

    args = parser.parse_args()

    # 解析年份範圍
    year_range = None
    if args.year_range:
        parts = args.year_range.split("-")
        if len(parts) == 2:
            year_range = (int(parts[0]), int(parts[1]))

    # 搜尋
    searcher = TaiwanAcademicSearch()
    result = searcher.search(
        keyword=args.keyword,
        school=args.school,
        department=args.department,
        advisor=args.advisor,
        degree=args.degree,
        year_range=year_range,
        sources=args.source,
        top_n=args.top_n,
    )

    # 輸出
    if args.output:
        output_path = Path(args.output)
        if output_path.suffix == ".json" or args.format == "json":
            output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            report = searcher.generate_report(result, args.keyword)
            output_path.write_text(report, encoding="utf-8")
        print(f"✅ 結果已儲存至 {output_path}", file=sys.stderr)
    else:
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            report = searcher.generate_report(result, args.keyword)
            print(report)


if __name__ == "__main__":
    main()
