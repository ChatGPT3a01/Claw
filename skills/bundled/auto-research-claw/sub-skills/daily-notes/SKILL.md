---
name: daily-notes
description: |
  為每日「必讀」論文生成結構化筆記，自動維護概念庫和目錄頁。
  國際論文使用 paper-note-template，台灣博碩士論文使用 thesis-note-template。
trigger_phrases:
  - "生成論文筆記"
  - "generate notes"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Task
---

# daily-notes — 結構化筆記生成

## 觸發條件
- 使用者說「生成論文筆記」
- 被 `/daily-papers` 主入口自動呼叫（Step 3）

## 前置條件
- 當日推薦報告已存在（由 daily-review 產出）
- 推薦報告中有「🔥 必讀」論文

## 執行步驟

### Step 1：補充概念庫
1. 掃描當日推薦報告，提取所有 `[[概念]]` wikilink 和 `method_names`
2. 對每個新概念：
   - 依據 `references/concept-categories.md` 歸類到 20 個子目錄之一
   - 如該概念筆記不存在，建立概念筆記
   - 如已存在，追加新的相關論文連結

### Step 2：為「必讀」論文生成筆記
對每篇 🔥 必讀論文：

#### 國際論文（arXiv / HuggingFace）
1. 取得論文全文（優先 arXiv HTML → PDF 解析）
2. 使用 `templates/paper-note-template.md` 模板
3. 使用 `config/prompts.yaml` 中的 `daily_notes` 提示詞
4. **可用 fork 模式** (`context: fork`) 並行處理多篇論文

#### 台灣博碩士論文 🇹🇼
1. 取得論文資訊（NDLTD 頁面 / Handle 解析）
2. 使用 `templates/thesis-note-template.md` 模板
3. 填入台灣特有欄位：
   - 學校全稱 / 系所 / 學位類別
   - 指導教授 / 口試委員
   - 民國年與西元年對照
   - NDLTD 永久連結
4. 如有全文 PDF，進行深度解析

### Step 3：品質驗證
每篇筆記必須通過以下檢查（參見 `references/quality-standards.md`）：

| 指標 | 國際論文 | 台灣論文 |
|------|---------|---------|
| 總行數 | >= 120 行 | >= 100 行 |
| LaTeX 公式 | >= 2 處 | >= 1 處（如有） |
| 圖片 | >= 1 張 | 不強制 |
| 必含章節 | 全部 | 全部 |
| wikilink | >= 3 個 | >= 2 個 |

**不達標處理**：刪除該筆記，重新生成（最多 3 次）。

### Step 4：連結回填
將生成的筆記檔名回填到當日推薦報告中，修正 wikilink。

### Step 5：刷新 MOC 目錄頁
```bash
python skills/auto-research-claw/scripts/moc_builder.py
```
- 遞迴掃描論文筆記目錄和概念目錄
- 自動生成帶 wikilink 的索引頁
- 內容沒變的檔案不重寫（幂等操作）

## 圖片取得策略（多路 fallback）

```
嘗試 1：arXiv HTML 版 (ar5iv.labs.arxiv.org) 直接提取 <img>
    ↓ 失敗
嘗試 2：論文專案主頁 / GitHub Repo 找 figures
    ↓ 失敗
嘗試 3：PDF 萃取 (PyMuPDF pdfimages)
    ↓ 失敗
fallback：用文字描述替代，標註 [圖片未取得]
```

## 鐵律

1. **「必讀」論文一篇不能少**，全部生成筆記
2. **禁止手寫簡化版**替代模板
3. **台灣論文不得跳過**，需與國際論文同等對待
4. **概念庫必須更新**，不可跳過 Step 1
5. **MOC 必須刷新**，不可跳過 Step 5

## 輸出位置

```
{obsidian_vault}/
├── {paper_notes_folder}/
│   ├── {分類}/
│   │   ├── 論文筆記1.md      ← 國際論文
│   │   └── 🇹🇼論文筆記2.md   ← 台灣論文
│   └── _概念/
│       ├── 1-生成模型/
│       ├── 2-強化學習/
│       └── ...
└── {daily_papers_folder}/
    └── YYYY-MM-DD-論文推薦.md  ← 回填連結後
```
