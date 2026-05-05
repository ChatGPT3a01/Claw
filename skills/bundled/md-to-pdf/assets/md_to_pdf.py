#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 轉 PDF 工具（純 Python 備案）
========================================
當 pandoc 不可用時的替代方案。
使用 markdown + weasyprint 將 Markdown 轉為 PDF。

依賴套件安裝：
  pip install markdown weasyprint pyyaml

注意：WeasyPrint 在 Windows 上需要 GTK 相關依賴。
建議優先使用 pandoc 方案。
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("❌ 請先安裝 markdown：pip install markdown")
    sys.exit(1)


# ─────────────────────────────────────────────
# YAML Front Matter 處理
# ─────────────────────────────────────────────

def extract_front_matter(md_text: str) -> tuple[dict, str]:
    """從 Markdown 中提取 YAML Front Matter。"""
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, md_text, re.DOTALL)
    if not match:
        return {}, md_text
    yaml_str = match.group(1)
    content = md_text[match.end():]
    try:
        import yaml
        metadata = yaml.safe_load(yaml_str) or {}
    except Exception:
        metadata = {}
    return metadata, content


# ─────────────────────────────────────────────
# HTML 模板
# ─────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
@page {{
  size: {page_size};
  margin: 2.5cm;
}}
body {{
  font-family: "{font}", "Microsoft JhengHei", "PingFang TC", "Noto Sans CJK TC", sans-serif;
  font-size: 11pt;
  line-height: 1.6;
  color: #1a1a2e;
}}
h1 {{ font-size: 22pt; color: #1a1a2e; border-bottom: 2px solid #ddd; padding-bottom: 0.3em; }}
h2 {{ font-size: 18pt; color: #2d2d44; }}
h3 {{ font-size: 15pt; color: #3d3d5c; }}
h4 {{ font-size: 13pt; color: #4a4a6a; }}
h5, h6 {{ font-size: 11pt; color: #5a5a7a; }}
table {{
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}}
th, td {{
  border: 1px solid #ccc;
  padding: 8px 12px;
  text-align: left;
}}
th {{
  background-color: #f5f5f5;
  font-weight: bold;
}}
pre {{
  background-color: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 4px;
  padding: 12px;
  overflow-x: auto;
  font-size: 9.5pt;
}}
code {{
  font-family: "Consolas", "Monaco", monospace;
  font-size: 9.5pt;
}}
p > code {{
  background-color: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  color: #c7254e;
}}
blockquote {{
  border-left: 4px solid #ddd;
  margin: 1em 0;
  padding: 0.5em 1em;
  color: #555;
  font-style: italic;
}}
hr {{
  border: none;
  border-top: 1px solid #ddd;
  margin: 2em 0;
}}
a {{
  color: #0563c1;
  text-decoration: underline;
}}
img {{
  max-width: 100%;
  height: auto;
}}
</style>
</head>
<body>
{content}
</body>
</html>"""


# ─────────────────────────────────────────────
# 轉換函式
# ─────────────────────────────────────────────

def convert_md_to_pdf(
    md_path: Path,
    output_path: Path | None = None,
    font_name: str = "微軟正黑體",
    page_size: str = "A4",
) -> Path:
    """將 Markdown 檔案轉為 PDF。"""
    if not md_path.exists():
        raise FileNotFoundError(f"找不到檔案：{md_path}")

    if output_path is None:
        output_path = md_path.with_suffix(".pdf")

    print(f"\n🔄 轉換：{md_path.name}")

    # 讀取 Markdown
    md_text = md_path.read_text(encoding="utf-8")
    metadata, content = extract_front_matter(md_text)
    title = metadata.get("title", md_path.stem)

    # Markdown → HTML
    extensions = ["tables", "fenced_code", "codehilite", "toc", "sane_lists", "smarty"]
    html_content = markdown.markdown(content, extensions=extensions)

    # 組裝完整 HTML
    full_html = HTML_TEMPLATE.format(
        title=title,
        font=font_name,
        page_size=page_size,
        content=html_content,
    )

    # HTML → PDF（使用 WeasyPrint）
    try:
        from weasyprint import HTML as WeasyHTML
        WeasyHTML(string=full_html, base_url=str(md_path.parent)).write_pdf(str(output_path))
        print(f"  ✅ 已輸出：{output_path}")
        return output_path
    except ImportError:
        print("  ⚠️  WeasyPrint 未安裝，嘗試其他方案...")

    # 備案：存為 HTML（提示使用者用瀏覽器列印為 PDF）
    html_output = output_path.with_suffix(".html")
    html_output.write_text(full_html, encoding="utf-8")
    print(f"  📄 已輸出 HTML：{html_output}")
    print(f"  💡 請用瀏覽器開啟後 Ctrl+P 列印為 PDF")
    return html_output


def batch_convert(
    folder: Path,
    output_folder: Path | None = None,
    font_name: str = "微軟正黑體",
    page_size: str = "A4",
):
    """批次轉換資料夾內所有 .md。"""
    md_files = list(folder.glob("*.md"))
    if not md_files:
        print(f"⚠️  在 {folder} 中找不到任何 .md 檔案。")
        return

    out_dir = output_folder or folder
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"📂 批次轉換 {len(md_files)} 個 Markdown，輸出到：{out_dir}")
    success, failed = 0, []

    for md_file in md_files:
        out = out_dir / md_file.with_suffix(".pdf").name
        try:
            convert_md_to_pdf(md_file, out, font_name=font_name, page_size=page_size)
            success += 1
        except Exception as e:
            print(f"  ❌ 失敗：{md_file.name}，原因：{e}")
            failed.append(md_file.name)

    print(f"\n✅ 完成：{success}/{len(md_files)} 個成功")
    if failed:
        print("❌ 失敗清單：" + ", ".join(failed))


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Markdown 轉 PDF 工具（純 Python）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  python md_to_pdf.py report.md
  python md_to_pdf.py report.md -o output.pdf
  python md_to_pdf.py report.md --font "標楷體" --page-size A4
  python md_to_pdf.py ./docs/ --batch -o ./output/
        """,
    )
    parser.add_argument("input", help=".md 檔案路徑或資料夾路徑")
    parser.add_argument("-o", "--output", help="輸出 .pdf 路徑或輸出資料夾")
    parser.add_argument("--font", default="微軟正黑體", help="中文字型（預設：微軟正黑體）")
    parser.add_argument("--page-size", default="A4", help="紙張大小（預設：A4）")
    parser.add_argument("--batch", action="store_true", help="批次轉換")

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None

    if args.batch or input_path.is_dir():
        if not input_path.is_dir():
            print(f"❌ 批次模式需要指定資料夾")
            sys.exit(1)
        batch_convert(input_path, output_path, font_name=args.font, page_size=args.page_size)
    else:
        if not input_path.suffix.lower() == ".md":
            print(f"❌ 輸入檔案必須是 .md 格式")
            sys.exit(1)
        convert_md_to_pdf(input_path, output_path, font_name=args.font, page_size=args.page_size)


if __name__ == "__main__":
    main()
