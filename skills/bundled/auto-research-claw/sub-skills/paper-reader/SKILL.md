---
name: paper-reader
description: |
  單篇論文深度精讀助手。支援 arXiv、DOI/Crossref、NDLTD 台灣博碩士論文。
  生成結構化筆記，自動維護概念庫。
context: fork
trigger_phrases:
  - "讀一下這篇論文"
  - "解析這篇 paper"
  - "幫我讀"
  - "read this paper"
  - "論文精讀"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
---

# paper-reader — 單篇論文精讀

> 在獨立 fork 中運行（`context: fork`），不佔主 agent 上下文。

## 觸發條件
- 使用者說「讀一下這篇論文 [URL/標題]」
- 使用者說「解析這篇 paper」「論文精讀」
- 被 daily-notes 呼叫處理「必讀」論文

## 支援的輸入格式

| 輸入類型 | 範例 | 處理方式 |
|---------|------|---------|
| arXiv URL | `arxiv.org/abs/2403.xxxxx` | 取 arXiv HTML + PDF |
| arXiv ID | `2403.xxxxx` | 同上 |
| DOI | `10.xxxx/xxxxx` | Crossref 解析 |
| **NDLTD URL** | `ndltd.ncl.edu.tw/r/xxxxx` | Handle 解析 + 頁面萃取 ⭐ |
| **Handle URL** | `hdl.handle.net/11296/xxxxx` | Handle API 解析 ⭐ |
| 本地 PDF | `/path/to/paper.pdf` | PyMuPDF 萃取 |
| 論文標題 | 「Attention Is All You Need」 | 搜尋引擎找全文 |

## 閱讀模式

| 模式 | 觸發 | 輸出行數 | 適用場景 |
|------|------|---------|---------|
| **快速摘要** | 「簡單看一下」「快速摘要」 | ~50 行 | 快速篩選 |
| **完整解析** | 預設模式 | 120+ 行 | 詳細理解 |
| **批判分析** | 「批判分析」「review this」 | 150+ 行 | 深度評價 |
| **知識提取** | 「提取概念」「extract」 | ~80 行 | 概念網建構 |

## 執行流程

### 1. 辨識輸入來源
```
輸入 URL/標題
    │
    ├── 含 arxiv.org → arXiv 論文
    ├── 含 ndltd.ncl.edu.tw 或 hdl.handle.net/11296 → 台灣博碩士論文 🇹🇼
    ├── 含 doi.org → DOI 解析
    ├── 含 .pdf → 本地 PDF
    └── 其他 → WebSearch 搜尋
```

### 2. 取得論文全文

#### 國際論文
```
arXiv HTML (ar5iv.labs.arxiv.org)
    ↓ 失敗
arXiv PDF → PyMuPDF 萃取
    ↓ 失敗
Crossref API 取元資料（透過 DOI）
    ↓ 失敗
WebSearch 搜尋全文
```

#### 台灣博碩士論文 🇹🇼
```
NDLTD 短連結解析 → 論文詳情頁
    ↓
Handle API 取永久 URL
    ↓
論文頁面萃取元資料（標題、摘要、關鍵字、學校、系所、指導教授）
    ↓
如有全文 PDF 連結 → 下載並萃取
    ↓ 無全文
基於摘要和元資料生成筆記（標註「全文未公開」）
```

### 3. 選擇模板
- 國際論文 → `templates/paper-note-template.md`
- 台灣博碩士論文 → `templates/thesis-note-template.md`

### 4. 生成筆記

#### 國際論文筆記包含
- 元資訊（作者、機構、會議、連結）
- 一句話總結
- 核心貢獻（3 點）
- 問題背景（問題、局限、動機）
- 方法詳解（架構圖 + 核心模組）
- 關鍵公式（LaTeX，含符號說明）
- 關鍵圖表（圖片 + 分析）
- 實驗（資料集、實現、結果、消融）
- 批判性思考（優點、局限、改進、可複現性）
- 關聯筆記（基於、對比、方法相關）
- 速查卡片

#### 台灣論文筆記額外包含 🇹🇼
- 學校全稱 / 系所 / 學位類別
- 指導教授 / 口試委員
- 民國年與西元年對照
- NDLTD 永久連結 / Handle URL
- 中英文摘要
- 研究設計與方法論
- 同指導教授其他論文連結
- 同校同系所相關研究

### 5. 品質檢查

| 指標 | 國際論文 | 台灣論文 |
|------|---------|---------|
| 行數 | >= 120 | >= 100 |
| 公式 | >= 2 | >= 1（如有） |
| 圖片 | >= 1 | 不強制 |
| wikilink | >= 3 | >= 2 |

不通過 → 刪除重來（最多 3 次）

### 6. 概念萃取
- 從筆記中提取 `[[概念]]` wikilink
- 依據 `references/concept-categories.md` 歸類
- 建立或更新概念筆記

### 7. 輸出
```
{obsidian_vault}/{paper_notes_folder}/{分類}/筆記標題.md
```

## 台灣論文特殊處理 🇹🇼

### 民國年轉換
自動偵測並轉換：
- 輸入「民國 112 年」→ 顯示「民國 112 年（2023）」
- 論文系統 ID 如 `112NTU5090001` → 自動解析為 2023 年台大論文

### 搜尋同系所論文
自動搜尋同一指導教授、同一系所的相關論文：
```bash
python scripts/taiwan_academic_search.py --advisor "{指導教授}" --school "{學校}" --top-n 5
```

### NDLTD 連結格式
- 短連結：`https://ndltd.ncl.edu.tw/r/{code}`
- Handle：`https://hdl.handle.net/11296/{code}`
- 系統 ID URL：`https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi?o=dnclcdr&s=id%3D%22{id}%22`

## 錯誤處理
- URL 無法存取：嘗試 WebSearch 搜尋替代來源
- PDF 萃取失敗：基於摘要生成簡化筆記，標註「全文萃取失敗」
- NDLTD 被 CAPTCHA 阻擋：使用 Handle API 取基本資訊，附上手動查詢 URL
- 圖片全部取不到：用文字描述替代，不因此降低筆記品質
