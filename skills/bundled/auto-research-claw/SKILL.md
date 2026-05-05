---
name: auto-research-claw
description: |
  全自動學術研究助手：每日論文追蹤、主題深度研究、單篇論文精讀。
  整合國際論文庫（arXiv、HuggingFace DailyPapers）
  與台灣學術資源（NDLTD 博碩士論文、各大學機構典藏 OAI-PMH、Crossref）。
  支援 APA 第七版引用格式（含中文 APA）、結構化筆記生成、知識庫自動維護。
  論文產出支援 15,000-25,000 字長篇學術論文。
trigger_phrases:
  - "今日論文推薦"
  - "過去N天論文"
  - "論文追蹤"
  - "研究 [主題]"
  - "寫一篇關於 [主題] 的論文"
  - "讀一下這篇論文"
  - "搜尋台灣論文"
  - "搜尋博碩士論文"
  - "daily papers"
  - "research [topic]"
  - "write a paper about [topic]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Task
---

# AutoResearchClaw — 全自動學術研究助手

> 整合 [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw)、[dailypaper-skills](https://github.com/huangkiki/dailypaper-skills) 及台灣學術資源，打造一站式研究工作流。

---

## 快速入門

使用者只需說一句話，系統自動判斷模式：

| 觸發語句 | 模式 | 說明 |
|---------|------|------|
| `今日論文推薦` / `過去3天論文` | Mode A | 每日論文追蹤 |
| `研究 [主題]` / `寫一篇關於 X 的論文` | Mode B | 主題深度研究 |
| `讀一下這篇論文 [URL]` | Mode C | 單篇論文精讀 |
| `搜尋台灣論文 [關鍵字]` | Mode T | 台灣博碩士論文專搜 |

---

## Mode A：每日論文追蹤

### 觸發條件
使用者說「今日論文推薦」「過去 N 天論文」「daily papers」「論文追蹤」時啟動。

### 執行流程

依序呼叫三個子技能：

#### Step 1：論文抓取（零 token 消耗）
- **子技能**：`/daily-fetch`
- **執行**：`python scripts/fetch_papers.py --days {N}`
- **來源**：
  - arXiv API（按 `user-config.json` 中的 `arxiv_categories` 和 `keywords`）
  - HuggingFace Daily Papers + Trending
  - **NDLTD 台灣博碩士論文**（按關鍵字搜尋近期論文）⭐
- **打分**：正向關鍵字 +3/+1、負向 -999、領域加分 +1~2、台灣論文額外 +2
- **輸出**：`~/tmp/daily_papers_top30.json`（Windows）或 `/tmp/daily_papers_top30.json`（Linux/Mac）
- **去重**：`.history.json` 30 天內不重複推薦

#### Step 2：AI 點評與分流
- **子技能**：`/daily-review`
- **角色**：資深研究員，具批判精神
- **分流**：🔥 必讀 / 👀 值得看 / ⏭️ 可跳過
- **台灣論文標註**：🇹🇼 標記台灣來源，附上學校/系所/指導教授
- **輸出**：`{DailyPapers}/YYYY-MM-DD-論文推薦.md`

#### Step 3：結構化筆記生成
- **子技能**：`/daily-notes`
- **範圍**：僅為「🔥 必讀」論文生成完整筆記
- **台灣論文**：使用 `thesis-note-template.md`（含指導教授、口試委員、學校系所）
- **國際論文**：使用 `paper-note-template.md`
- **概念萃取**：自動歸類到 20 個概念子目錄
- **品質要求**：>=120 行、>=2 處公式（如有）、>=1 張圖片（如有）
- **MOC 刷新**：自動更新知識庫目錄頁

### 鐵律
1. 「必讀」論文一篇不能少，全部生成筆記
2. 禁止手寫簡化版筆記替代模板
3. 台灣論文不得跳過，需與國際論文同等對待

---

## Mode B：主題深度研究

### 觸發條件
使用者說「研究 [主題]」「write a paper about [topic]」「幫我做 [主題] 的文獻回顧」時啟動。

### 子技能
`/deep-research`

### 論文格式選項

| 格式 | 字數 | 引用風格 | 適用場景 |
|------|------|---------|---------|
| **`apa`**（預設）| **15,000-25,000 字** | APA 7th 中英文混合 | 碩博論文、教育研究 |
| `apa_journal` | 8,000-12,000 字 | APA 7th 中英文混合 | 期刊投稿 |
| `neurips` | 5,000-6,500 字 | 數字引用 [1][2] | CS 頂會 |
| `icml` / `iclr` | 5,000-6,500 字 | 數字引用 [1][2] | CS 頂會（同 conference 變體） |

APA 格式特色：
- 五章結構：緒論→文獻探討→研究方法→結果與討論→結論與建議
- 中文引用：（王大明，2024）/ 英文引用：(Smith, 2024)
- 台灣論文引用：王大明（2024）。《論文標題》〔碩士論文，國立臺灣大學〕。
- 參考文獻 30+ 篇，中文在前（筆劃排序）英文在後（字母排序）

### 8 階段 23 步驟管線

```
Phase A: 研究定義     → [1] 主題初始化 → [2] 問題拆解
Phase B: 文獻探索     → [3] 搜尋策略 → [4] 文獻收集 → [5] 篩選閘門 → [6] 知識萃取
Phase C: 知識合成     → [7] 主題聚類 → [8] 假說生成
Phase D: 實驗設計     → [9] 實驗設計閘門 → [10] 程式碼生成 → [11] 資源規劃
Phase E: 實驗執行     → [12] 執行 → [13] 迭代改進
Phase F: 分析決策     → [14] 結果分析 → [15] 決策（PROCEED/PIVOT/REFINE）
Phase G: 論文撰寫     → [16] 大綱 → [17] 撰稿 → [18] 同儕審查 → [19] 修訂
Phase H: 定稿匯出     → [20] 品質閘門 → [21] 知識歸檔 → [22] 匯出 → [23] 引用驗證
```

### 文獻搜尋來源（Phase B 加強版）⭐

| 來源 | 類型 | 涵蓋範圍 |
|------|------|---------|
| arXiv | 預印本 | 全球，即時（含重試機制） |
| HuggingFace | Daily/Trending Papers | 社群熱門 |
| **NDLTD 開放資料** | 台灣博碩士論文 | 2013-2023，結構化 CSV |
| **NDLTD Web** | 台灣博碩士論文 | 1956-至今，含摘要 |
| **各大學機構典藏** | OAI-PMH 機構典藏 | 台大/清大/成大/交大等 8 校 |
| **Crossref** | DOI 解析 | 有 DOI 的台灣論文 |

### 台灣論文在深度研究中的特殊處理
1. **自動加入搜尋**：Phase B 的搜尋策略自動包含 NDLTD 和機構典藏
2. **中英文雙語搜尋**：同時使用中文和英文關鍵字
3. **學校排名加權**：頂尖大學（台清交成政）論文權重 +1
4. **指導教授網絡**：自動發現同一指導教授的相關論文
5. **文獻回顧專區**：在論文中設專段引用台灣相關研究

### 閘門機制
- **Stage 5**（文獻篩選閘門）：拒絕 → 回到 Stage 4 重新收集
- **Stage 9**（實驗設計閘門）：拒絕 → 回到 Stage 8 重新生成假說
- **Stage 20**（品質閘門）：拒絕 → 回到 Stage 16 重寫論文
- 使用 `--auto-approve` 可跳過人工核准

### 決策迴圈（Stage 15）
- **PROCEED**：繼續到論文撰寫
- **REFINE**：回到 Stage 13，保留假說重跑實驗
- **PIVOT**：回到 Stage 8，重新生成假說（最多 2 次）

### 輸出成品
```
artifacts/{run-id}/
├── stage-1/ ~ stage-23/          # 每步驟輸出
├── paper.tex                     # 會議級 LaTeX
├── paper_draft.md                # Markdown 版論文
├── references.bib                # 真實 BibTeX 引用（含台灣論文）
├── verification_report.json      # 引用驗證報告
├── reviews.md                    # 模擬同儕審查
├── charts/                       # 視覺化圖表
└── deliverables/                 # Overleaf 就緒資料夾
```

---

## Mode C：單篇論文精讀

### 觸發條件
使用者說「讀一下這篇論文」「解析這篇 paper」「幫我讀 [URL/標題]」時啟動。

### 子技能
`/paper-reader`（在獨立 fork 中運行）

### 支援來源
- arXiv URL / PDF 連結
- DOI / Crossref 連結
- **NDLTD 論文連結**（`ndltd.ncl.edu.tw/r/xxx` 或 `hdl.handle.net/11296/xxx`）⭐
- **各大學機構典藏連結** ⭐
- 本地 PDF 檔案路徑

### 閱讀模式

| 模式 | 觸發 | 輸出深度 |
|------|------|---------|
| 快速摘要 | 「簡單看一下」 | 50 行，核心貢獻 + 一句話總結 |
| 完整解析 | 預設模式 | 120+ 行，全面結構化筆記 |
| 批判分析 | 「批判分析」 | 150+ 行，含詳細優缺點和改進建議 |
| 知識提取 | 「提取概念」 | 聚焦在術語、概念和方法論連結 |

### 台灣論文精讀增強 ⭐
- 自動辨識 NDLTD 連結，使用 `thesis-note-template.md`
- 補充欄位：學校/系所/指導教授/口試委員/學位類別
- 自動搜尋同校同系所相關論文
- 民國年自動轉換西元年

---

## Mode T：台灣論文專搜

### 觸發條件
使用者說「搜尋台灣論文 [關鍵字]」「搜尋博碩士論文 [關鍵字]」「找台灣的研究」時啟動。

### 搜尋能力

```python
# 執行腳本
python scripts/taiwan_academic_search.py --keyword "深度學習" --school "臺灣大學" --year-range 2020-2025

# 支援參數
--keyword     關鍵字（支援中英文、布林邏輯 AND/OR）
--school      學校篩選（支援多校）
--department  系所篩選
--advisor     指導教授
--degree      學位類別（碩士/博士）
--year-range  年份範圍（自動處理民國/西元）
--source      指定來源（ndltd/oai/crossref/web）
--top-n       最多回傳幾篇（預設 50）
```

### 搜尋來源與方法

| 來源 | 方法 | 欄位涵蓋 | 年份範圍 |
|------|------|---------|---------|
| NDLTD 開放資料 | CSV 下載 + 本地搜尋 | 標題、學校、系所、作者、指導教授、學位 | 2013-2023 |
| NDLTD Web | Web 搜尋（含摘要） | 全部欄位含摘要、關鍵字 | 1956-至今 |
| Handle System | API 解析永久連結 | 連結解析 | 不限 |
| 各大學 OAI-PMH | DSpace 標準協議 | Dublin Core 元資料 | 依各校 |
| Crossref | REST API | 有 DOI 的論文 | 不限 |

### 台灣頂尖大學機構典藏 OAI-PMH 端點 ⭐

| 學校 | OAI-PMH 端點 | 說明 |
|------|-------------|------|
| 臺灣大學 | `https://tdr.lib.ntu.edu.tw/oai/request` | DSpace |
| 清華大學 | `https://etd.lib.nthu.edu.tw/oai/request` | DSpace |
| 成功大學 | `https://etds.lib.ncku.edu.tw/oai/request` | DSpace |
| 陽明交通大學 | `https://etd.lib.nycu.edu.tw/oai/request` | DSpace |
| 政治大學 | `https://thesis.lib.nccu.edu.tw/oai/request` | DSpace |
| 中央大學 | `https://ir.lib.ncu.edu.tw/oai/request` | DSpace |
| 中山大學 | `https://etd.lib.nsysu.edu.tw/oai/request` | DSpace |
| 臺灣師範大學 | `https://etds.lib.ntnu.edu.tw/oai/request` | DSpace |

### 輸出格式
- Markdown 報告（含論文清單、摘要、連結）
- JSON 結構化資料
- 可直接匯入 Obsidian 知識庫

---

## 配置

### 首次使用設定

1. 複製並編輯配置檔：
```bash
cp skills/auto-research-claw/config/user-config.json \
   skills/auto-research-claw/config/user-config.local.json
# 編輯 user-config.local.json 設定你的路徑和關鍵字
```

2. 設定環境變數（深度研究模式需要）：
```bash
export OPENAI_API_KEY="sk-..."          # 或其他 OpenAI 相容 API
export OPENAI_BASE_URL="https://..."    # 可選，用於 DeepSeek 等
```

### 配置檔說明
- `config/user-config.json`：預設配置（勿直接修改）
- `config/user-config.local.json`：使用者自訂覆蓋（git ignore）
- `config/prompts.yaml`：LLM 提示詞模板（placeholder 由 `prompt_loader.py` 展開）

### 配置驗證
```bash
# 驗證設定檔格式和必要欄位
python scripts/prompt_loader.py
```
驗證項目：必要路徑、關鍵字、arXiv 類別、台灣來源設定、論文格式、LLM 模型。

### 關鍵配置項

```json
{
  "paths": {
    "obsidian_vault": "~/ObsidianVault",
    "paper_notes_folder": "論文筆記",
    "daily_papers_folder": "DailyPapers",
    "concepts_folder": "_概念",
    "artifacts_folder": "artifacts"
  },
  "daily_papers": {
    "keywords": ["transformer", "diffusion", "LLM"],
    "negative_keywords": ["medical"],
    "arxiv_categories": ["cs.AI", "cs.LG", "cs.CV"],
    "top_n": 30,
    "include_taiwan_theses": true
  },
  "taiwan": {
    "enabled": true,
    "keywords_zh": ["深度學習", "自然語言處理", "電腦視覺"],
    "degree_filter": ["碩士", "博士"],
    "bonus_score": 2,
    "top_schools": ["臺灣大學", "清華大學", "成功大學"]
  },
  "deep_research": {
    "paper_format": "apa",
    "paper_format_options": {
      "apa": "APA 7th 完整版（15,000-25,000字，碩博論文）",
      "apa_journal": "APA 7th 精簡版（8,000-12,000字，期刊投稿）",
      "neurips": "NeurIPS 會議格式（5,000-6,500字）"
    }
  },
  "llm": {
    "provider": "openai_compatible",
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com",
    "fallback_models": ["gpt-4o", "gpt-5.4"]
  }
}
```

---

## 依賴

### 必要
- Python 3.11+
- Claude Code（CLI 環境）

### Python 套件
```bash
pip install pyyaml rich arxiv numpy httpx
```

### 可選
- `scholarly`：Google Scholar 搜尋
- `PyMuPDF`：PDF 全文萃取
- `matplotlib`：圖表生成
- `beautifulsoup4`：Web Scraping（台灣論文進階搜尋）
- `lxml`：OAI-PMH XML 解析

---

## 檔案結構

```
auto-research-claw/
├── SKILL.md                          # 本檔案（主入口）
├── requirements.txt                  # Python 依賴清單
├── config/
│   ├── user-config.json              # 預設配置
│   ├── user-config.local.json        # 使用者覆蓋（gitignore）
│   └── prompts.yaml                  # LLM 提示詞模板
├── scripts/
│   ├── fetch_papers.py               # 多來源論文抓取（國際+台灣）含打分去重、重試機制
│   ├── taiwan_academic_search.py     # 台灣學術論文搜尋模組（NDLTD/OAI-PMH/Crossref）
│   ├── moc_builder.py               # 知識庫目錄頁生成
│   └── prompt_loader.py             # 提示詞載入器 + 設定檔驗證工具
├── templates/
│   ├── paper-note-template.md        # 國際論文筆記模板
│   ├── thesis-note-template.md       # 台灣博碩士論文筆記模板
│   └── daily-report-template.md      # 每日推薦報告模板
├── references/
│   ├── concept-categories.md         # 概念分類規則（20 類）
│   ├── quality-standards.md          # 筆記品質規範
│   └── taiwan-sources.md             # 台灣學術來源完整指南
└── sub-skills/
    ├── daily-fetch/SKILL.md          # Mode A Step 1
    ├── daily-review/SKILL.md         # Mode A Step 2
    ├── daily-notes/SKILL.md          # Mode A Step 3
    ├── deep-research/SKILL.md        # Mode B 完整管線
    └── paper-reader/SKILL.md         # Mode C 單篇精讀
```

---

## 故障排除

| 問題 | 解法 |
|------|------|
| NDLTD 開放資料下載失敗 | 檢查 `https://ndltd.ncl.edu.tw/opendata/` 是否可存取 |
| arXiv API 回傳空結果 | 增加 `since_days`、改用 OR 邏輯、擴展關鍵字 |
| 台灣論文搜不到 | 嘗試使用不同中文同義詞，或直接用 NDLTD Web 搜尋 |
| LLM API 401 錯誤 | 檢查 `OPENAI_API_KEY` 和 `base_url` 是否正確 |
| OAI-PMH 逾時 | 某些大學端點可能暫時不可用，會自動跳過 |
| 筆記品質不達標 | 系統會自動刪除重來，最多重試 3 次 |

---

## 致謝

本技能整合自：
- [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw) — 全自動研究管線核心
- [dailypaper-skills](https://github.com/huangkiki/dailypaper-skills) — 每日論文追蹤與 Obsidian 整合
- 台灣國家圖書館 NDLTD 開放資料 — 博碩士論文知識加值系統
