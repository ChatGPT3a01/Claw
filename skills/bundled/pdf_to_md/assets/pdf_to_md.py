#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 轉 Markdown 工具
====================
支援功能：
  1. 一般文字型 PDF → Markdown（使用 pdfplumber）
  2. 掃描版 PDF → Markdown（使用 OCR：pdf2image + pytesseract）
  3. 表格自動轉換為 Markdown 表格格式
  4. 批次轉換整個資料夾的 PDF

依賴套件安裝：
  pip install pdfplumber pdf2image pytesseract

  掃描版 OCR 額外需要：
  - Tesseract OCR：https://github.com/tesseract-ocr/tesseract
  - Poppler（pdf2image 使用）：https://github.com/oschwartz10612/poppler-windows/releases
"""

import argparse
import os
import sys
from pathlib import Path


# ─────────────────────────────────────────────
# 核心轉換：文字型 PDF
# ─────────────────────────────────────────────

def extract_text_pdf(pdf_path: Path, language: str = "chi_tra+eng") -> str:
    """
    使用 pdfplumber 萃取文字型 PDF 內容，並轉為 Markdown。
    - 一般段落 → 段落文字
    - 表格 → Markdown 表格
    """
    try:
        import pdfplumber
    except ImportError:
        print("❌ 請先安裝 pdfplumber：pip install pdfplumber")
        sys.exit(1)

    md_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"  📄 共 {total} 頁，開始萃取…")

        for i, page in enumerate(pdf.pages, start=1):
            print(f"  處理第 {i}/{total} 頁…", end="\r")

            # ── 頁碼標題 ──
            md_lines.append(f"\n---\n\n## 第 {i} 頁\n")

            # ── 取得表格佔據區域，避免重複抓文字 ──
            tables = page.extract_tables()
            table_bboxes = []
            if tables:
                # 取得每個表格的邊界框
                for table_settings in page.find_tables():
                    table_bboxes.append(table_settings.bbox)

            # ── 萃取非表格區域的文字 ──
            if table_bboxes:
                # 從頁面移除表格區域後萃取文字
                non_table_page = page
                for bbox in table_bboxes:
                    non_table_page = non_table_page.outside_bbox(bbox)
                text = non_table_page.extract_text() or ""
            else:
                text = page.extract_text() or ""

            if text.strip():
                md_lines.append(text.strip() + "\n")

            # ── 轉換表格 ──
            for table in tables:
                md_lines.append("\n" + table_to_markdown(table) + "\n")

    print()  # 換行
    return "\n".join(md_lines)


def table_to_markdown(table: list) -> str:
    """將 pdfplumber 萃取的表格（list of lists）轉為 Markdown 表格字串。"""
    if not table or not table[0]:
        return ""

    # 清理單元格內容
    def clean(cell):
        if cell is None:
            return ""
        return str(cell).replace("\n", " ").strip()

    # 標頭列
    header = [clean(cell) for cell in table[0]]
    rows = [[clean(cell) for cell in row] for row in table[1:]]

    # 計算每欄最大寬度
    col_count = len(header)
    col_widths = [max(len(header[c]), 3) for c in range(col_count)]
    for row in rows:
        for c in range(min(len(row), col_count)):
            col_widths[c] = max(col_widths[c], len(row[c]))

    def fmt_row(cells):
        padded = []
        for c in range(col_count):
            val = cells[c] if c < len(cells) else ""
            padded.append(val.ljust(col_widths[c]))
        return "| " + " | ".join(padded) + " |"

    separator = "| " + " | ".join("-" * w for w in col_widths) + " |"

    lines = [fmt_row(header), separator]
    for row in rows:
        lines.append(fmt_row(row))

    return "\n".join(lines)


# ─────────────────────────────────────────────
# 核心轉換：掃描版 PDF（OCR）
# ─────────────────────────────────────────────

def extract_ocr_pdf(pdf_path: Path, language: str = "chi_tra+eng") -> str:
    """
    使用 pdf2image + pytesseract 對掃描版 PDF 做 OCR，並轉為 Markdown。
    language 範例：
      "chi_tra+eng"  → 繁體中文 + 英文
      "chi_sim+eng"  → 簡體中文 + 英文
      "eng"          → 純英文
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        print("❌ 請先安裝 pdf2image：pip install pdf2image")
        sys.exit(1)
    try:
        import pytesseract
    except ImportError:
        print("❌ 請先安裝 pytesseract：pip install pytesseract")
        sys.exit(1)

    print(f"  🔍 OCR 模式，語言：{language}")
    images = convert_from_path(str(pdf_path), dpi=300)
    total = len(images)
    print(f"  📄 共 {total} 頁，開始 OCR…")

    md_lines = []
    for i, image in enumerate(images, start=1):
        print(f"  OCR 第 {i}/{total} 頁…", end="\r")
        text = pytesseract.image_to_string(image, lang=language)
        md_lines.append(f"\n---\n\n## 第 {i} 頁\n")
        md_lines.append(text.strip() + "\n")

    print()
    return "\n".join(md_lines)


# ─────────────────────────────────────────────
# 工具函式
# ─────────────────────────────────────────────

def is_scanned_pdf(pdf_path: Path, sample_pages: int = 3) -> bool:
    """
    嘗試從前幾頁萃取文字，若文字極少（<20 字元），推测為掃描版 PDF。
    """
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            total_text = ""
            for page in pdf.pages[:sample_pages]:
                total_text += page.extract_text() or ""
        return len(total_text.strip()) < 20
    except Exception:
        return False


def build_front_matter(pdf_path: Path) -> str:
    """產生 Markdown YAML Front Matter（從 PDF Metadata 讀取）。"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        meta = reader.metadata or {}
        title = meta.get("/Title", pdf_path.stem) or pdf_path.stem
        author = meta.get("/Author", "") or ""
        subject = meta.get("/Subject", "") or ""
        creation = meta.get("/CreationDate", "") or ""
    except Exception:
        title = pdf_path.stem
        author = subject = creation = ""

    lines = ["---"]
    lines.append(f'title: "{title}"')
    if author:
        lines.append(f'author: "{author}"')
    if subject:
        lines.append(f'subject: "{subject}"')
    if creation:
        lines.append(f'created: "{creation}"')
    lines.append(f'source: "{pdf_path.name}"')
    lines.append("---\n")
    return "\n".join(lines)


def convert_pdf_to_md(
    pdf_path: Path,
    output_path: Path | None = None,
    ocr: bool = False,
    auto_detect: bool = True,
    language: str = "chi_tra+eng",
) -> Path:
    """
    主要轉換函式。

    參數：
      pdf_path    - 輸入 PDF 路徑
      output_path - 輸出 .md 路徑（預設與 PDF 同目錄同名）
      ocr         - 強制使用 OCR 模式
      auto_detect - 自動偵測是否為掃描版（ocr=False 時有效）
      language    - Tesseract OCR 語言字串
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"找不到檔案：{pdf_path}")

    if output_path is None:
        output_path = pdf_path.with_suffix(".md")

    print(f"\n🔄 轉換：{pdf_path.name}")

    # 決定使用哪種模式
    use_ocr = ocr
    if not use_ocr and auto_detect:
        if is_scanned_pdf(pdf_path):
            print("  ⚠️  偵測到掃描版 PDF，自動切換為 OCR 模式")
            use_ocr = True

    # 執行轉換
    front_matter = build_front_matter(pdf_path)
    if use_ocr:
        content = extract_ocr_pdf(pdf_path, language=language)
    else:
        content = extract_text_pdf(pdf_path, language=language)

    # 寫出 Markdown
    markdown = front_matter + content
    output_path.write_text(markdown, encoding="utf-8")
    print(f"  ✅ 已輸出：{output_path}")
    return output_path


def batch_convert(
    folder: Path,
    output_folder: Path | None = None,
    ocr: bool = False,
    auto_detect: bool = True,
    language: str = "chi_tra+eng",
):
    """批次轉換資料夾內所有 PDF。"""
    pdfs = list(folder.glob("*.pdf"))
    if not pdfs:
        print(f"⚠️  在 {folder} 中找不到任何 PDF 檔案。")
        return

    out_dir = output_folder or folder
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"📂 批次轉換 {len(pdfs)} 個 PDF，輸出到：{out_dir}")
    success, failed = 0, []

    for pdf in pdfs:
        out = out_dir / pdf.with_suffix(".md").name
        try:
            convert_pdf_to_md(pdf, out, ocr=ocr, auto_detect=auto_detect, language=language)
            success += 1
        except Exception as e:
            print(f"  ❌ 失敗：{pdf.name}，原因：{e}")
            failed.append(pdf.name)

    print(f"\n✅ 完成：{success}/{len(pdfs)} 個成功")
    if failed:
        print("❌ 失敗清單：" + ", ".join(failed))


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PDF 轉 Markdown 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 轉換單一 PDF（自動偵測掃描版）
  python pdf_to_md.py report.pdf

  # 指定輸出路徑
  python pdf_to_md.py report.pdf -o output.md

  # 強制 OCR 模式（繁體中文 + 英文）
  python pdf_to_md.py scan.pdf --ocr

  # 簡體中文 OCR
  python pdf_to_md.py scan.pdf --ocr --lang chi_sim+eng

  # 批次轉換整個資料夾
  python pdf_to_md.py ./pdfs/ --batch

  # 批次轉換，輸出到指定資料夾
  python pdf_to_md.py ./pdfs/ --batch -o ./output/
        """,
    )
    parser.add_argument("input", help="PDF 檔案路徑 或 資料夾路徑（搭配 --batch）")
    parser.add_argument("-o", "--output", help="輸出 .md 檔案路徑 或 輸出資料夾（搭配 --batch）")
    parser.add_argument("--ocr", action="store_true", help="強制使用 OCR 模式（適合掃描版 PDF）")
    parser.add_argument(
        "--no-auto-detect",
        action="store_true",
        help="關閉自動偵測掃描版 PDF（預設會自動偵測）",
    )
    parser.add_argument(
        "--lang",
        default="chi_tra+eng",
        help="Tesseract OCR 語言（預設：chi_tra+eng）",
    )
    parser.add_argument("--batch", action="store_true", help="批次轉換資料夾內所有 PDF")

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None
    auto_detect = not args.no_auto_detect

    if args.batch or input_path.is_dir():
        if not input_path.is_dir():
            print(f"❌ 批次模式需要指定資料夾，但 {input_path} 不是資料夾。")
            sys.exit(1)
        batch_convert(input_path, output_path, ocr=args.ocr, auto_detect=auto_detect, language=args.lang)
    else:
        if not input_path.suffix.lower() == ".pdf":
            print(f"❌ 輸入檔案必須是 .pdf 格式：{input_path}")
            sys.exit(1)
        convert_pdf_to_md(input_path, output_path, ocr=args.ocr, auto_detect=auto_detect, language=args.lang)


if __name__ == "__main__":
    main()
