---
name: md-to-pdf
description: >
  [已整併] 此技能已併入 markitdown 萬能轉換器。
  請改用 markitdown skill（方向 2：MD→PDF）。
  若需高質感 PDF 設計/表單填寫，改用 pdf skill。
deprecated: true
redirect: markitdown
---

# Markdown 轉 PDF（已整併至 markitdown）

> **此技能已整併至 `markitdown` skill。**
> 請改用 `markitdown`（方向 2：MD→ANY）。
> 若需設計級 PDF / 表單填寫，改用 `pdf` skill。
>
> 快速替代：`npx --yes md-to-pdf input.md`

---

以下為舊版內容（僅供參考）：

# Markdown 轉 PDF 子流程（舊版）

這個技能現在只負責：

- Markdown 檔案轉 `.pdf`
- 批次 Markdown 轉 PDF
- 針對 Markdown 內容做快速 PDF 輸出

## 什麼時候用這個技能

- 使用者已經有 `.md` 檔案
- 使用者明確要求「轉成 PDF」
- 需求核心是轉檔，不是 PDF 設計或重排

## 什麼時候不要用這個技能

以下情況改用 `pdf`：

- 需要 CREATE / FILL / REFORMAT 工作流
- 需要高品質版面設計
- 需要填寫 PDF 表單
- 需要重排既有 PDF 或將文件重新設計

## 執行原則

1. 優先確認輸入是 Markdown 檔案或 Markdown 內容
2. 優先使用 `md-to-pdf (npm)`
3. 若 `md-to-pdf` 不可用，再考慮 `pandoc + xelatex`
4. 若需求超出純轉檔，立即切回 `pdf`

## 快速指令

```bash
npx --yes md-to-pdf input.md
npx --yes md-to-pdf input.md --stylesheet style.css
```

## 與主技能的關係

- 這個技能是 `pdf` 的子流程
- 主技能：`pdf`
- 子任務：Markdown -> PDF 轉換
