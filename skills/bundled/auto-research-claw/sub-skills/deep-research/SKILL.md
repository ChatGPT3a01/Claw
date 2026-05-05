---
name: deep-research
description: |
  主題深度研究 — 從想法到論文的全自動管線。
  23 個步驟、8 個階段，涵蓋文獻探索、假說生成、實驗設計與執行、
  論文撰寫與同儕審查。整合台灣博碩士論文作為文獻來源。
trigger_phrases:
  - "研究 [主題]"
  - "write a paper about"
  - "寫一篇關於 [主題] 的論文"
  - "幫我做文獻回顧"
  - "research [topic]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Task
---

# deep-research — 主題深度研究（從想法到論文）

> Chat an Idea. Get a Paper. 🎯

## 觸發條件
使用者說「研究 [主題]」「寫一篇關於 X 的論文」「幫我做文獻回顧」時啟動。

## 核心管線：8 階段 23 步驟

### Phase A：研究定義（Stage 1-2）

**[1] TOPIC_INIT — 主題初始化**
- 將使用者的模糊想法轉化為明確的研究問題
- 產出：RQ1/RQ2/RQ3、中英文關鍵字、搜尋策略
- 提示詞：`prompts.yaml → topic_init`

**[2] PROBLEM_DECOMPOSE — 問題拆解**
- 將研究問題拆解為可執行的子問題
- 識別所需的資料、方法和工具

### Phase B：文獻探索（Stage 3-6）⭐ 含台灣論文

**[3] SEARCH_STRATEGY — 搜尋策略**
- 設計多來源搜尋查詢：
  - arXiv（國際預印本）
  - **NDLTD 台灣博碩士論文**（中文關鍵字）⭐
  - **各大學 OAI-PMH 機構典藏** ⭐
  - Crossref（有 DOI 的台灣論文）
- 布林邏輯組合 + 時間範圍

**[4] LITERATURE_COLLECT — 文獻收集**
- 並行查詢所有來源
- 台灣論文搜尋：
  ```bash
  python scripts/taiwan_academic_search.py --keyword "{中文關鍵字}" --top-n 20
  ```
- 合併去重

**[5] LITERATURE_SCREEN — 文獻篩選 [⛩️ 閘門]**
- AI 評估每篇文獻的相關性（1-5 分）
- 台灣論文以 🇹🇼 標記
- **閘門**：需人工核准篩選結果
  - ✅ 通過 → 繼續
  - ❌ 拒絕 → 回滾到 Stage 4 重新收集

**[6] KNOWLEDGE_EXTRACT — 知識萃取**
- 從篩選通過的文獻中萃取關鍵資訊
- 建立文獻矩陣（作者、年份、方法、結果、貢獻）

### Phase C：知識合成（Stage 7-8）

**[7] SYNTHESIS — 主題聚類**
- 將萃取的知識按主題聚類
- 識別研究缺口和趨勢

**[8] HYPOTHESIS_GEN — 假說生成**
- 使用多智能體辯論機制：
  - Agent A：支持角度
  - Agent B：反對角度
  - Agent C：綜合判斷
- 生成 2-3 個可驗證的研究假說
- 提示詞：`prompts.yaml → hypothesis_gen`

### Phase D：實驗設計（Stage 9-11）

**[9] EXPERIMENT_DESIGN — 實驗設計 [⛩️ 閘門]**
- 設計實驗方案、指標、基線
- **閘門**：需人工核准
  - ✅ 通過 → 繼續
  - ❌ 拒絕 → 回滾到 Stage 8 重新生成假說

**[10] CODE_GENERATION — 程式碼生成**
- 生成真實、可執行的實驗程式碼
- 提示詞：`prompts.yaml → code_generation`
- **反模式清單**（禁止）：
  - 隨機數偽造結果
  - 硬編碼預期結果
  - 跳過實際計算

**[11] RESOURCE_PLANNING — 資源規劃**
- 評估所需 GPU/CPU/記憶體
- 選擇執行模式（sandbox/docker/ssh/colab）

### Phase E：實驗執行（Stage 12-13）

**[12] EXPERIMENT_RUN — 實驗執行**
- 在所選環境中執行程式碼
- 監控進度、收集指標
- 偵測 NaN/Inf/除以零等異常

**[13] ITERATIVE_REFINE — 迭代改進**
- 基於結果自動改進程式碼
- 最多 10 輪迭代（由 `user-config.json → max_iterative_refine` 控制）
- 自我修復流程：
  1. 偵測實驗失敗或異常（NaN/Inf/crash/指標不合理）
  2. Claude agent 診斷錯誤原因
  3. 自動修改程式碼並重跑
  4. 若連續 3 輪無改善 → 提前終止並進入 Stage 14

### Phase F：分析與決策（Stage 14-15）

**[14] RESULT_ANALYSIS — 結果分析**
- 統計分析實驗結果
- 自動生成視覺化圖表

**[15] RESEARCH_DECISION — 研究決策**
- 基於結果做出決策：
  - **PROCEED**：結果支持假說 → 繼續到論文撰寫
  - **REFINE**：結果部分支持 → 回到 Stage 13 改進實驗
  - **PIVOT**：結果不支持 → 回到 Stage 8 重新生成假說（最多 2 次）

### Phase G：論文撰寫（Stage 16-19）

**[16] PAPER_OUTLINE — 論文大綱**
- 生成論文結構大綱
- 分配每節預計字數

**[17] PAPER_DRAFT — 論文撰稿**
- 依 `paper_format` 設定選擇格式與字數：

| 格式 | 字數 | 引用風格 | 適用場景 |
|------|------|---------|---------|
| `apa` | **15,000-25,000 字** | APA 7th（中英文混合） | 碩博論文、教育研究 |
| `apa_journal` | **8,000-12,000 字** | APA 7th（中英文混合） | 期刊投稿 |
| `neurips` | 5,000-6,500 字 | 數字引用 [1][2] | CS 頂會 |
| `icml` / `iclr` | 5,000-6,500 字 | 數字引用 [1][2] | CS 頂會 |

- **APA 格式特色** ⭐：
  - 五章結構：緒論→文獻探討→研究方法→結果與討論→結論與建議
  - 中文文內引用：（王大明，2024）、英文：(Smith, 2024)
  - 台灣論文引用：王大明（2024）。《論文標題》〔碩士論文，國立臺灣大學〕。臺灣博碩士論文知識加值系統。
  - 參考文獻 30+ 篇，中文在前（筆劃排序）英文在後（字母排序）
  - 統計數據報告效果量（Cohen's d, η²）
- 提示詞：`prompts.yaml → paper_draft`
- **台灣文獻引用**：在文獻探討中適當引用台灣相關研究
- 所有數據必須來自真實實驗結果

**[18] PEER_REVIEW — 同儕審查模擬**
- 雙審稿人制度
- 評審維度：新穎性、嚴謹性、充分性、寫作品質
- 提示詞：`prompts.yaml → peer_review`

**[19] PAPER_REVISION — 論文修訂**
- 根據審查意見修訂
- **鐵律**：只能擴展和改進，禁止縮短已有內容

### Phase H：定稿與匯出（Stage 20-23）

**[20] QUALITY_GATE — 品質閘門 [⛩️ 閘門]**
- 最終品質檢查
- **閘門**：需人工核准
  - ✅ 通過 → 繼續
  - ❌ 拒絕 → 回滾到 Stage 16 重寫論文

**[21] KNOWLEDGE_ARCHIVE — 知識歸檔**
- 將研究過程中的教訓存入進化系統
- 可供未來執行參考

**[22] EXPORT_PUBLISH — 匯出**
- 生成 LaTeX（可直接上傳 Overleaf）
- 生成 Markdown 版本
- 自動生成圖表

**[23] CITATION_VERIFY — 引用驗證**
- **5 層驗證**：
  1. arXiv ID 驗證
  2. DOI 驗證（含台灣論文 DOI）
  3. **Handle 驗證**（台灣 NDLTD 論文 `11296/xxxxx`）⭐
  4. WebSearch 標題驗證
  5. LLM 相關性評分（最後手段）
- 提示詞：`prompts.yaml → citation_verify`

## 輸出成品

```
artifacts/{run-id}/
├── stage-1/ ~ stage-23/          # 每步驟輸出
├── stage-10/experiment.py         # 實驗程式碼
├── stage-12/runs/                 # 實驗結果
├── stage-14/experiment_summary.json
├── stage-14/results_table.tex
├── stage-17/paper_draft.md        # 完整論文草稿
├── paper.tex                      # 會議級 LaTeX
├── references.bib                 # BibTeX（含台灣論文引用）
├── verification_report.json       # 引用驗證報告
├── reviews.md                     # 模擬審查意見
├── charts/                        # 視覺化圖表
└── deliverables/                  # Overleaf 就緒資料夾
```

## 快速開始

在 Claude Code 中直接用自然語言觸發：

```
研究 教育科技中的自適應學習          → 完整 23 步驟管線（預設 APA 格式）
研究 深度學習 --格式 neurips          → CS 會議格式
幫我做 學習分析 的文獻回顧            → 只跑到 Phase C 停止
寫一篇關於 AI教育 的論文              → 完整論文產出
```

## 配置選項

```json
{
  "deep_research": {
    "experiment_mode": "sandbox",     // sandbox/docker/ssh/colab
    "auto_approve": false,            // 跳過閘門人工核准
    "max_pivot": 2,                   // 最多換 2 次假說
    "max_iterative_refine": 10,       // 實驗最多迭代 10 輪
    "paper_format": "apa",            // apa/apa_journal/neurips/icml/iclr
    "citation_verify": true,          // 啟用引用驗證
    "include_taiwan_literature": true  // 包含台灣文獻
  }
}
```
