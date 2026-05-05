#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarkItDown 萬能文件轉換器
========================
整合 markitdown + pdfplumber(OCR回退) + pandoc + puppeteer
支援：ANY→MD、MD→ANY、HTML→PNG、批次轉換

用法：
  # ANY → Markdown
  python convert.py --input report.pdf --direction to-md
  python convert.py --input ./docs/ --direction to-md --ext pdf,docx,pptx

  # Markdown → DOCX / PDF
  python convert.py --input notes.md --direction to-docx
  python convert.py --input ./md_files/ --direction to-pdf

  # HTML → PNG
  python convert.py --input page.html --direction html-to-png
  python convert.py --input ./html_files/ --direction html-to-png

  # PDF 掃描版（OCR 模式）
  python convert.py --input scan.pdf --direction to-md --ocr --lang chi_tra+eng
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# ─────────────────────────────────────────────
# 方向 1：ANY → Markdown（markitdown 引擎）
# ─────────────────────────────────────────────

MARKITDOWN_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt",
    ".xlsx", ".xls", ".csv", ".json", ".xml",
    ".html", ".htm", ".jpg", ".jpeg", ".png",
    ".gif", ".bmp", ".tiff", ".wav", ".mp3",
    ".zip", ".epub", ".msg",
}


def convert_to_md(input_path: Path, output_path: Path | None = None,
                  ocr: bool = False, lang: str = "chi_tra+eng") -> Path:
    """將任意檔案轉為 Markdown。"""
    if output_path is None:
        output_path = input_path.with_suffix(".md")

    # PDF 掃描版 OCR 回退（使用 pdfplumber + tesseract）
    if input_path.suffix.lower() == ".pdf" and ocr:
        return _pdf_ocr_fallback(input_path, output_path, lang)

    # 主引擎：markitdown
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(str(input_path))
        output_path.write_text(result.markdown, encoding="utf-8")
        size_kb = output_path.stat().st_size / 1024
        print(f"  [OK] {input_path.name} -> {output_path.name} ({size_kb:.0f} KB)")
        return output_path
    except Exception as e:
        # PDF 自動回退到 pdfplumber
        if input_path.suffix.lower() == ".pdf":
            print(f"  [WARN] markitdown 失敗，回退到 pdfplumber: {e}")
            return _pdf_pdfplumber_fallback(input_path, output_path, lang)
        raise


def _pdf_pdfplumber_fallback(pdf_path: Path, output_path: Path,
                              lang: str = "chi_tra+eng") -> Path:
    """使用 pdfplumber 萃取文字型 PDF，含表格支援。"""
    import pdfplumber

    md_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages, start=1):
            md_lines.append(f"\n---\n\n## 第 {i} 頁\n")

            tables = page.extract_tables()
            table_bboxes = []
            if tables:
                for ts in page.find_tables():
                    table_bboxes.append(ts.bbox)

            if table_bboxes:
                non_table_page = page
                for bbox in table_bboxes:
                    non_table_page = non_table_page.outside_bbox(bbox)
                text = non_table_page.extract_text() or ""
            else:
                text = page.extract_text() or ""

            if text.strip():
                md_lines.append(text.strip() + "\n")

            for table in tables:
                md_lines.append("\n" + _table_to_markdown(table) + "\n")

    # Front matter
    front_matter = _build_front_matter(pdf_path)
    markdown = front_matter + "\n".join(md_lines)
    output_path.write_text(markdown, encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024
    print(f"  [OK] {pdf_path.name} -> {output_path.name} ({size_kb:.0f} KB) [pdfplumber]")
    return output_path


def _pdf_ocr_fallback(pdf_path: Path, output_path: Path,
                       lang: str = "chi_tra+eng") -> Path:
    """使用 pdf2image + pytesseract 對掃描版 PDF 做 OCR。"""
    from pdf2image import convert_from_path
    import pytesseract

    images = convert_from_path(str(pdf_path), dpi=300)
    md_lines = []
    for i, image in enumerate(images, start=1):
        text = pytesseract.image_to_string(image, lang=lang)
        md_lines.append(f"\n---\n\n## 第 {i} 頁\n")
        md_lines.append(text.strip() + "\n")

    front_matter = _build_front_matter(pdf_path)
    markdown = front_matter + "\n".join(md_lines)
    output_path.write_text(markdown, encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024
    print(f"  [OK] {pdf_path.name} -> {output_path.name} ({size_kb:.0f} KB) [OCR]")
    return output_path


def _table_to_markdown(table: list) -> str:
    """將表格（list of lists）轉為 Markdown 表格。"""
    if not table or not table[0]:
        return ""

    def clean(cell):
        if cell is None:
            return ""
        return str(cell).replace("\n", " ").strip()

    header = [clean(c) for c in table[0]]
    rows = [[clean(c) for c in row] for row in table[1:]]
    col_count = len(header)
    col_widths = [max(len(header[c]), 3) for c in range(col_count)]
    for row in rows:
        for c in range(min(len(row), col_count)):
            col_widths[c] = max(col_widths[c], len(row[c]))

    def fmt(cells):
        padded = [
            (cells[c] if c < len(cells) else "").ljust(col_widths[c])
            for c in range(col_count)
        ]
        return "| " + " | ".join(padded) + " |"

    sep = "| " + " | ".join("-" * w for w in col_widths) + " |"
    return "\n".join([fmt(header), sep] + [fmt(r) for r in rows])


def _build_front_matter(pdf_path: Path) -> str:
    """從 PDF metadata 建立 YAML front matter。"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        meta = reader.metadata or {}
        title = meta.get("/Title", pdf_path.stem) or pdf_path.stem
        author = meta.get("/Author", "") or ""
    except Exception:
        title = pdf_path.stem
        author = ""

    lines = ["---", f'title: "{title}"']
    if author:
        lines.append(f'author: "{author}"')
    lines.append(f'source: "{pdf_path.name}"')
    lines.append("---\n")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# 方向 2：Markdown → ANY（pandoc / md-to-pdf）
# ─────────────────────────────────────────────

def md_to_docx(input_path: Path, output_path: Path | None = None,
               template: str | None = None) -> Path:
    """Markdown → DOCX（via pandoc）。"""
    if output_path is None:
        output_path = input_path.with_suffix(".docx")
    cmd = ["pandoc", str(input_path), "-o", str(output_path)]
    if template:
        cmd.extend(["--reference-doc", template])
    subprocess.run(cmd, check=True)
    size_kb = output_path.stat().st_size / 1024
    print(f"  [OK] {input_path.name} -> {output_path.name} ({size_kb:.0f} KB)")
    return output_path


def md_to_pdf(input_path: Path, output_path: Path | None = None,
              stylesheet: str | None = None) -> Path:
    """Markdown → PDF（via md-to-pdf npm）。"""
    if output_path is None:
        output_path = input_path.with_suffix(".pdf")
    cmd = ["npx", "--yes", "md-to-pdf", str(input_path)]
    if stylesheet:
        cmd.extend(["--stylesheet", stylesheet])
    subprocess.run(cmd, check=True)
    # md-to-pdf 輸出到同目錄
    generated = input_path.with_suffix(".pdf")
    if generated != output_path and generated.exists():
        generated.rename(output_path)
    size_kb = output_path.stat().st_size / 1024
    print(f"  [OK] {input_path.name} -> {output_path.name} ({size_kb:.0f} KB)")
    return output_path


def md_to_html(input_path: Path, output_path: Path | None = None) -> Path:
    """Markdown → HTML（via pandoc）。"""
    if output_path is None:
        output_path = input_path.with_suffix(".html")
    subprocess.run([
        "pandoc", str(input_path), "-o", str(output_path), "--standalone"
    ], check=True)
    size_kb = output_path.stat().st_size / 1024
    print(f"  [OK] {input_path.name} -> {output_path.name} ({size_kb:.0f} KB)")
    return output_path


# ─────────────────────────────────────────────
# 方向 3：HTML → PNG（puppeteer）
# ─────────────────────────────────────────────

def html_to_png(input_path: Path, output_path: Path | None = None,
                width: int = 1280, height: int = 900) -> Path:
    """HTML → PNG 截圖（via puppeteer）。"""
    if output_path is None:
        output_path = input_path.with_suffix(".png")
    html_abs = str(input_path.resolve()).replace("\\", "/")
    png_abs = str(output_path.resolve()).replace("\\", "/")

    js_code = f"""
const puppeteer = require('puppeteer');
(async () => {{
  const browser = await puppeteer.launch({{ headless: 'new' }});
  const page = await browser.newPage();
  await page.setViewport({{ width: {width}, height: {height} }});
  await page.goto('file:///{html_abs}', {{ waitUntil: 'networkidle0', timeout: 15000 }});
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({{ path: '{png_abs}', fullPage: true, type: 'png' }});
  await browser.close();
}})();
"""
    subprocess.run(["node", "-e", js_code], check=True)
    size_kb = output_path.stat().st_size / 1024
    print(f"  [OK] {input_path.name} -> {output_path.name} ({size_kb:.0f} KB)")
    return output_path


# ─────────────────────────────────────────────
# 批次轉換引擎
# ─────────────────────────────────────────────

def batch_convert(input_dir: Path, direction: str,
                  ext_filter: set | None = None, **kwargs) -> dict:
    """批次轉換資料夾內檔案。回傳 {success: int, failed: list}。"""
    results = {"success": 0, "failed": []}

    # 決定要處理的檔案
    if direction == "to-md":
        target_exts = ext_filter or MARKITDOWN_EXTENSIONS
        files = [f for f in input_dir.iterdir()
                 if f.is_file() and f.suffix.lower() in target_exts]
        convert_fn = lambda f: convert_to_md(f, **kwargs)
    elif direction == "to-docx":
        files = list(input_dir.glob("*.md"))
        convert_fn = lambda f: md_to_docx(f, **kwargs)
    elif direction == "to-pdf":
        files = list(input_dir.glob("*.md"))
        convert_fn = lambda f: md_to_pdf(f, **kwargs)
    elif direction == "to-html":
        files = list(input_dir.glob("*.md"))
        convert_fn = lambda f: md_to_html(f, **kwargs)
    elif direction == "html-to-png":
        files = list(input_dir.glob("*.html"))
        convert_fn = lambda f: html_to_png(f, **kwargs)
    else:
        print(f"[ERR] 不支援的方向：{direction}")
        return results

    if not files:
        print(f"[WARN] 在 {input_dir} 找不到符合條件的檔案")
        return results

    print(f"[BATCH] {len(files)} 個檔案，方向：{direction}\n")

    for f in sorted(files):
        try:
            convert_fn(f)
            results["success"] += 1
        except Exception as e:
            print(f"  [FAIL] {f.name}: {e}")
            results["failed"].append(f.name)

    total = results["success"] + len(results["failed"])
    print(f"\n[DONE] {results['success']}/{total} 成功")
    if results["failed"]:
        print(f"[FAIL] 失敗清單: {', '.join(results['failed'])}")
    return results


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="MarkItDown 萬能文件轉換器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
方向選項：
  to-md        ANY → Markdown（markitdown 引擎）
  to-docx      Markdown → Word（pandoc）
  to-pdf       Markdown → PDF（md-to-pdf）
  to-html      Markdown → HTML（pandoc）
  html-to-png  HTML → PNG 截圖（puppeteer）

範例：
  python convert.py --input report.pdf --direction to-md
  python convert.py --input ./docs/ --direction to-md --ext pdf,docx
  python convert.py --input notes.md --direction to-docx
  python convert.py --input ./pages/ --direction html-to-png
  python convert.py --input scan.pdf --direction to-md --ocr
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="輸入檔案或資料夾")
    parser.add_argument("--output", "-o", help="輸出檔案或資料夾")
    parser.add_argument("--direction", "-d", required=True,
                        choices=["to-md", "to-docx", "to-pdf", "to-html", "html-to-png"],
                        help="轉換方向")
    parser.add_argument("--ext", help="篩選副檔名，逗號分隔（僅 to-md 批次）例：pdf,docx,pptx")
    parser.add_argument("--ocr", action="store_true", help="強制 OCR（僅 PDF）")
    parser.add_argument("--lang", default="chi_tra+eng", help="OCR 語言（預設 chi_tra+eng）")
    parser.add_argument("--template", help="Word 模板路徑（僅 to-docx）")
    parser.add_argument("--stylesheet", help="CSS 樣式路徑（僅 to-pdf）")
    parser.add_argument("--width", type=int, default=1280, help="截圖寬度（僅 html-to-png）")

    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None

    # 解析副檔名篩選
    ext_filter = None
    if args.ext:
        ext_filter = {"." + e.strip().lstrip(".") for e in args.ext.split(",")}

    # 批次 or 單檔
    if input_path.is_dir():
        kwargs = {}
        if args.ocr:
            kwargs["ocr"] = True
        if args.lang != "chi_tra+eng":
            kwargs["lang"] = args.lang
        if args.template:
            kwargs["template"] = args.template
        if args.stylesheet:
            kwargs["stylesheet"] = args.stylesheet
        if args.width != 1280:
            kwargs["width"] = args.width
        batch_convert(input_path, args.direction, ext_filter=ext_filter, **kwargs)
    else:
        # 單檔轉換
        if args.direction == "to-md":
            convert_to_md(input_path, output_path, ocr=args.ocr, lang=args.lang)
        elif args.direction == "to-docx":
            md_to_docx(input_path, output_path, template=args.template)
        elif args.direction == "to-pdf":
            md_to_pdf(input_path, output_path, stylesheet=args.stylesheet)
        elif args.direction == "to-html":
            md_to_html(input_path, output_path)
        elif args.direction == "html-to-png":
            html_to_png(input_path, output_path, width=args.width)


if __name__ == "__main__":
    main()
