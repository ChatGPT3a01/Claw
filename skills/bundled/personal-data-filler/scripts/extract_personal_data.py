#!/usr/bin/env python3
"""
個人資料提取腳本
用於從 JSON 檔案提取個人資訊，並支援不同的欄位映射
"""

import json
import sys
from pathlib import Path

# 預設個人資料路徑
DEFAULT_DATA_PATH = Path(__file__).parent.parent / "references" / "personal-data.json"

# 欄位映射 - 將各種可能的欄位名稱映射到標準欄位
FIELD_MAPPINGS = {
    # 姓名
    "name": ["姓名", "名字", "Name", "full_name", "fullname"],
    "phone": ["電話", "手機", "phone", "tel", "telephone", "電話號碼"],
    "address": ["地址", "住址", "address", "location"],
    "id_number": ["身分證號", "身分證", "ID", "id_number", "id"],
    "service_unit": ["服務單位", "單位", "service_unit", "department", "org"],
    "position": ["職稱", "職位", "position", "title", "job_title"],
}

def load_personal_data(data_path=None):
    """讀取個人資料"""
    if data_path is None:
        data_path = DEFAULT_DATA_PATH

    if not Path(data_path).exists():
        print(f"錯誤：找不到資料檔案 {data_path}", file=sys.stderr)
        return None

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"錯誤：JSON 格式不正確 - {e}", file=sys.stderr)
        return None

def get_field_value(data, field_name):
    """
    根據欄位名稱取得值
    支援多個可能的欄位名稱
    """
    # 直接查找
    if field_name in data:
        return data[field_name]

    # 從映射中查找
    for standard_field, aliases in FIELD_MAPPINGS.items():
        if field_name in aliases or field_name.lower() in [a.lower() for a in aliases]:
            if standard_field in data:
                return data[standard_field]

    return None

def format_data_for_display(data):
    """將資料格式化為易於查看的格式"""
    output = []
    output.append("=" * 50)
    output.append("個人資料摘要")
    output.append("=" * 50)

    for key, value in data.items():
        output.append(f"{key}: {value}")

    output.append("=" * 50)
    return "\n".join(output)

if __name__ == "__main__":
    data = load_personal_data()
    if data:
        print(format_data_for_display(data))

        # 如果有命令列參數，則查找特定欄位
        if len(sys.argv) > 1:
            field = sys.argv[1]
            value = get_field_value(data, field)
            if value:
                print(f"\n{field}: {value}")
            else:
                print(f"找不到欄位: {field}", file=sys.stderr)
    else:
        sys.exit(1)
