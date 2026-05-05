---
name: md-to-docx
description: >
  [已整併] 此技能已併入 markitdown 萬能轉換器。
  請改用 markitdown skill（方向 2：MD→DOCX）。
  若需正式文件撰寫/編修，改用 docx skill。
deprecated: true
redirect: markitdown
---

# Markdown 轉 Word（已整併至 markitdown）

> **此技能已整併至 `markitdown` skill。**
> 請改用 `markitdown`（方向 2：MD→ANY）。
> 若需正式文件建立/編輯，改用 `docx` skill。
>
> 快速替代：`pandoc input.md -o output.docx`

---

以下為舊版內容（僅供參考）：

# Markdown 轉 Word 子流程（舊版）

這個技能現在只負責：

- Markdown 檔案轉 `.docx`
- 批次 Markdown 轉 Word
- 套用既有 Word 樣板做 Markdown 匯出

## 什麼時候用這個技能

- 使用者已經有 `.md` 檔案
- 使用者明確要求「轉成 Word」或「輸出 `.docx`」
- 需求核心是轉檔，不是文件策劃或深度編修

## 什麼時候不要用這個技能

以下情況改用 `docx`：

- 撰寫正式報告、提案、合約、文件
- 編修現有 `.docx`
- 套用正式版面與樣式系統
- 需要更完整的文件結構與格式控管

## 執行原則

1. 優先確認輸入是 Markdown 檔案或 Markdown 內容
2. 優先使用 `pandoc`
3. 若要套用 Word 樣板，可用 `--reference-doc`
4. 若需求超出純轉檔，立即切回 `docx`

## 快速指令

```bash
pandoc input.md -o output.docx
pandoc input.md -o output.docx --reference-doc=template.docx
```

## 與主技能的關係

- 這個技能是 `docx` 的子流程
- 主技能：`docx`
- 子任務：Markdown -> DOCX 轉換
