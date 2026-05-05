---
name: daily-fetch
description: |
  每日論文抓取（零 token 消耗）。
  從 arXiv、HuggingFace、NDLTD 台灣博碩士論文等多來源抓取論文，
  按關鍵字打分篩選，輸出 Top N 候選清單。
trigger_phrases:
  - "論文抓取"
  - "跑一下論文抓取"
  - "fetch papers"
allowed-tools: Bash, Read, Glob
---

# daily-fetch — 每日論文抓取

## 觸發條件
- 使用者說「論文抓取」「跑一下論文抓取」
- 被 `/daily-papers` 主入口自動呼叫（Step 1）

## 執行步驟

### 1. 讀取配置
```bash
# 配置路徑（優先讀 local，回退 default）
CONFIG_DIR="skills/auto-research-claw/config"
CONFIG="$CONFIG_DIR/user-config.local.json"
[ ! -f "$CONFIG" ] && CONFIG="$CONFIG_DIR/user-config.json"
```

### 2. 執行抓取腳本
```bash
python skills/auto-research-claw/scripts/fetch_papers.py \
  --days {DAYS} \
  --config "$CONFIG" \
  --include-taiwan \
  --output "$HOME/tmp/daily_papers_top30.json"
```

**參數說明**：
- `--days N`：抓取最近 N 天（預設 1，使用者說「過去 3 天」則用 3）
- `--include-taiwan`：包含 NDLTD 台灣論文（預設啟用）
- `--no-taiwan`：不包含台灣論文
- `--top-n N`：保留前 N 篇（預設 30）
- `--categories cs.AI cs.LG`：指定 arXiv 類別

### 3. 驗證輸出
```bash
# 確認輸出檔案存在且非空
python -c "
import json, sys
import os; data = json.load(open(os.path.expanduser('~/tmp/daily_papers_top30.json')))
print(f'✅ 抓取完成：{data[\"top_n\"]} 篇候選論文')
print(f'   來源：arXiv={sum(1 for p in data[\"papers\"] if p[\"source\"]==\"arxiv\")}')
print(f'   HuggingFace={sum(1 for p in data[\"papers\"] if \"huggingface\" in p[\"source\"])}')
print(f'   🇹🇼 NDLTD={sum(1 for p in data[\"papers\"] if p[\"is_taiwan\"])}')
"
```

### 4. 輸出
- 主輸出：Windows `~/tmp/daily_papers_top30.json`、Linux/Mac `/tmp/daily_papers_top30.json`
- 此步驟 **零 token 消耗**，全部由 Python 完成

## 輸出格式
```json
{
  "date": "2026-03-31",
  "days": 1,
  "total_fetched": 150,
  "after_dedup": 95,
  "top_n": 30,
  "papers": [
    {
      "title": "...",
      "authors": ["..."],
      "abstract": "...",
      "url": "...",
      "arxiv_id": "...",
      "source": "arxiv",
      "score": 7.0,
      "is_taiwan": false,
      "extra": {}
    }
  ]
}
```

## 台灣論文額外欄位
```json
{
  "is_taiwan": true,
  "source": "ndltd",
  "extra": {
    "school": "國立臺灣大學",
    "department": "資訊工程學系",
    "advisor": "某教授",
    "degree": "碩士",
    "year_roc": 112
  }
}
```

## 錯誤處理
- arXiv API 超時：自動重試最多 2 次，每次間隔 5 秒（fetch_papers.py 內建）
- HuggingFace API 失敗：跳過，不影響其他來源
- NDLTD 下載失敗：跳過該年份，繼續其他年份
- 所有來源都失敗：輸出空列表，報告錯誤
