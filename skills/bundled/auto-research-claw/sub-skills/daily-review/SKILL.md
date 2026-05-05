---
name: daily-review
description: |
  每日論文 AI 點評與分流。
  讀取抓取結果，以資深研究員角色為每篇論文判定分流標籤，
  生成帶態度的推薦點評，台灣論文以 🇹🇼 標記。
trigger_phrases:
  - "論文點評"
  - "review papers"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch
---

# daily-review — 每日論文點評與分流

## 觸發條件
- 使用者說「論文點評」
- 被 `/daily-papers` 主入口自動呼叫（Step 2）

## 前置條件
- `~/tmp/daily_papers_top30.json`（Windows）或 `/tmp/daily_papers_top30.json`（Linux/Mac）必須存在（由 daily-fetch 產出）

## 執行步驟

### 1. 讀取候選論文
```python
import json, os, sys
from pathlib import Path
tmp_dir = Path.home() / "tmp" if sys.platform == "win32" else Path("/tmp")
papers = json.load(open(tmp_dir / "daily_papers_top30.json"))["papers"]
```

### 2. 掃描已有筆記庫（建立索引）
掃描 Obsidian 筆記庫，匹配候選論文與已有筆記，避免重複推薦已讀論文。

### 3. AI 點評
使用 `config/prompts.yaml` 中的 `daily_review` 提示詞。

**角色設定**：
- 資深研究員，有態度有觀點
- 看到創新要誠實讚賞，看到灌水也要直說
- **鐵律**：基於事實評價，禁止編造論文沒有的缺陷

**分流標籤**：
- 🔥 **必讀**：重大突破、高影響力、與研究直接相關
- 👀 **值得看**：有趣但非核心、方法新穎值得了解
- ⏭️ **可跳過**：增量改進、與研究不相關、品質不足

**台灣論文處理**：
- 以 🇹🇼 標記
- 附上學校/系所/指導教授
- 與國際論文同等標準評審，不因出處而加分或扣分

### 4. 輸出格式

#### Markdown 報告結構
```markdown
# 📰 YYYY-MM-DD 論文推薦

## 分流總覽
| # | 判決 | 標題 | 來源 | 分數 | 一句話評價 |
|---|------|------|------|------|-----------|
| 1 | 🔥 | Paper Title | arXiv | 8.5 | 方法創新，效果顯著 |
| 2 | 🇹🇼🔥 | 論文標題 | NDLTD | 7.0 | 台大碩論，紮實的實證研究 |
| 3 | 👀 | Another Paper | HF | 5.0 | 有趣但缺少消融實驗 |
...

## 🔥 必讀（N 篇）
### 1. Paper Title
**來源**: arXiv:2403.xxxxx | **分數**: 8.5
**作者**: Author1, Author2
> 兩三句具體評語...

### 2. 🇹🇼 論文標題
**來源**: NDLTD | **學校**: 國立臺灣大學 資訊工程學系 | **指導教授**: 某教授
> 兩三句具體評語...

## 👀 值得看（N 篇）
...

## ⏭️ 可跳過（N 篇）
...
```

### 5. 儲存
```
{obsidian_vault}/{DailyPapers}/YYYY-MM-DD-論文推薦.md
```

### 6. 更新歷史記錄
更新 `.history.json` 做跨天去重。

## 品質要求

> 完整品質規範詳見 `references/quality-standards.md`

- 每篇論文都必須有判決標籤，不得遺漏
- 每篇至少 2 句具體評語（正面或負面皆可，但必須有理有據）
- 禁止泛泛之詞如「很有趣」「值得一看」（需具體說明為什麼）
- 台灣論文必須標註 🇹🇼 並附學校資訊
- 分流表和詳細點評的論文清單必須完全一致
