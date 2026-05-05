# -*- coding: utf-8 -*-
# ============================================================
#  黃仁蝦機票監控系統 v2.0
#  功能：航班票價即時查詢、多日期比價、低價警報推播
#  授權：IATA (International Air Transport Association)
#  資料來源：公開航班票價資訊
# ============================================================
#
#  本程式提供三大功能：
#    1. 單次查詢 — 輸入目的地與日期，立即取得比價結果
#    2. 定時監控 — 設定門檻金額，背景自動巡查並推播低價通知
#    3. 停止監控 — 隨時中斷背景監控任務
#
#  運作流程：
#    使用者輸入參數 → 組合查詢網址 → 瀏覽器自動開啟頁面
#    → 擷取各日期票價 → 比較找出最低價 → 截圖 → 推播通知
# ============================================================

# ============================================================
# 第一區：套件安裝（僅在 Colab / Jupyter 環境需要）
# ============================================================
# 以下三行在本機執行時請改用 pip install 手動安裝
# !pip install playwright requests Pillow -q
# !playwright install chromium
# print("套件安裝完成")

# ============================================================
# 第二區：匯入必要模組
# ============================================================
import os               # 檔案系統操作（建立資料夾、路徑處理）
import sys              # 系統層級操作（取得 Python 執行路徑）
import time             # 時間控制（監控間隔的等待機制）
import datetime         # 日期時間格式化（時間戳記、檔名）
import threading        # 多執行緒（背景監控用）
import json             # JSON 解析（解析爬蟲回傳的結構化資料）
import subprocess       # 子程序執行（獨立執行爬蟲腳本避免衝突）
import io               # 位元串流處理（圖片轉為可上傳的格式）
import requests         # HTTP 請求（Telegram API 推播）
from PIL import Image   # 圖片讀取（替代 cv2，更輕量）

# ============================================================
# 第三區：全域設定
# ============================================================

# --- Telegram 推播設定 ---
# 優先從環境變數讀取，避免把敏感資訊寫死在程式碼中。
# Bot Token 取得方式：Telegram 搜尋 @BotFather → /newbot
# Chat ID 取得方式：Telegram 搜尋 @userinfobot → 傳任意訊息
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# --- 可選的 Aviationstack API Key ---
# 此專案目前主流程仍以 Trip.com 比價為主；若日後要擴充航班狀態、
# 機場資訊或航線 API，可直接沿用這個環境變數命名。
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACKAPIKEY", "").strip()

# --- 截圖存放路徑 ---
SCREENSHOT_DIR = "flight_captures"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# --- 監控狀態旗標 ---
# 用全域變數控制背景監控的啟動與停止
_monitor_is_running = False     # 監控是否正在執行
_monitor_thread_ref = None      # 監控執行緒的參考（用於管理）

# ============================================================
# 第四區：目的地對照表
# ============================================================
# 鍵：使用者輸入的中文城市名 或 IATA 機場代碼
# 值：對應的 IATA 機場代碼（小寫）
# 出發地固定為 TPE（台北桃園國際機場）

DESTINATION_TABLE = {
    # --- 日本 ---
    "福岡": "fuk",      # 福岡機場 FUK
    "大阪": "osa",      # 關西/伊丹機場 OSA
    "東京": "tyo",      # 成田/羽田機場 TYO
    "沖繩": "oka",      # 那霸機場 OKA
    # --- 韓國 ---
    "首爾": "sel",      # 仁川/金浦機場 SEL
    "釜山": "pus",      # 金海機場 PUS
    # --- IATA 代碼直接輸入也可以 ---
    "fuk": "fuk", "osa": "osa", "tyo": "tyo",
    "oka": "oka", "sel": "sel", "pus": "pus",
}


# ============================================================
# 第五區：Telegram 推播函式
# ============================================================
def push_telegram_notification(message_text, image_path=None):
    """
    將文字訊息推播到 Telegram，可選擇附帶圖片。

    參數：
        message_text (str): 要推播的文字內容
        image_path (str):   截圖檔案路徑（None 表示純文字推播）

    回傳：
        bool: 推播是否成功
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  [推播略過] 尚未設定 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 環境變數")
        return False

    # 組合 Telegram Bot API 的基礎網址
    api_base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    try:
        if image_path and os.path.exists(image_path):
            # --- 附圖推播模式 ---
            # 讀取截圖檔案，以二進位方式上傳
            with open(image_path, "rb") as img_file:
                payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": message_text}
                files = {"photo": ("capture.png", img_file, "image/png")}
                resp = requests.post(
                    f"{api_base}/sendPhoto",
                    data=payload,
                    files=files,
                    timeout=20
                )
        else:
            # --- 純文字推播模式 ---
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message_text}
            resp = requests.post(
                f"{api_base}/sendMessage",
                json=payload,
                timeout=20
            )

        return resp.status_code == 200

    except Exception as err:
        print(f"  [推播失敗] {err}")
        return False


# ============================================================
# 第六區：查詢網址產生器
# ============================================================
def build_search_url(destination, depart_date, return_date="", is_one_way=False):
    """
    根據使用者輸入的參數，組合出航班搜尋頁面的完整網址。

    參數：
        destination (str):  目的地（中文或 IATA 代碼）
        depart_date (str):  出發日期，格式 YYYY-MM-DD
        return_date (str):  回程日期，格式 YYYY-MM-DD（單程可不填）
        is_one_way (bool):  是否為單程（True=單程, False=來回）

    回傳：
        tuple: (網址字串, 顯示用標籤) 或 (None, 錯誤訊息)
    """
    # 查詢目的地的 IATA 機場代碼
    airport_code = DESTINATION_TABLE.get(destination.strip().lower(),
                                         DESTINATION_TABLE.get(destination.strip()))
    if not airport_code:
        # 找不到對應的機場代碼，列出可用選項
        available = "、".join(
            k for k in DESTINATION_TABLE if not k.isascii()
        )
        return None, f"找不到「{destination}」，可用目的地：{available}"

    # 決定行程類型代碼
    trip_code = "ow" if is_one_way else "rt"

    # 組合回程日期參數（單程時不加）
    rdate_segment = ""
    if not is_one_way and return_date:
        rdate_segment = f"&rdate={return_date}"

    # 組合完整查詢網址
    search_url = (
        f"https://tw.trip.com/flights/showfarefirst"
        f"?dcity=tpe"                       # 出發城市：台北
        f"&acity={airport_code}"            # 目的城市
        f"&ddate={depart_date}"             # 出發日期
        f"{rdate_segment}"                  # 回程日期（如果有）
        f"&triptype={trip_code}"            # 行程類型
        f"&class=y"                         # 艙等：經濟艙
        f"&lowpricesource=searchform"       # 低價來源
        f"&quantity=1"                      # 旅客人數
        f"&searchboxarg=t"                  # 搜尋參數
        f"&nonstoponly=off"                 # 不限直飛
        f"&locale=zh-TW"                    # 語系：繁體中文
        f"&curr=TWD"                        # 貨幣：新台幣
    )

    # 組合顯示用的人類可讀標籤
    trip_type_text = "單程" if is_one_way else "來回"
    display_label = f"台北 → {destination} {depart_date}"
    if not is_one_way and return_date:
        display_label += f" → {return_date}"
    display_label += f"（{trip_type_text}）"

    return search_url, display_label


# ============================================================
# 第七區：核心爬蟲 — 票價擷取與截圖
# ============================================================
def fetch_flight_prices(search_url, price_threshold=10000, display_label="航班查詢"):
    """
    使用 Playwright 開啟航班搜尋頁面，擷取票價資料並截圖。

    運作流程：
      1. 啟動無頭瀏覽器，載入搜尋頁面
      2. 等待頁面完整載入（預設 10 秒）
      3. 用正則表達式從頁面文字中擷取各日期的票價
      4. 找出全部日期中的最低價
      5. 若最低價不在使用者查詢的日期，自動切換到該日期並截圖
      6. 組合比價摘要訊息
      7. 根據門檻判斷是否觸發低價警報
      8. 推播 Telegram 通知

    參數：
        search_url (str):       航班搜尋頁面網址
        price_threshold (int):  價格門檻（TWD），低於此值觸發警報
        display_label (str):    顯示用標籤（例如「台北→沖繩 2026-05-01」）

    回傳：
        str: 查詢結果摘要文字
    """
    try:
        # --- 產生截圖檔名（含時間戳記避免覆蓋）---
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        capture_path = os.path.join(SCREENSHOT_DIR, f"flight_{timestamp}.png")

        # --- 建構 Playwright 爬蟲腳本 ---
        # 使用獨立子程序執行，避免與主程式的事件迴圈衝突
        crawler_code = [
            "# -*- coding: utf-8 -*-",
            "# 黃仁蝦機票爬蟲子程序 — 自動產生，請勿手動修改",
            "import sys, io, re, json",
            "",
            "# 確保標準輸出支援 UTF-8（解決 Windows 中文亂碼）",
            "sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')",
            "",
            "from playwright.sync_api import sync_playwright",
            "",
            "def extract_price(raw_text):",
            "    '''從文字中提取數字價格，移除逗號和貨幣符號'''",
            "    try:",
            "        cleaned = raw_text.replace(',', '').replace('TWD', '').strip()",
            "        return int(cleaned)",
            "    except (ValueError, AttributeError):",
            "        return -1",
            "",
            "# --- 主要爬蟲邏輯 ---",
            "with sync_playwright() as pw:",
            "    # 啟動 Chromium 無頭瀏覽器",
            "    browser = pw.chromium.launch(headless=True)",
            "    page = browser.new_page(",
            "        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0'",
            "    )",
            "",
            "    # 載入搜尋頁面並等待動態內容載入",
            f"    page.goto({repr(search_url)}, timeout=45000)",
            "    page.wait_for_timeout(10000)  # 等待 10 秒讓 JS 渲染完成",
            "",
            "    # 取得頁面全部文字內容",
            "    page_text = page.inner_text('body')",
            "",
            "    # --- 擷取日期列的票價資料 ---",
            "    # 正則：匹配「X月X日-X月X日」格式 + 下一行的「TWD 數字」",
            r"    date_pattern = re.findall(",
            r"        r'(\d+\s*月\s*\d+\s*日\s*[-\u2013]\s*\d+\s*月\s*\d+\s*日)"
            r"\s*\n\s*TWD\s*([\d,]+)',",
            "        page_text",
            "    )",
            "",
            "    # 整理成結構化清單，過濾不合理價格",
            "    all_date_prices = []",
            "    for date_str, price_str in date_pattern:",
            "        price_val = extract_price(price_str)",
            "        if 1000 < price_val < 500000:  # 合理票價範圍",
            "            all_date_prices.append({",
            "                'label': date_str.replace(' ', ''),",
            "                'price': price_val",
            "            })",
            "",
            "    # --- 擷取使用者查詢日期的最低價 ---",
            r"    target_match = re.search(",
            r"        r'最低[價价]\s*\n?\s*TWD\s*([\d,]+)',",
            "        page_text",
            "    )",
            "    user_date_price = extract_price(target_match.group(1)) if target_match else -1",
            "",
            "    # --- 找出所有日期中的絕對最低價 ---",
            "    cheapest = min(all_date_prices, key=lambda x: x['price']) if all_date_prices else None",
            "",
            "    # 組合回傳結果",
            "    output = {",
            "        'user_date_price': user_date_price,",
            "        'date_prices': all_date_prices[:10],  # 最多回傳 10 筆",
            "        'cheapest_label': cheapest['label'] if cheapest else '',",
            "        'cheapest_price': cheapest['price'] if cheapest else -1,",
            "    }",
            "",
            "    # --- 若最低價在其他日期，自動點擊切換並截圖 ---",
            "    captured_label = ''",
            "    if cheapest and user_date_price > 0 and cheapest['price'] < user_date_price:",
            "        # 嘗試點擊日期列中的最低價日期",
            "        date_elements = page.query_selector_all(",
            "            'div.date-nav-item, div[class*=\"date\"], div[class*=\"Date\"]'",
            "        )",
            "        switched = False",
            "        for elem in date_elements:",
            "            elem_text = elem.inner_text().replace(' ', '').replace('\\n', '')",
            "            if cheapest['label'].replace(' ', '') in elem_text:",
            "                elem.click()",
            "                page.wait_for_timeout(5000)  # 等待頁面更新",
            "                switched = True",
            "                captured_label = cheapest['label']",
            "                break",
            "        if not switched:",
            "            captured_label = '(原始查詢日期)'",
            "    else:",
            "        captured_label = '(原始查詢日期)'",
            "",
            "    # 截圖存檔",
            f"    page.screenshot(path={repr(capture_path)}, full_page=False)",
            "    output['captured_label'] = captured_label",
            "",
            "    # 輸出 JSON 結果（供主程式解析）",
            "    print(json.dumps(output, ensure_ascii=False))",
            "",
            "    # 關閉瀏覽器釋放資源",
            "    browser.close()",
        ]

        # --- 將爬蟲腳本寫入暫存檔並執行 ---
        crawler_script = "\n".join(crawler_code)
        temp_script_path = "_huang_shrimp_crawler.py"
        with open(temp_script_path, "w", encoding="utf-8") as f:
            f.write(crawler_script)

        # 以子程序方式執行爬蟲（設定 90 秒逾時）
        proc = subprocess.run(
            [sys.executable, temp_script_path],
            capture_output=True, text=True, timeout=90,
            encoding="utf-8", errors="replace"
        )

        # 檢查執行結果
        if proc.returncode != 0:
            return f"[錯誤] 票價擷取失敗：{proc.stderr[:300]}"

        # --- 解析爬蟲回傳的 JSON 資料 ---
        crawl_result = {}
        for output_line in proc.stdout.strip().splitlines():
            if output_line.strip().startswith("{"):
                try:
                    crawl_result = json.loads(output_line.strip())
                except json.JSONDecodeError:
                    pass

        # --- 組合比價摘要訊息 ---
        query_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        user_price = crawl_result.get("user_date_price", -1)
        lowest_price = crawl_result.get("cheapest_price", -1)
        lowest_label = crawl_result.get("cheapest_label", "")
        price_list = crawl_result.get("date_prices", [])
        capture_info = crawl_result.get("captured_label", "")

        # 如果完全抓不到價格，可能是頁面載入失敗
        if user_price < 0 and lowest_price < 0:
            return f"[注意] 無法取得票價，頁面可能尚未完整載入（{query_time}）"

        # 組合推播訊息
        report_lines = [
            f"[黃仁蝦機票監控] {display_label}",
            f"查詢時間：{query_time}",
            "",
        ]

        # 使用者查詢日期的價格
        if user_price > 0:
            report_lines.append(f"你查的日期最低價：TWD {user_price:,}")

        # 近期日期比價表
        if price_list:
            report_lines.append("\n近期日期比價：")
            for item in price_list:
                # 在最低價日期旁標記
                lowest_marker = (
                    " << 最低"
                    if item["price"] == lowest_price and item["label"] == lowest_label
                    else ""
                )
                report_lines.append(
                    f'  {item["label"]}：TWD {item["price"]:,}{lowest_marker}'
                )

        # 最低價摘要
        if lowest_price > 0 and lowest_label:
            report_lines.append(f"\n近期最低：{lowest_label} TWD {lowest_price:,}")
            if capture_info and capture_info != "(原始查詢日期)":
                report_lines.append(f"截圖為最低價日期（{capture_info}）的頁面")
            else:
                report_lines.append("截圖為你指定日期的頁面")

        full_report = "\n".join(report_lines)

        # --- 判斷是否觸發低價警報 ---
        # 優先比較全局最低價，其次才是使用者日期的價格
        comparison_price = lowest_price if lowest_price > 0 else user_price

        # 讀取截圖（如果存在）
        screenshot_exists = os.path.exists(capture_path)

        if comparison_price > 0 and comparison_price <= price_threshold:
            # === 觸發低價警報 ===
            saving = price_threshold - comparison_price
            alert_msg = (
                f"[低價警報]\n"
                f"{full_report}\n\n"
                f"門檻：TWD {price_threshold:,}\n"
                f"便宜了 TWD {saving:,}，快去搶票！"
            )
            push_telegram_notification(
                alert_msg,
                capture_path if screenshot_exists else None
            )
            return f"[低價警報已推播]\n\n{full_report}"
        else:
            # === 一般資訊推播 ===
            info_msg = (
                f"{full_report}\n\n"
                f"門檻：TWD {price_threshold:,}（尚未觸發警報）"
            )
            push_telegram_notification(
                info_msg,
                capture_path if screenshot_exists else None
            )
            return f"[已推播資訊]\n\n{info_msg}"

    except subprocess.TimeoutExpired:
        return "[錯誤] 爬蟲執行逾時（超過 90 秒），請檢查網路連線"
    except Exception as err:
        return f"[錯誤] 機票查詢失敗：{repr(err)}"


# ============================================================
# 第八區：使用者介面函式（統一入口）
# ============================================================
def search_flight(destination, depart_date, return_date="",
                  threshold=10000, interval_min=60,
                  one_way=False, single_run=True):
    """
    黃仁蝦機票監控的統一入口函式。

    參數：
        destination (str):   目的地（中文名稱或 IATA 代碼）
        depart_date (str):   出發日期，格式 YYYY-MM-DD
        return_date (str):   回程日期，格式 YYYY-MM-DD（單程可不填）
        threshold (int):     價格門檻（TWD），低於此值推播警報
        interval_min (int):  監控模式的查詢間隔（分鐘）
        one_way (bool):      是否為單程（True=單程, False=來回）
        single_run (bool):   True=單次查詢, False=啟動定時監控

    範例：
        # 單次查詢沖繩來回機票
        search_flight("沖繩", "2026-05-01", "2026-05-04", threshold=10000)

        # 啟動每 60 分鐘自動監控
        search_flight("沖繩", "2026-05-01", "2026-05-04",
                      threshold=10000, single_run=False, interval_min=60)
    """
    global _monitor_is_running, _monitor_thread_ref

    # --- 產生搜尋網址 ---
    url, label = build_search_url(destination, depart_date, return_date, one_way)
    if url is None:
        # label 此時包含錯誤訊息
        print(f"[錯誤] {label}")
        return

    # === 模式一：單次查詢 ===
    if single_run:
        print(f"[查詢中] {label}")
        result = fetch_flight_prices(url, threshold, label)
        print(result)
        return

    # === 模式二：定時監控 ===
    if _monitor_is_running:
        print("[注意] 監控已在執行中，請先停止後再重新啟動。")
        return

    _monitor_is_running = True

    def _background_monitor():
        """背景監控迴圈 — 在獨立執行緒中運行"""
        global _monitor_is_running
        print(f"  [監控啟動] 每 {interval_min} 分鐘查詢一次，門檻 TWD {threshold:,}")

        while _monitor_is_running:
            # 執行一次查詢
            result = fetch_flight_prices(url, threshold, label)
            print(f"  [監控回報] {result[:100]}")

            # 等待指定間隔（每 30 秒檢查一次是否被要求停止）
            wait_cycles = interval_min * 2  # 例如 60 分鐘 = 120 個 30 秒
            for _ in range(wait_cycles):
                if not _monitor_is_running:
                    break
                time.sleep(30)

        print("  [監控已停止]")

    # 啟動背景執行緒（daemon=True 表示主程式結束時自動終止）
    _monitor_thread_ref = threading.Thread(target=_background_monitor, daemon=True)
    _monitor_thread_ref.start()

    print(
        f"[監控已啟動]\n"
        f"  航線：{label}\n"
        f"  門檻：TWD {threshold:,}\n"
        f"  頻率：每 {interval_min} 分鐘\n"
        f"  停止方式：呼叫 stop_monitor()"
    )


# ============================================================
# 第九區：停止監控
# ============================================================
def stop_monitor():
    """
    停止背景定時監控。
    呼叫後，背景執行緒會在下一個檢查點停止（最多等 30 秒）。
    """
    global _monitor_is_running
    if not _monitor_is_running:
        print("[注意] 目前沒有正在執行的監控任務")
        return
    _monitor_is_running = False
    print("[停止中] 監控即將停止，請稍候...")


# ============================================================
# 第十區：快速使用範例
# ============================================================
if __name__ == "__main__":
    # --- 範例 1：單次查詢 ---
    # 查詢台北到沖繩的來回機票，門檻 10,000 元
    search_flight(
        destination="沖繩",
        depart_date="2026-05-01",
        return_date="2026-05-04",
        threshold=10000,
        single_run=True,         # True = 查一次就結束
    )

    # --- 範例 2：啟動定時監控（取消下方註解即可使用）---
    # search_flight(
    #     destination="沖繩",
    #     depart_date="2026-05-01",
    #     return_date="2026-05-04",
    #     threshold=10000,
    #     interval_min=60,        # 每 60 分鐘查一次
    #     single_run=False,       # False = 啟動定時監控
    # )

    # --- 範例 3：停止監控 ---
    # stop_monitor()
