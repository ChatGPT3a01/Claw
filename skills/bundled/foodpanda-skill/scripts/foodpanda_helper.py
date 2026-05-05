# foodpanda_helper.py
# -*- coding: utf-8 -*-

"""
Foodpanda AI 外送點餐助理 - 智慧推薦引擎
==========================================

功能：
1. 從 restaurants.json 載入餐廳資料
2. 根據多維度條件篩選餐廳與餐點
3. 智慧預算分配（主餐 + 配菜 + 飲料）
4. 多人份量估算與組合推薦
5. 產出結構化的建議點餐清單

安全說明：
- 不直接連接 foodpanda 付款流程
- 不儲存帳號密碼
- 適合教學、展示、CLI 測試、LINE Bot 前置整理

用法：
  python foodpanda_helper.py '{"location":"新北市板橋區","budget":300,...}'
  python foodpanda_helper.py --demo          # 執行所有示範案例
  python foodpanda_helper.py --interactive   # 互動式問答模式
"""

import json
import sys
import os
import io
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# 修正 Windows 終端機中文輸出編碼
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ============================================================
# 資料模型
# ============================================================

@dataclass
class MenuItem:
    name: str
    price: int
    item_type: str  # main, side, soup, drink
    features: List[str] = field(default_factory=list)
    calories: int = 0
    quantity: int = 1

    @property
    def subtotal(self) -> int:
        return self.price * self.quantity


@dataclass
class Restaurant:
    id: str
    name: str
    location: str
    categories: List[str]
    tags: List[str]
    rating: float
    delivery_fee: int
    min_order: int
    fast_delivery: bool
    chain: bool
    items: List[MenuItem]


@dataclass
class UserRequest:
    location: str = ""
    budget: int = 200
    meal_time: str = ""  # breakfast, lunch, dinner, late_night, afternoon_tea
    category: List[str] = field(default_factory=list)
    avoid: List[str] = field(default_factory=list)
    people: int = 1
    drink: bool = False
    fast_delivery: bool = False
    chain_ok: bool = True

    @property
    def budget_per_person(self) -> int:
        return max(1, self.budget // max(1, self.people))

    @property
    def meal_time_display(self) -> str:
        mapping = {
            "breakfast": "早餐", "lunch": "午餐", "dinner": "晚餐",
            "late_night": "宵夜", "afternoon_tea": "下午茶"
        }
        return mapping.get(self.meal_time, self.meal_time or "未指定")


# ============================================================
# 資料載入
# ============================================================

def load_restaurants(data_path: Optional[str] = None) -> List[Restaurant]:
    """從 JSON 檔載入餐廳資料"""
    if data_path is None:
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "restaurants.json")

    if not os.path.exists(data_path):
        print(f"[警告] 找不到資料檔：{data_path}，使用內建範例資料")
        return get_builtin_restaurants()

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    restaurants = []
    for r in data.get("restaurants", []):
        items = [
            MenuItem(
                name=item["name"],
                price=item["price"],
                item_type=item["type"],
                features=item.get("features", []),
                calories=item.get("calories", 0)
            )
            for item in r.get("items", [])
        ]
        restaurants.append(Restaurant(
            id=r.get("id", ""),
            name=r["name"],
            location=r.get("location", ""),
            categories=r.get("categories", []),
            tags=r.get("tags", []),
            rating=r.get("rating", 0),
            delivery_fee=r.get("delivery_fee", 0),
            min_order=r.get("min_order", 0),
            fast_delivery=r.get("fast_delivery", False),
            chain=r.get("chain", False),
            items=items
        ))
    return restaurants


def get_builtin_restaurants() -> List[Restaurant]:
    """內建的基本範例資料（當 JSON 不存在時使用）"""
    return [
        Restaurant("b01", "好飽便當屋", "新北市板橋區",
                   ["便當", "飯類"], ["快速出餐", "高CP值"], 4.5, 30, 100, True, False,
                   [
                       MenuItem("雞腿便當", 135, "main", ["飯類", "不辣"], 650),
                       MenuItem("排骨便當", 125, "main", ["飯類", "炸物"], 700),
                       MenuItem("燙青菜", 40, "side", ["清爽", "素食"], 80),
                       MenuItem("味噌湯", 30, "soup", ["湯品"], 60),
                   ]),
        Restaurant("b02", "宵夜小館", "新北市板橋區",
                   ["麵類", "宵夜"], ["宵夜", "平價"], 4.1, 20, 60, True, False,
                   [
                       MenuItem("陽春麵", 65, "main", ["麵類"], 380),
                       MenuItem("鹽酥雞", 90, "main", ["炸物"], 550),
                       MenuItem("貢丸湯", 40, "soup", ["湯品"], 100),
                   ]),
    ]


# ============================================================
# 篩選引擎
# ============================================================

def matches_location(user_loc: str, restaurant_loc: str) -> bool:
    """地區比對（模糊匹配）"""
    if not user_loc:
        return True
    user_loc = user_loc.replace("台", "臺")
    restaurant_loc = restaurant_loc.replace("台", "臺")
    # 雙向包含
    return user_loc in restaurant_loc or restaurant_loc in user_loc


def has_avoid_conflict(item: MenuItem, avoid_list: List[str]) -> bool:
    """檢查餐點是否踩到禁忌"""
    if not avoid_list:
        return False
    text = " ".join(item.features + [item.name])
    for avoid in avoid_list:
        if avoid in text:
            return True
    return False


def matches_meal_time(restaurant: Restaurant, meal_time: str) -> bool:
    """依時段篩選（寬鬆匹配）"""
    if not meal_time:
        return True
    tags_text = " ".join(restaurant.categories + restaurant.tags)
    time_keywords = {
        "breakfast": ["早餐", "早午餐", "輕食"],
        "lunch": ["便當", "飯類", "麵類", "健康餐", "午餐"],
        "dinner": ["便當", "飯類", "麵類", "湯品", "晚餐"],
        "late_night": ["宵夜", "深夜", "麵類"],
        "afternoon_tea": ["飲料", "手搖", "下午茶", "甜點", "輕食"],
    }
    keywords = time_keywords.get(meal_time, [])
    if not keywords:
        return True
    return any(kw in tags_text for kw in keywords)


def category_score(user_cats: List[str], restaurant: Restaurant) -> int:
    """計算分類匹配分數"""
    if not user_cats:
        return 1
    combined = " ".join(restaurant.categories + restaurant.tags +
                        [item.name for item in restaurant.items])
    score = 0
    for cat in user_cats:
        if cat in combined:
            score += 2
    return score


# ============================================================
# 推薦引擎
# ============================================================

def plan_combo(restaurant: Restaurant, request: UserRequest) -> Optional[Dict[str, Any]]:
    """為單間餐廳規劃最佳組合"""
    budget = request.budget
    people = request.people
    avoid = request.avoid

    # 過濾掉禁忌餐點
    valid_items = [item for item in restaurant.items if not has_avoid_conflict(item, avoid)]
    if not valid_items:
        return None

    mains = [i for i in valid_items if i.item_type == "main"]
    sides = [i for i in valid_items if i.item_type in ("side", "soup")]
    drinks = [i for i in valid_items if i.item_type == "drink"]

    if not mains:
        # 如果是飲料店，沒有主餐也可以
        if drinks and request.drink:
            pass
        else:
            return None

    combo_items: List[Dict[str, Any]] = []
    total = 0

    if mains:
        # 每人一份主餐（選最接近人均預算的）
        budget_per = request.budget_per_person
        mains_sorted = sorted(mains, key=lambda x: abs(x.price - budget_per * 0.7))

        for i in range(people):
            # 輪流選不同主餐增加多樣性
            pick = mains_sorted[i % len(mains_sorted)]
            if total + pick.price <= budget:
                combo_items.append({
                    "name": pick.name, "price": pick.price,
                    "type": "main", "qty": 1
                })
                total += pick.price

        # 餘額補配菜/湯品
        if sides:
            sides_sorted = sorted(sides, key=lambda x: x.price)
            for side in sides_sorted:
                if total + side.price <= budget:
                    combo_items.append({
                        "name": side.name, "price": side.price,
                        "type": "side", "qty": 1
                    })
                    total += side.price
                    break  # 先加一個就好

    # 飲料
    if request.drink and drinks:
        drinks_sorted = sorted(drinks, key=lambda x: x.price)
        for i in range(people):
            pick = drinks_sorted[i % len(drinks_sorted)]
            if total + pick.price <= budget:
                combo_items.append({
                    "name": pick.name, "price": pick.price,
                    "type": "drink", "qty": 1
                })
                total += pick.price
    elif not mains and drinks:
        # 純飲料店模式
        drinks_sorted = sorted(drinks, key=lambda x: x.price)
        for i in range(people):
            pick = drinks_sorted[i % len(drinks_sorted)]
            if total + pick.price <= budget:
                combo_items.append({
                    "name": pick.name, "price": pick.price,
                    "type": "drink", "qty": 1
                })
                total += pick.price

    if not combo_items:
        return None

    # 合併相同品項
    merged = merge_combo_items(combo_items)

    return {
        "restaurant": restaurant.name,
        "location": restaurant.location,
        "rating": restaurant.rating,
        "delivery_fee": restaurant.delivery_fee,
        "tags": restaurant.tags,
        "combo": merged,
        "food_total": total,
        "grand_total": total + restaurant.delivery_fee,
        "remaining": budget - total - restaurant.delivery_fee,
    }


def merge_combo_items(items: List[Dict]) -> List[Dict]:
    """合併相同品項"""
    merged: Dict[str, Dict] = {}
    for item in items:
        key = item["name"]
        if key in merged:
            merged[key]["qty"] += item["qty"]
        else:
            merged[key] = dict(item)
    return list(merged.values())


def recommend(request: UserRequest, restaurants: List[Restaurant]) -> List[Dict[str, Any]]:
    """主推薦流程"""
    candidates = []

    for r in restaurants:
        # 基本篩選
        if not matches_location(request.location, r.location):
            continue
        if request.fast_delivery and not r.fast_delivery:
            continue
        if not request.chain_ok and r.chain:
            continue
        if not matches_meal_time(r, request.meal_time):
            continue

        # 計算分類匹配分數
        score = category_score(request.category, r)

        # 規劃組合
        combo = plan_combo(r, request)
        if combo is None:
            continue

        # 檢查最低消費
        if combo["food_total"] < r.min_order:
            continue

        combo["match_score"] = score
        combo["reason"] = build_reason(r, combo, request)
        candidates.append(combo)

    # 排序：匹配分數高 → 評分高 → 總價低
    candidates.sort(key=lambda x: (-x["match_score"], -x.get("rating", 0), x["grand_total"]))
    return candidates[:5]


def build_reason(restaurant: Restaurant, combo: Dict, request: UserRequest) -> str:
    """產出推薦原因"""
    reasons = []

    if request.category:
        matched = [c for c in request.category
                   if c in " ".join(restaurant.categories + restaurant.tags)]
        if matched:
            reasons.append(f"符合偏好：{'、'.join(matched)}")

    if request.avoid:
        reasons.append(f"已避開：{'、'.join(request.avoid)}")

    if restaurant.fast_delivery:
        reasons.append("快速出餐")

    if restaurant.rating >= 4.5:
        reasons.append(f"高評價 {restaurant.rating} 分")
    elif restaurant.rating >= 4.0:
        reasons.append(f"評價 {restaurant.rating} 分")

    tag_highlights = [t for t in restaurant.tags if t not in request.category][:3]
    if tag_highlights:
        reasons.append(f"特色：{'、'.join(tag_highlights)}")

    return "；".join(reasons) if reasons else "綜合推薦"


# ============================================================
# 輸出格式化
# ============================================================

def format_output(request: UserRequest, results: List[Dict[str, Any]]) -> str:
    """產出完整的推薦報告"""
    lines = []

    # 標題
    lines.append("=" * 50)
    lines.append("  Foodpanda AI 外送助理 - 點餐建議報告")
    lines.append("=" * 50)
    lines.append("")

    # 需求摘要
    lines.append("【需求摘要】")
    lines.append(f"  用餐人數：{request.people} 人")
    lines.append(f"  總預算　：{request.budget} 元（約每人 {request.budget_per_person} 元）")
    lines.append(f"  地區　　：{request.location or '未指定'}")
    lines.append(f"  用餐時段：{request.meal_time_display}")
    lines.append(f"  偏好　　：{'、'.join(request.category) if request.category else '未指定'}")
    lines.append(f"  禁忌　　：{'、'.join(request.avoid) if request.avoid else '無'}")
    lines.append(f"  加點飲料：{'是' if request.drink else '否'}")
    lines.append(f"  快速送達：{'是' if request.fast_delivery else '不限'}")
    lines.append("")

    if not results:
        lines.append("【推薦結果】")
        lines.append("  目前找不到完全符合條件的推薦。")
        lines.append("  建議放寬以下條件之一：")
        lines.append("  - 提高預算")
        lines.append("  - 減少禁忌限制")
        lines.append("  - 擴大搜尋地區")
        lines.append("  - 取消快速送達限制")
        return "\n".join(lines)

    # 推薦清單
    lines.append(f"【推薦清單】共找到 {len(results)} 個方案")
    lines.append("-" * 50)

    for idx, rec in enumerate(results, 1):
        star = " *" if idx == 1 else ""
        lines.append(f"方案 {idx}{star}：{rec['restaurant']}")
        lines.append(f"  評價：{'*' * int(rec.get('rating', 0))} {rec.get('rating', '-')} 分")
        lines.append(f"  推薦原因：{rec['reason']}")
        lines.append(f"  建議組合：")

        for item in rec["combo"]:
            type_icon = {"main": "M", "side": "S", "soup": "S", "drink": "D"}.get(item["type"], " ")
            lines.append(f"    [{type_icon}] {item['name']} x{item['qty']}　${item['price'] * item['qty']}")

        lines.append(f"  餐點小計：${rec['food_total']}")
        lines.append(f"  外送費　：${rec['delivery_fee']}")
        lines.append(f"  預估總計：${rec['grand_total']}")
        remaining = rec.get('remaining', 0)
        if remaining > 0:
            lines.append(f"  剩餘預算：${remaining}")
        elif remaining < 0:
            lines.append(f"  超出預算：${abs(remaining)}（含外送費）")
        lines.append("")

    # 最佳推薦
    best = results[0]
    lines.append("=" * 50)
    lines.append("【最佳推薦】")
    lines.append(f"  店家：{best['restaurant']}")
    combo_names = [f"{item['name']}x{item['qty']}" for item in best["combo"]]
    lines.append(f"  組合：{' + '.join(combo_names)}")
    lines.append(f"  預估總價：${best['grand_total']}（含外送費 ${best['delivery_fee']}）")
    lines.append("")

    # 提醒
    lines.append("【使用提醒】")
    lines.append("  - 以上為 AI 協助整理之推薦結果")
    lines.append("  - 實際餐點、價格、運費與優惠請以 foodpanda 平台顯示為準")
    lines.append("  - 請自行至平台確認後下單")
    lines.append(f"  - 平台連結：https://www.foodpanda.com.tw/")
    lines.append("=" * 50)

    return "\n".join(lines)


def format_json(request: UserRequest, results: List[Dict[str, Any]]) -> str:
    """產出 JSON 格式（給程式串接用）"""
    output = {
        "request": {
            "location": request.location,
            "budget": request.budget,
            "meal_time": request.meal_time_display,
            "category": request.category,
            "avoid": request.avoid,
            "people": request.people,
            "drink": request.drink,
            "budget_per_person": request.budget_per_person,
        },
        "recommendations": results,
        "best_pick": results[0] if results else None,
        "note": "此結果為建議清單，實際價格與外送費請以 foodpanda 平台顯示為準。",
        "platform_url": "https://www.foodpanda.com.tw/",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


# ============================================================
# 互動模式
# ============================================================

def interactive_mode(restaurants: List[Restaurant]):
    """互動式問答點餐"""
    print("=" * 50)
    print("  Foodpanda AI 外送助理 - 互動模式")
    print("  輸入 'quit' 或 'exit' 結束")
    print("=" * 50)
    print()

    while True:
        try:
            print("請告訴我你的用餐需求（或輸入 quit 離開）：")
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再見！祝用餐愉快！")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("再見！祝用餐愉快！")
            break

        if not user_input:
            continue

        # 從自然語言解析需求（簡易版）
        request = parse_natural_language(user_input)
        results = recommend(request, restaurants)
        print()
        print(format_output(request, results))
        print()


def parse_natural_language(text: str) -> UserRequest:
    """從自然語言中擷取點餐需求（簡易版解析器）"""
    request = UserRequest()

    # 解析人數
    for pattern in ["個人", "人份", "位"]:
        idx = text.find(pattern)
        if idx > 0:
            num_str = ""
            for ch in reversed(text[:idx]):
                if ch.isdigit():
                    num_str = ch + num_str
                else:
                    break
            if num_str:
                request.people = int(num_str)
                break

    # 解析預算
    for pattern in ["元內", "元以內", "塊內", "塊以內", "元"]:
        idx = text.find(pattern)
        if idx > 0:
            num_str = ""
            for ch in reversed(text[:idx]):
                if ch.isdigit():
                    num_str = ch + num_str
                else:
                    break
            if num_str:
                request.budget = int(num_str)
                break

    # 解析地區
    areas = ["板橋", "中正", "大安", "信義", "中山", "松山",
             "南港", "內湖", "士林", "北投", "萬華", "文山",
             "三重", "新莊", "永和", "中和", "土城", "蘆洲",
             "汐止", "樹林", "淡水", "新店"]
    for area in areas:
        if area in text:
            if "新北" in text or area in ["板橋", "三重", "新莊", "永和", "中和", "土城", "蘆洲"]:
                request.location = f"新北市{area}區"
            else:
                request.location = f"台北市{area}區"
            break

    # 解析時段
    if any(kw in text for kw in ["早餐", "早上"]):
        request.meal_time = "breakfast"
    elif any(kw in text for kw in ["午餐", "中午"]):
        request.meal_time = "lunch"
    elif any(kw in text for kw in ["晚餐", "晚上"]):
        request.meal_time = "dinner"
    elif any(kw in text for kw in ["宵夜", "消夜", "深夜"]):
        request.meal_time = "late_night"
    elif any(kw in text for kw in ["下午茶", "點心"]):
        request.meal_time = "afternoon_tea"

    # 解析偏好
    cat_keywords = {
        "便當": "便當", "飯": "飯類", "麵": "麵類", "湯": "湯品",
        "飲料": "飲料", "手搖": "飲料", "健康": "健康餐", "輕食": "輕食",
        "素食": "素食", "韓式": "韓式", "義式": "義式", "西式": "西式",
        "台式": "台式", "早餐": "早餐",
    }
    for keyword, cat in cat_keywords.items():
        if keyword in text:
            request.category.append(cat)

    # 解析禁忌
    avoid_keywords = ["辣", "炸", "炸物", "內臟", "甜", "油", "生食"]
    for kw in avoid_keywords:
        if f"不要{kw}" in text or f"不吃{kw}" in text or f"不{kw}" in text or f"無{kw}" in text:
            request.avoid.append(kw)

    # 飲料
    if any(kw in text for kw in ["飲料", "手搖", "加飲料", "要喝"]):
        request.drink = True

    # 快速
    if any(kw in text for kw in ["快速", "趕時間", "快一點"]):
        request.fast_delivery = True

    return request


# ============================================================
# 示範模式
# ============================================================

def demo_mode(restaurants: List[Restaurant]):
    """執行所有示範案例"""
    demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_input.json")

    if os.path.exists(demo_path):
        with open(demo_path, "r", encoding="utf-8") as f:
            demo_data = json.load(f)
        cases = demo_data.get("demo_cases", [])
    else:
        cases = [
            {
                "name": "Demo: 兩人晚餐",
                "input": {
                    "location": "新北市板橋區", "budget": 300,
                    "meal_time": "dinner", "category": ["便當"],
                    "avoid": ["炸物"], "people": 2,
                    "drink": False, "fast_delivery": True, "chain_ok": True
                }
            }
        ]

    for i, case in enumerate(cases, 1):
        print(f"\n{'#' * 50}")
        print(f"  示範案例 {i}：{case['name']}")
        print(f"{'#' * 50}")

        inp = case["input"]
        request = UserRequest(
            location=inp.get("location", ""),
            budget=inp.get("budget", 200),
            meal_time=inp.get("meal_time", ""),
            category=inp.get("category", []),
            avoid=inp.get("avoid", []),
            people=inp.get("people", 1),
            drink=inp.get("drink", False),
            fast_delivery=inp.get("fast_delivery", False),
            chain_ok=inp.get("chain_ok", True),
        )

        results = recommend(request, restaurants)
        print(format_output(request, results))


# ============================================================
# 主程式入口
# ============================================================

def main():
    restaurants = load_restaurants()

    if len(sys.argv) < 2:
        print("用法：")
        print("  python foodpanda_helper.py '{\"location\":\"...\", ...}'")
        print("  python foodpanda_helper.py --demo")
        print("  python foodpanda_helper.py --interactive")
        print("  python foodpanda_helper.py --json '{...}'")
        sys.exit(0)

    arg = sys.argv[1]

    if arg == "--demo":
        demo_mode(restaurants)
        return

    if arg == "--interactive":
        interactive_mode(restaurants)
        return

    output_json = False
    raw_input = arg

    if arg == "--json":
        output_json = True
        if len(sys.argv) < 3:
            print("請提供 JSON 參數")
            sys.exit(1)
        raw_input = sys.argv[2]

    try:
        user_input = json.loads(raw_input)
    except json.JSONDecodeError:
        # 嘗試當作自然語言處理
        request = parse_natural_language(raw_input)
        results = recommend(request, restaurants)
        print(format_output(request, results))
        return

    request = UserRequest(
        location=user_input.get("location", ""),
        budget=user_input.get("budget", 200),
        meal_time=user_input.get("meal_time", ""),
        category=user_input.get("category", []),
        avoid=user_input.get("avoid", []),
        people=user_input.get("people", 1),
        drink=user_input.get("drink", False),
        fast_delivery=user_input.get("fast_delivery", False),
        chain_ok=user_input.get("chain_ok", True),
    )

    results = recommend(request, restaurants)

    if output_json:
        print(format_json(request, results))
    else:
        print(format_output(request, results))


if __name__ == "__main__":
    main()
