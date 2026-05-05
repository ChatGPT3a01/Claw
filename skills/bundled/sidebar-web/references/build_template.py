#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教師手冊網站 - 內容建構腳本
讀取所有教師手冊 Markdown 檔案，產生 data/units.js
"""

import os
import json
import re

# 教師手冊根目錄（相對於此腳本的上一層）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MANUAL_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "data", "units.js")

# 單元定義（順序、資料夾名、檔名、顯示名稱、是否為子單元）
UNITS = [
    {
        "id": "unit00",
        "folder": "單元00_Vibecoding氛圍編程",
        "file": "00-Vibecoding氛圍編程.md",
        "title": "單元00：Vibe Coding 氛圍編程",
        "shortTitle": "00 Vibe Coding",
        "parent": None
    },
    {
        "id": "unit01",
        "folder": "單元01_獲取AI通關鑰匙_API_Key",
        "file": "01-獲取AI通關鑰匙_API_Key.md",
        "title": "單元01：獲取 AI 通關鑰匙 — API Key",
        "shortTitle": "01 API Key",
        "parent": None
    },
    {
        "id": "unit02",
        "folder": "單元02_地端與雲端串接概念",
        "file": "02-地端與雲端串接概念.md",
        "title": "單元02：地端與雲端串接概念",
        "shortTitle": "02 地端與雲端",
        "parent": None
    },
    {
        "id": "unit03",
        "folder": "單元03_打造RAG知識庫問答平台",
        "file": "03-打造RAG知識庫問答平台.md",
        "title": "單元03：打造 RAG 知識庫問答平台",
        "shortTitle": "03 RAG 知識庫",
        "parent": None
    },
    {
        "id": "unit04",
        "folder": "單元04_AI智慧助理多功能整合平台",
        "file": "04-AI智慧助理多功能整合平台.md",
        "title": "單元04：AI 智慧助理多功能整合平台",
        "shortTitle": "04 AI 智慧助理",
        "parent": None
    },
    {
        "id": "unit05",
        "folder": "單元05_AI_Prompt互動提示詞生成系統",
        "file": "05-AI_Prompt互動提示詞生成系統.md",
        "title": "單元05：AI Prompt 互動提示詞生成系統",
        "shortTitle": "05 Prompt 生成",
        "parent": None
    },
    {
        "id": "unit06",
        "folder": "單元06_AI生成表單系統",
        "file": "06-AI生成表單系統.md",
        "title": "單元06：AI 問卷自動生成系統",
        "shortTitle": "06 表單系統",
        "parent": None
    },
    {
        "id": "unit07",
        "folder": "單元07_AI預約系統",
        "file": "07-AI預約系統.md",
        "title": "單元07：AI 智能預約助理系統",
        "shortTitle": "07 預約系統",
        "parent": None
    },
    {
        "id": "unit08",
        "folder": "單元08_Line聊天機器人",
        "file": "08-Line聊天機器人.md",
        "title": "單元08：LINE Bot 智慧客服生成器",
        "shortTitle": "08 LINE Bot",
        "parent": None
    },
    {
        "id": "unit09",
        "folder": "單元09_YT影片建置測驗系統",
        "file": "09-YT影片建置測驗系統.md",
        "title": "單元09：YouTube 影片互動問答系統",
        "shortTitle": "09 YT 測驗",
        "parent": None
    },
    {
        "id": "unit10",
        "folder": "單元10_Ollama下載AI模型串接對話平台",
        "file": "10-Ollama下載AI模型串接對話平台.md",
        "title": "單元10：Ollama 下載 AI 模型串接對話平台",
        "shortTitle": "10 Ollama",
        "parent": None
    },
    {
        "id": "unit11",
        "folder": "單元11_AI生成簡報系統",
        "file": "11-AI生成簡報系統.md",
        "title": "單元11：AI 生成簡報系統",
        "shortTitle": "11 簡報系統",
        "parent": None
    },
    {
        "id": "unit12",
        "folder": "單元12_AI_Music音樂視覺化系統",
        "file": "12-AI_Music音樂視覺化系統.md",
        "title": "單元12：AI Music 音樂視覺化系統",
        "shortTitle": "12 Music 視覺化",
        "parent": None
    },
    {
        "id": "unit13",
        "folder": "單元13_AI建置到班打卡系統",
        "file": "13-AI建置到班打卡系統.md",
        "title": "單元13：AI 建置到班打卡系統",
        "shortTitle": "13 打卡系統",
        "parent": None
    },
    {
        "id": "unit14",
        "folder": None,
        "file": None,
        "title": "單元14：Claude AI 平台開發完整版",
        "shortTitle": "14 Claude AI",
        "parent": None,
        "isGroup": True
    },
    {
        "id": "unit14a",
        "folder": "單元14_Claude_AI平台開發完整版",
        "file": "14A-Claude_AI助手完全指南.md",
        "title": "14-A：Claude AI 助手完全指南（Web 版）",
        "shortTitle": "14A Web 版",
        "parent": "unit14"
    },
    {
        "id": "unit14b",
        "folder": "單元14_Claude_AI平台開發完整版",
        "file": "14B-Claude_CLI命令列版教學.md",
        "title": "14-B：Claude CLI 命令列版教學",
        "shortTitle": "14B CLI 版",
        "parent": "unit14"
    },
    {
        "id": "unit14c",
        "folder": "單元14_Claude_AI平台開發完整版",
        "file": "14C-Claude_Desktop桌面版教學.md",
        "title": "14-C：Claude Desktop 桌面版教學",
        "shortTitle": "14C Desktop 版",
        "parent": "unit14"
    },
    {
        "id": "unit14d",
        "folder": "單元14_Claude_AI平台開發完整版",
        "file": "14D-Claude_MCP專區.md",
        "title": "14-D：Claude MCP 專區",
        "shortTitle": "14D MCP",
        "parent": "unit14"
    },
]


def read_md_file(folder, filename):
    """讀取 Markdown 檔案內容"""
    filepath = os.path.join(MANUAL_DIR, folder, filename)
    if not os.path.exists(filepath):
        print(f"  [WARN] File not found: {filepath}")
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def escape_js_string(s):
    """將字串轉義為安全的 JS 字串（用於 JSON）"""
    return json.dumps(s, ensure_ascii=False)


def build_units_js():
    """產生 data/units.js"""
    print("=" * 60)
    print("Teacher Manual Website - Content Builder")
    print("=" * 60)

    units_data = []

    for unit in UNITS:
        is_group = unit.get("isGroup", False)

        if is_group:
            # 群組標題（單元14），不含內容
            units_data.append({
                "id": unit["id"],
                "title": unit["title"],
                "shortTitle": unit["shortTitle"],
                "parent": unit["parent"],
                "isGroup": True,
                "content": ""
            })
            print(f"  [GROUP] {unit['title']}")
        else:
            # 一般單元，讀取 md 內容
            content = read_md_file(unit["folder"], unit["file"])
            units_data.append({
                "id": unit["id"],
                "title": unit["title"],
                "shortTitle": unit["shortTitle"],
                "parent": unit["parent"],
                "isGroup": False,
                "content": content
            })
            lines = content.count("\n") + 1 if content else 0
            print(f"  [OK] {unit['title']} ({lines} lines)")

    # 產生 JS 檔案
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("// 此檔案由 build.py 自動產生，請勿手動編輯\n")
        f.write("// 產生時間：" + __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
        f.write("const UNITS_DATA = ")
        json.dump(units_data, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"\n[DONE] Output: {OUTPUT_FILE}")
    print(f"  Size: {file_size / 1024:.1f} KB")
    print(f"  Units: {len(units_data)}")


if __name__ == "__main__":
    build_units_js()
