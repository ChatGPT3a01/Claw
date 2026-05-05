---
name: markitdown
description: >
  萬能文件格式轉換瑞士刀。整合微軟 MarkItDown 引擎 + pandoc + puppeteer，
  支援三大轉換方向：ANY→Markdown、Markdown→ANY、ANY→ANY。
  當使用者需要讀取/轉換任何文件格式時觸發。
  觸發詞：轉 Markdown、轉 MD、文件轉換、格式轉換、轉檔、讀取文件、
  PDF 轉 MD、Word 轉 MD、PPT 轉 MD、Excel 轉 MD、
  MD 轉 Word、MD 轉 PDF、HTML 轉圖片、批次轉換。
  整併自：pdf_to_md、md-to-docx、md-to-pdf、html-to-png。
---

# MarkItDown — 萬能文件格式轉換瑞士刀

將任何文件轉成 AI 可讀的 Markdown，或從 Markdown 輸出為各種格式。

## 與其他 Skill 的分工

| 需求 | 用哪個 Skill |
|------|-------------|
| **讀取 / 轉換**文件（任何格式 → MD） | `markitdown`（本技能） |
| **建立 / 編輯** Word 文件 | `docx` |
| **建立 / 編輯** PowerPoint 簡報 | `pptx` |
| **建立 / 編輯** Excel 試算表 | `xlsx` |
| **設計級** PDF / 表單填寫 | `pdf` |
| **進階語者辨識**音訊轉文字 | `transcribe` |

> 簡單口訣：**讀轉用 markitdown，建編用專門 skill**

---

## 支援的三大方向

### 方向 1：ANY → Markdown（markitdown 引擎）

| 格式類別 | 支援格式 |
|----------|---------|
| 辦公文件 | PDF, DOCX, PPTX, XLSX/XLS |
| 網頁內容 | HTML, URL（直接丟網址） |
| 影像檔案 | JPG, PNG（OCR 辨識 / AI 圖片描述） |
| 音訊檔案 | WAV, MP3（語音轉文字） |
| 資料格式 | CSV, JSON, XML |
| 其他格式 | ZIP（自動解壓轉換）, EPub, Outlook MSG |

### 方向 2：Markdown → ANY（pandoc / md-to-pdf）

| 輸出格式 | 引擎 | 指令 |
|----------|------|------|
| DOCX | pandoc | `pandoc input.md -o output.docx` |
| DOCX（套模板） | pandoc | `pandoc input.md -o output.docx --reference-doc=template.docx` |
| PDF | md-to-pdf (npm) | `npx --yes md-to-pdf input.md` |
| PDF（自訂 CSS） | md-to-pdf | `npx --yes md-to-pdf input.md --stylesheet style.css` |
| HTML | pandoc | `pandoc input.md -o output.html --standalone` |

### 方向 3：ANY → ANY（先轉 MD 再轉目標 / 直接轉）

| 轉換路線 | 方法 |
|----------|------|
| DOCX → PDF | markitdown → MD → md-to-pdf |
| PDF → DOCX | markitdown → MD → pandoc |
| HTML → PNG | puppeteer 直接截圖 |
| PPT → PDF | markitdown → MD → md-to-pdf |
| 任意 → 任意 | 先 markitdown → MD，再 pandoc/md-to-pdf 輸出 |

---

## 前置檢查

### 必要（方向 1）
```bash
pip show markitdown   # 確認已安裝
# 若未安裝：
pip install "markitdown[all]"
# 或選擇性安裝：
pip install "markitdown[pdf,docx,pptx]"
```

### 選用（方向 2）
```bash
pandoc --version         # MD → DOCX / HTML
npx --yes md-to-pdf -V   # MD → PDF
```

### 選用（方向 3：HTML → PNG）
```bash
node --version           # Node.js 18+
npx puppeteer browsers install chrome   # puppeteer 瀏覽器
```

### 選用（AI 增強）
- 圖片 AI 描述：需要 OpenAI API Key（設定 `OPENAI_API_KEY` 環境變數）
- OCR 辨識：需要 Azure Document Intelligence 或 Tesseract OCR

---

## 執行步驟

### Step 1：判斷轉換方向

根據使用者需求判斷：

| 使用者說… | 方向 | 執行路線 |
|-----------|------|---------|
| 「把這個 PDF/Word/PPT 轉成 Markdown」 | ANY → MD | markitdown 引擎 |
| 「讀取這個文件的內容」 | ANY → MD | markitdown 引擎 |
| 「把 Markdown 轉成 Word/PDF」 | MD → ANY | pandoc / md-to-pdf |
| 「把這個 Word 轉成 PDF」 | ANY → ANY | 兩階段轉換 |
| 「把 HTML 截圖成 PNG」 | HTML → PNG | puppeteer |
| 「批次轉換整個資料夾」 | 批次 | 使用 assets/convert.py |

### Step 2：執行轉換

#### 方向 1：ANY → Markdown

**單檔轉換（命令列）：**
```bash
markitdown 報告.pdf -o 報告.md
markitdown 簡報.pptx -o 簡報.md
markitdown 表格.xlsx -o 表格.md
markitdown https://example.com -o 網頁.md
```

**單檔轉換（Python）：**
```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("文件.docx")
print(result.markdown)

# 輸出到檔案
from pathlib import Path
Path("文件.md").write_text(result.markdown, encoding="utf-8")
```

**搭配 AI 圖片描述：**
```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()  # 需設定 OPENAI_API_KEY
md = MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("照片.jpg")
print(result.markdown)
```

**批次轉換：**
```bash
python @assets/convert.py --input ./documents/ --direction to-md
python @assets/convert.py --input ./documents/ --direction to-md --ext pdf,docx
```

#### 方向 2：Markdown → ANY

**MD → DOCX：**
```bash
pandoc input.md -o output.docx
pandoc input.md -o output.docx --reference-doc=template.docx
```

**MD → PDF：**
```bash
npx --yes md-to-pdf input.md
npx --yes md-to-pdf input.md --stylesheet custom.css
```

**MD → HTML：**
```bash
pandoc input.md -o output.html --standalone
```

**批次 MD → DOCX/PDF：**
```bash
python @assets/convert.py --input ./markdown_files/ --direction to-docx
python @assets/convert.py --input ./markdown_files/ --direction to-pdf
```

#### 方向 3：ANY → ANY

**兩階段轉換（例：DOCX → PDF）：**
```bash
# 階段 1：DOCX → MD
markitdown document.docx -o temp.md
# 階段 2：MD → PDF
npx --yes md-to-pdf temp.md
```

**HTML → PNG（puppeteer 直接截圖）：**
```bash
node -e "
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });
  const htmlPath = process.argv[1].replace(/\\\\/g, '/');
  const pngPath = htmlPath.replace(/\\.html$/, '.png');
  await page.goto('file:///' + htmlPath, { waitUntil: 'networkidle0', timeout: 15000 });
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: pngPath, fullPage: true, type: 'png' });
  console.log('Done: ' + pngPath);
  await browser.close();
})();
" "<HTML_FILE_PATH>"
```

**批次 HTML → PNG：**
```bash
python @assets/convert.py --input ./html_files/ --direction html-to-png
```

### Step 3：輸出確認

1. 確認輸出檔案已建立且非空
2. 對 Markdown 輸出：檢查標題、表格、清單結構是否保留
3. 對 PDF/DOCX 輸出：確認格式正確
4. 回報轉換結果（檔案路徑、大小、頁數）

---

## 進階用法

### PDF 深度萃取（含表格 + OCR 回退）

當 markitdown 對 PDF 的表格萃取效果不佳時，使用 `@assets/convert.py` 的 pdfplumber 回退：

```bash
python @assets/convert.py --input scan.pdf --direction to-md --ocr
python @assets/convert.py --input scan.pdf --direction to-md --lang chi_tra+eng
```

### MCP 伺服器模式

MarkItDown 原生支援 MCP，可掛載到 Claude Desktop：

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "markitdown",
      "args": ["--mcp"]
    }
  }
}
```

### Token 節省提示

先用 markitdown 轉成 Markdown 再餵給 AI，比直接上傳原始檔案可**節省高達 80% Token**。
建議的工作流：
1. `markitdown document.pdf -o document.md`
2. 將 `document.md` 餵給 LLM 分析

---

## 已知限制

| 限制 | 替代方案 |
|------|---------|
| 複雜圖表轉換效果有限 | 搭配 AI 圖片描述 |
| 高度客製化排版可能丟失 | 需要高保真格式用 pandoc |
| 掃描版 PDF 需 OCR | 使用 `--ocr` 或 Azure Document Intelligence |
| 音訊轉文字品質一般 | 進階需求改用 `transcribe` skill |
| 影片不支援 | YouTube 可擷取字幕 |

---

## 常見問題

| 問題 | 解法 |
|------|------|
| `markitdown` 指令找不到 | `pip install "markitdown[all]"` |
| PDF 表格亂掉 | 加 `--ocr` 或改用 pdfplumber 回退 |
| 中文亂碼 | 確保輸出使用 UTF-8 編碼 |
| 圖片沒有文字描述 | 需設定 `OPENAI_API_KEY` 搭配 AI |
| pandoc 找不到 | `winget install JohnMacFarlane.Pandoc` 或 `choco install pandoc` |
| puppeteer 截圖空白 | 確認 HTML 的 file:// 路徑正確，Windows 需用正斜線 |
