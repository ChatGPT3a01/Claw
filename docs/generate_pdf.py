#!/usr/bin/env python3
"""
generate_pdf.py — 將 teaching-guide.md 轉換為中文 PDF
使用 reportlab + 微軟正黑體

Usage:
    python docs/generate_pdf.py
    python docs/generate_pdf.py --input docs/teaching-guide.md --output docs/teaching-guide.pdf
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --------------- Font Registration ---------------

# Windows 微軟正黑體 paths
_FONT_PATHS = [
    "C:/Windows/Fonts/msjh.ttc",
    "C:/Windows/Fonts/msjhbd.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/mingliu.ttc",
]

_FONT_NAME = "MSJhenghei"
_FONT_REGISTERED = False


def _register_fonts():
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    for fp in _FONT_PATHS:
        if Path(fp).exists():
            try:
                pdfmetrics.registerFont(TTFont(_FONT_NAME, fp, subfontIndex=0))
                _FONT_REGISTERED = True
                return
            except Exception:
                continue
    # Fallback: try system font name
    try:
        pdfmetrics.registerFont(TTFont(_FONT_NAME, "Microsoft JhengHei"))
        _FONT_REGISTERED = True
    except Exception:
        print("[WARN] 找不到微軟正黑體，使用預設字體（中文可能亂碼）")


# --------------- Style Definitions ---------------

def _build_styles() -> dict[str, ParagraphStyle]:
    _register_fonts()
    font = _FONT_NAME if _FONT_REGISTERED else "Helvetica"
    font_bold = font  # TTC 不分 bold，用 size 區分

    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "Title_CN", parent=base["Title"],
            fontName=font, fontSize=22, leading=30,
            textColor=HexColor("#1a1a2e"), alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle_CN", parent=base["Normal"],
            fontName=font, fontSize=12, leading=18,
            textColor=HexColor("#555555"), alignment=TA_CENTER,
            spaceAfter=20,
        ),
        "h1": ParagraphStyle(
            "H1_CN", parent=base["Heading1"],
            fontName=font, fontSize=18, leading=26,
            textColor=HexColor("#16213e"), spaceBefore=20, spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "H2_CN", parent=base["Heading2"],
            fontName=font, fontSize=14, leading=22,
            textColor=HexColor("#0f3460"), spaceBefore=14, spaceAfter=8,
        ),
        "h3": ParagraphStyle(
            "H3_CN", parent=base["Heading3"],
            fontName=font, fontSize=12, leading=18,
            textColor=HexColor("#533483"), spaceBefore=10, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body_CN", parent=base["Normal"],
            fontName=font, fontSize=10.5, leading=17,
            textColor=HexColor("#333333"), spaceAfter=6,
        ),
        "code": ParagraphStyle(
            "Code_CN", parent=base["Code"],
            fontName="Courier", fontSize=9, leading=13,
            textColor=HexColor("#1a1a2e"),
            backColor=HexColor("#f5f5f5"),
            leftIndent=12, rightIndent=12,
            spaceBefore=4, spaceAfter=4,
            borderWidth=0.5, borderColor=HexColor("#dddddd"),
            borderPadding=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet_CN", parent=base["Normal"],
            fontName=font, fontSize=10.5, leading=17,
            textColor=HexColor("#333333"),
            leftIndent=20, bulletIndent=8,
            spaceAfter=3,
        ),
        "table_header": ParagraphStyle(
            "TH_CN", parent=base["Normal"],
            fontName=font, fontSize=9.5, leading=14,
            textColor=HexColor("#ffffff"),
        ),
        "table_cell": ParagraphStyle(
            "TD_CN", parent=base["Normal"],
            fontName=font, fontSize=9.5, leading=14,
            textColor=HexColor("#333333"),
        ),
    }


# --------------- Markdown → Flowables ---------------

def _escape_xml(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline_format(text: str) -> str:
    """Convert basic inline markdown (bold, code, links) to reportlab XML."""
    text = _escape_xml(text)
    # Bold **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Inline code `text`
    text = re.sub(r'`(.+?)`', r'<font face="Courier" color="#c7254e">\1</font>', text)
    # Links [text](url) — just show text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'<u>\1</u>', text)
    return text


def _parse_table(lines: list[str], styles: dict) -> Table | None:
    """Parse markdown table lines into a reportlab Table."""
    if len(lines) < 2:
        return None
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    # Remove separator row (---)
    if len(rows) > 1 and all(set(c.strip()) <= {"-", ":", " "} for c in rows[1]):
        rows.pop(1)
    if not rows:
        return None

    header = rows[0]
    body = rows[1:]

    # Build table data with Paragraphs
    data = [[Paragraph(_inline_format(c), styles["table_header"]) for c in header]]
    for row in body:
        # Pad row if needed
        while len(row) < len(header):
            row.append("")
        data.append([Paragraph(_inline_format(c), styles["table_cell"]) for c in row[:len(header)]])

    col_count = len(header)
    available = A4[0] - 50 * mm
    col_widths = [available / col_count] * col_count

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#16213e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f8f8f8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def md_to_flowables(md_text: str) -> list:
    """Convert markdown text to a list of reportlab flowables."""
    styles = _build_styles()
    flowables: list = []
    lines = md_text.split("\n")
    i = 0
    in_code = False
    code_lines: list[str] = []

    while i < len(lines):
        line = lines[i]

        # Code block
        if line.strip().startswith("```"):
            if in_code:
                code_text = "<br/>".join(_escape_xml(l) for l in code_lines)
                flowables.append(Paragraph(code_text, styles["code"]))
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        stripped = line.strip()

        # Empty line
        if not stripped:
            i += 1
            continue

        # Page break (---)
        if stripped == "---":
            flowables.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cccccc")))
            flowables.append(Spacer(1, 6))
            i += 1
            continue

        # HTML anchor (skip)
        if stripped.startswith("<a ") and stripped.endswith(">"):
            i += 1
            continue

        # Headings
        if stripped.startswith("# ") and not stripped.startswith("## "):
            text = _inline_format(stripped[2:].strip())
            flowables.append(Paragraph(text, styles["h1"]))
            i += 1
            continue

        if stripped.startswith("## "):
            text = _inline_format(stripped[3:].strip())
            flowables.append(Paragraph(text, styles["h2"]))
            i += 1
            continue

        if stripped.startswith("### "):
            text = _inline_format(stripped[4:].strip())
            flowables.append(Paragraph(text, styles["h3"]))
            i += 1
            continue

        # Blockquote
        if stripped.startswith("> "):
            text = _inline_format(stripped[2:])
            flowables.append(Paragraph(f"<i>{text}</i>", styles["body"]))
            i += 1
            continue

        # Table detection
        if "|" in stripped and stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and "|" in lines[i].strip() and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            t = _parse_table(table_lines, styles)
            if t:
                flowables.append(Spacer(1, 4))
                flowables.append(t)
                flowables.append(Spacer(1, 4))
            continue

        # Bullet / numbered list
        bullet_match = re.match(r'^(\s*)[-*]\s+(.+)', line)
        num_match = re.match(r'^(\s*)\d+\.\s+(.+)', line)
        if bullet_match:
            text = _inline_format(bullet_match.group(2))
            flowables.append(Paragraph(f"\u2022 {text}", styles["bullet"]))
            i += 1
            continue
        if num_match:
            text = _inline_format(num_match.group(2))
            flowables.append(Paragraph(f"\u2022 {text}", styles["bullet"]))
            i += 1
            continue

        # Normal paragraph
        text = _inline_format(stripped)
        flowables.append(Paragraph(text, styles["body"]))
        i += 1

    return flowables


# --------------- PDF Generation ---------------

def generate_pdf(input_path: Path, output_path: Path):
    """Read markdown file and generate PDF."""
    print(f"[INFO] 讀取: {input_path}")
    md_text = input_path.read_text(encoding="utf-8")

    flowables = md_to_flowables(md_text)

    # Add cover page
    styles = _build_styles()
    cover = [
        Spacer(1, 80),
        Paragraph("LiangClaw", styles["title"]),
        Paragraph("阿亮老師 AI Agent 平台", styles["title"]),
        Spacer(1, 20),
        Paragraph("完整安裝佈署教學", styles["subtitle"]),
        Spacer(1, 40),
        Paragraph("多模型 × 多介面 × 80+ 教育技能", styles["subtitle"]),
        Spacer(1, 20),
        Paragraph("v1.0.0", styles["subtitle"]),
        PageBreak(),
    ]

    all_flowables = cover + flowables

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title="LiangClaw 安裝佈署教學",
        author="阿亮老師",
    )

    doc.build(all_flowables)
    print(f"[OK] PDF 產生完成: {output_path}")
    print(f"     共 {len(all_flowables)} 個元素")


# --------------- CLI ---------------

def main():
    parser = argparse.ArgumentParser(description="Markdown → PDF (中文支援)")
    parser.add_argument(
        "--input", "-i",
        default=str(Path(__file__).parent / "teaching-guide.md"),
        help="輸入 Markdown 檔案路徑",
    )
    parser.add_argument(
        "--output", "-o",
        default=str(Path(__file__).parent / "teaching-guide.pdf"),
        help="輸出 PDF 檔案路徑",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"[ERROR] 找不到輸入檔案: {input_path}")
        sys.exit(1)

    generate_pdf(input_path, output_path)


if __name__ == "__main__":
    main()
