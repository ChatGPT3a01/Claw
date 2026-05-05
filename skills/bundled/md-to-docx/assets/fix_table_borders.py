#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 Word (.docx) 表格邊框
===========================
pandoc --reference-doc 不會繼承範本的表格邊框樣式，
此腳本後處理 .docx 檔案，為所有表格加上可見邊框。

依賴：僅使用 Python 標準庫（zipfile, re），無需額外安裝。

用法：
  # 修復單一檔案
  python fix_table_borders.py document.docx

  # 修復資料夾內所有 .docx（遞迴搜尋 **/book/*.docx）
  python fix_table_borders.py ./my_book/

  # 修復資料夾內所有 .docx（不限 book 子目錄）
  python fix_table_borders.py ./my_docs/ --all

  # 自訂邊框顏色與粗細
  python fix_table_borders.py document.docx --color 999999 --size 6
"""

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile


def make_borders_xml(color: str = "888888", size: str = "6") -> str:
    """產生表格邊框 XML 片段。"""
    attrs = f'w:val="single" w:sz="{size}" w:space="0" w:color="{color}"'
    return (
        f"<w:tblBorders>"
        f"<w:top {attrs}/>"
        f"<w:left {attrs}/>"
        f"<w:bottom {attrs}/>"
        f"<w:right {attrs}/>"
        f"<w:insideH {attrs}/>"
        f"<w:insideV {attrs}/>"
        f"</w:tblBorders>"
    )


def make_cell_borders_xml(color: str = "888888", size: str = "6") -> str:
    """產生儲存格邊框 XML 片段。"""
    attrs = f'w:val="single" w:sz="{size}" w:space="0" w:color="{color}"'
    return (
        f"<w:tcBorders>"
        f"<w:top {attrs}/>"
        f"<w:left {attrs}/>"
        f"<w:bottom {attrs}/>"
        f"<w:right {attrs}/>"
        f"</w:tcBorders>"
    )


def fix_table_borders(docx_path: str, color: str = "888888", size: str = "6") -> int:
    """
    修復單一 .docx 檔案的表格邊框。

    回傳修復的表格數量（0 表示無表格需修復，-1 表示錯誤）。
    """
    borders = make_borders_xml(color, size)
    cell_borders = make_cell_borders_xml(color, size)

    try:
        # 讀取 docx（ZIP 格式）
        with zipfile.ZipFile(docx_path, "r") as zin:
            names = zin.namelist()
            if "word/document.xml" not in names:
                return 0

            xml = zin.read("word/document.xml").decode("utf-8")

            count = 0

            # 1. 替換已有的 tblBorders
            new_xml, n = re.subn(
                r"<w:tblBorders>[\s\S]*?</w:tblBorders>",
                borders,
                xml,
            )
            count += n
            xml = new_xml

            # 2. 在沒有 tblBorders 的 tblPr 中加入
            def add_tbl_borders(m):
                nonlocal count
                inner = m.group(0)
                if "tblBorders" in inner:
                    return inner
                count += 1
                return inner.replace("</w:tblPr>", borders + "</w:tblPr>")

            xml = re.sub(r"<w:tblPr>[\s\S]*?</w:tblPr>", add_tbl_borders, xml)

            # 3. 為每個 tcPr 加上 cell borders
            def add_cell_borders(m):
                nonlocal count
                inner = m.group(0)
                if "tcBorders" in inner:
                    return inner
                count += 1
                return inner.replace("</w:tcPr>", cell_borders + "</w:tcPr>")

            xml = re.sub(r"<w:tcPr>[\s\S]*?</w:tcPr>", add_cell_borders, xml)

            if count == 0:
                return 0

            # 寫回新的 docx
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".docx")
            os.close(tmp_fd)

            with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
                for name in names:
                    if name == "word/document.xml":
                        zout.writestr(name, xml.encode("utf-8"))
                    else:
                        zout.writestr(name, zin.read(name))

        # 替換原始檔案
        shutil.move(tmp_path, docx_path)
        return count

    except Exception as e:
        print(f"  錯誤: {e}", file=sys.stderr)
        return -1


def find_docx_files(folder: str, book_only: bool = True) -> list:
    """遞迴搜尋 .docx 檔案。"""
    results = []
    for root, dirs, files in os.walk(folder):
        # 跳過 node_modules 等
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "__pycache__")]
        for f in sorted(files):
            if f.endswith(".docx") and not f.startswith("~"):
                full = os.path.join(root, f)
                if book_only and "book" not in full:
                    continue
                results.append(full)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="修復 Word (.docx) 表格邊框",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  python fix_table_borders.py report.docx
  python fix_table_borders.py ./my_book/
  python fix_table_borders.py ./docs/ --all --color 666666 --size 8
        """,
    )
    parser.add_argument("input", help=".docx 檔案路徑或資料夾路徑")
    parser.add_argument("--all", action="store_true", help="搜尋所有 .docx（不限 book 子目錄）")
    parser.add_argument("--color", default="888888", help="邊框顏色（預設 888888）")
    parser.add_argument("--size", default="6", help="邊框粗細（預設 6）")
    args = parser.parse_args()

    target = args.input

    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        files = find_docx_files(target, book_only=not args.all)
    else:
        print(f"找不到：{target}")
        sys.exit(1)

    print(f"找到 {len(files)} 個 .docx\n")

    ok, skip, fail = 0, 0, 0
    for f in files:
        name = os.path.basename(f)
        result = fix_table_borders(f, color=args.color, size=args.size)
        if result > 0:
            print(f"  ✅ {name} — 修復 {result} 處")
            ok += 1
        elif result == 0:
            print(f"  ⏭️  {name} — 無表格")
            skip += 1
        else:
            fail += 1

    print(f"\n完成: {ok} 修復, {skip} 跳過, {fail} 失敗")


if __name__ == "__main__":
    main()
