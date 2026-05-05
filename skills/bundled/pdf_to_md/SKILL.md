---
name: pdf_to_md
description: >
  [已整併] 此技能已併入 markitdown 萬能轉換器。
  請改用 markitdown skill。
deprecated: true
redirect: markitdown
---

# PDF 轉 Markdown 技能（已整併至 markitdown）

> **此技能已整併至 `markitdown` skill。**
> 請改用 `markitdown`，它支援更多格式且包含本技能的所有功能。
>
> 快速替代：`markitdown report.pdf -o report.md`

---

以下為舊版內容（僅供參考）：

# PDF 轉 Markdown 技能（舊版）

將 PDF 檔案轉換為格式良好的 Markdown 文件，自動處理文字萃取、表格轉換與掃描版 OCR。

## 前置檢查

1. Check if 使用者提供了 PDF 檔案路徑或資料夾路徑
2. Check if PDF 檔案存在且可讀取
3. Check if 需要的 Python 套件已安裝：
   - **必要**：`pdfplumber`（文字型 PDF）
   - **OCR 用**：`pdf2image`、`pytesseract`（掃描版 PDF）
   - **OCR 外部依賴**：Tesseract OCR、Poppler
4. 若套件未安裝，提示使用者執行：
   ```bash
   pip install pdfplumber pdf2image pytesseract
   ```

## 執行步驟

### Step 1：判斷轉換模式

Ask user 確認轉換需求：
- **單一檔案**：提供一個 PDF 路徑
- **批次轉換**：提供一個資料夾路徑，轉換所有 PDF

### Step 2：偵測 PDF 類型

使用 `@assets/pdf_to_md.py` 中的 `is_scanned_pdf()` 函式自動偵測：
- 從前 3 頁萃取文字，若文字少於 20 字元 → 判定為掃描版
- 掃描版自動切換 OCR 模式
- 使用者也可手動指定 `--ocr` 強制使用 OCR

### Step 3：萃取內容

**文字型 PDF**（使用 pdfplumber）：
1. 逐頁萃取文字內容
2. 偵測並分離表格區域，避免文字重複
3. 表格自動轉為 Markdown 表格格式

**掃描版 PDF**（使用 OCR）：
1. 以 300 DPI 將 PDF 頁面轉為圖片
2. 使用 Tesseract OCR 辨識文字
3. 預設語言：`chi_tra+eng`（繁體中文 + 英文）

### Step 4：組裝 Markdown

1. 從 PDF Metadata 產生 YAML Front Matter（標題、作者、日期）
2. 每頁以 `## 第 N 頁` 作為標題分隔
3. 表格轉為對齊的 Markdown 表格
4. 輸出為 UTF-8 編碼的 `.md` 檔案

### Step 5：輸出結果

- 預設輸出路徑：與 PDF 同目錄、同檔名但副檔名改為 `.md`
- 可用 `-o` 指定自訂輸出路徑
- 批次模式可指定輸出資料夾

## 例外處理

- **PDF 不存在**：回報 `FileNotFoundError` 並提示正確路徑
- **套件未安裝**：明確提示需要安裝哪個套件及安裝指令
- **OCR 辨識失敗**：確認 Tesseract 和 Poppler 是否正確安裝
- **表格萃取異常**：跳過損壞的表格，繼續處理其餘內容
- **批次轉換部分失敗**：記錄失敗檔案清單，不中斷其他檔案轉換

## 安全規則

- MUST 保留原始 PDF 檔案，NEVER 刪除或修改來源 PDF
- MUST 使用 UTF-8 編碼輸出
- NEVER 在未經使用者確認的情況下覆蓋已存在的 .md 檔案
- MUST 在批次轉換前確認資料夾路徑正確

## 輸出格式

輸出的 Markdown 檔案結構：

```markdown
---
title: "文件標題"
author: "作者"
source: "原始檔名.pdf"
---

## 第 1 頁

頁面文字內容...

| 欄位 A | 欄位 B | 欄位 C |
| ------ | ------ | ------ |
| 資料 1 | 資料 2 | 資料 3 |

---

## 第 2 頁

頁面文字內容...
```

## 範例

### 範例 1：單一檔案轉換

**使用者輸入：**
> 幫我把 report.pdf 轉成 Markdown

**執行指令：**
```bash
python @assets/pdf_to_md.py report.pdf
```

**預期輸出：** 同目錄產生 `report.md`

### 範例 2：指定輸出路徑

**使用者輸入：**
> 把 meeting.pdf 轉成 Markdown，存到 output 資料夾

**執行指令：**
```bash
python @assets/pdf_to_md.py meeting.pdf -o ./output/meeting.md
```

### 範例 3：掃描版 PDF（OCR）

**使用者輸入：**
> 這是掃描的文件，幫我 OCR 轉 Markdown

**執行指令：**
```bash
python @assets/pdf_to_md.py scan.pdf --ocr --lang chi_tra+eng
```

### 範例 4：批次轉換

**使用者輸入：**
> 把 pdfs 資料夾裡所有 PDF 都轉成 Markdown

**執行指令：**
```bash
python @assets/pdf_to_md.py ./pdfs/ --batch -o ./output/
```

## CLI 參數速查

| 參數 | 說明 | 預設值 |
| --- | --- | --- |
| `input` | PDF 檔案路徑或資料夾路徑 | （必填） |
| `-o, --output` | 輸出路徑 | 與 PDF 同目錄同名 |
| `--ocr` | 強制 OCR 模式 | 自動偵測 |
| `--lang` | OCR 語言 | `chi_tra+eng` |
| `--batch` | 批次轉換模式 | 關閉 |
| `--no-auto-detect` | 關閉自動偵測掃描版 | 開啟 |
