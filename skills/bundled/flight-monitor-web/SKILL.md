---
name: flight-monitor-web
description: |
  根據黃仁蝦機票監控程式碼，自動生成互動式機票比價網站、即時監控系統或三合一混合應用。
  支援 Trip.com 即時查價、視覺化儀表板、價格趨勢圖、Telegram / Line 低價警報推播，
  並可選配 Aviationstack API 來補充航班狀態、機場與航線資訊。
---

# 機票監控互動網站產生器

## Description
當使用者要求以下任一情境時啟動此 Skill：

1. **網頁版**：建立機票監控網站、機票比價網頁、航班價格追蹤儀表板
2. **小龍蝦 AI 即時回報版**：讓小龍蝦 AI（Colab / Jupyter）使用此監控邏輯，
   搭配 Telegram / Line 做即時低價回報系統
3. **混合版**：網頁儀表板 + 後端即時監控 + Telegram / Line 推播三合一

根據 @assets/huang_shrimp_flight.py 中的黃仁蝦機票監控邏輯，
自動生成對應版本的完整應用。

如果使用者指定要做 LINE Bot，則再分成兩層：

1. **基礎版**：
   先完成 LINE Bot 申請教學、取得 Token、取得 `LINE_USER_ID`、成功收到推播
2. **進階版**：
   加入完整對話機器人、多指令解析、資料庫、Rich menu，並支援多使用者或群組

觸發關鍵字：機票監控網站、機票比價網頁、航班追蹤、flight monitor web、
機票儀表板、黃仁蝦機票、即時監控、即時回報、Telegram 機票警報、Line 機票警報、
Aviationstack、航班 API、API Key、智慧航班助理

---

## API 教學整合模式

當使用者除了想做票價監控，還想：

- 教學生什麼是 API Key
- 製作「航班資料 API + 前端儀表板」教材
- 加入即時航班狀態、機場資訊、航線資料
- 做成「智慧航班助理」

則此 Skill 必須把 `AVIATIONSTACKAPIKEY` 一起納入方案設計。

你必須用教學口吻清楚說明：

- API Key = 網路服務的門禁卡
- 沒有 Key，API 會拒絕存取
- Aviationstack 可提供航班、機場、航線等資料
- API Key 不可寫死在前端、不可放 GitHub
- 正確做法是存放在環境變數或後端秘密設定中
- 若明確限定為本機教學 / 個人測試 / 免費 Key，也可提供 localStorage 測試模式，但要標示這不是公開部署做法

---

## 視覺設計系統

### 一、色彩系統（航空科技風）

#### 主題色：深空藍 × 天際橘

| CSS 變數 | 色碼 | 用途 |
|----------|------|------|
| `--color-bg` | `#F0F4F8` | 頁面背景（淺灰藍） |
| `--color-surface` | `#FFFFFF` | 卡片、面板底色 |
| `--color-primary` | `#1A237E` | 主色（深空藍）— 導覽列、頁首、主要按鈕 |
| `--color-primary-light` | `#3949AB` | 主色亮階 — hover 狀態 |
| `--color-primary-dark` | `#0D1442` | 主色暗階 — 頁尾、深色區塊 |
| `--color-accent` | `#FF6D00` | 強調色（天際橘）— CTA 按鈕、重點數字、警報 |
| `--color-accent-light` | `#FF9E40` | 強調色亮階 — hover、次要高亮 |
| `--color-success` | `#00C853` | 低價提示、監控啟動中、成功狀態 |
| `--color-danger` | `#FF1744` | 警報閃爍、價格上漲、停止按鈕 |
| `--color-warning` | `#FFD600` | 門檻接近提示 |
| `--color-text` | `#1A1A2E` | 主文字（近黑） |
| `--color-text-secondary` | `#5C6B7A` | 輔助文字、說明文字 |
| `--color-text-muted` | `#9BA8B7` | 佔位文字、停用狀態 |
| `--color-border` | `#E2E8F0` | 卡片邊框、分隔線 |
| `--color-code-bg` | `#F8FAFC` | 程式碼區塊背景 |

#### 漸層系統

| 名稱 | 定義 | 用途 |
|------|------|------|
| 天空漸層 | `linear-gradient(135deg, #1A237E 0%, #0D47A1 50%, #1565C0 100%)` | 頁首橫幅、封面背景 |
| 日落漸層 | `linear-gradient(135deg, #FF6D00 0%, #FF9E40 100%)` | CTA 按鈕、低價警報背景 |
| 夜幕漸層 | `linear-gradient(180deg, #0D1442 0%, #1A237E 100%)` | 頁尾背景 |
| 玻璃效果 | `background: rgba(255,255,255,0.85); backdrop-filter: blur(12px);` | 浮動面板、監控狀態列 |

#### 狀態色卡片配色

| 狀態 | 背景 | 邊框 | 文字 | 圖示 |
|------|------|------|------|------|
| 低價警報 | `#FFF3E0` | `#FF6D00` | `#E65100` | 閃爍鈴鐺 |
| 監控中 | `#E8F5E9` | `#00C853` | `#1B5E20` | 旋轉雷達 |
| 查詢中 | `#E3F2FD` | `#1565C0` | `#0D47A1` | 飛機動畫 |
| 錯誤 | `#FFEBEE` | `#FF1744` | `#B71C1C` | 驚嘆號 |
| 已停止 | `#F5F5F5` | `#9E9E9E` | `#616161` | 暫停圖示 |

#### 深色模式（Dark Mode）

| CSS 變數 | 深色模式色碼 | 說明 |
|----------|-------------|------|
| `--color-bg` | `#0A0E1A` | 深夜背景 |
| `--color-surface` | `#151B2B` | 卡片底色 |
| `--color-primary` | `#5C6BC0` | 主色（提亮） |
| `--color-text` | `#E8ECF1` | 主文字（淺色） |
| `--color-text-secondary` | `#8B9DC3` | 輔助文字 |
| `--color-border` | `#2A3450` | 邊框色 |

切換方式：頁首右上角太陽/月亮圖示，使用者偏好存入 localStorage，
也尊重 `prefers-color-scheme` 系統設定。

---

### 二、字型規格

| 層級 | 字體 | 大小 | 粗細 | 行高 | 用途 |
|------|------|------|------|------|------|
| 字體主體 | `"Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif` | — | — | — | 全站統一 |
| 等寬字體 | `"Fira Code", "Source Code Pro", "Consolas", monospace` | — | — | — | 價格數字、程式碼 |
| 數字字體 | `"Tabular Nums" (font-variant-numeric: tabular-nums)` | — | — | — | 價格欄位對齊 |
| 超大標題 | — | 48px | 800 | 1.2 | 首屏 Hero 標題 |
| 大標題 H1 | — | 32px | 700 | 1.3 | 區塊標題 |
| 區塊標題 H2 | — | 24px | 700 | 1.4 | 卡片群組標題 |
| 卡片標題 H3 | — | 18px | 600 | 1.5 | 卡片內標題 |
| 正文 | — | 16px | 400 | 1.75 | 一般說明文字 |
| 小說明 | — | 14px | 400 | 1.6 | 副標、佐證資訊 |
| 極小標籤 | — | 12px | 600 | 1.4 | 標籤 badge、狀態標示 |
| 價格大數字 | Fira Code | 56px | 700 | 1.0 | 最低價顯示卡片 |
| 價格表格數字 | Fira Code | 18px | 500 | 1.4 | 比價表內數字 |

---

### 三、間距與圓角系統

| Token | 值 | 用途 |
|-------|-----|------|
| `--space-xs` | 4px | 標籤內邊距 |
| `--space-sm` | 8px | 緊湊元素間距 |
| `--space-md` | 16px | 卡片內邊距、元素間距 |
| `--space-lg` | 24px | 區塊間距 |
| `--space-xl` | 32px | 大區塊間距 |
| `--space-2xl` | 48px | 頁面邊距、Hero 區段 |
| `--space-3xl` | 64px | 區段之間 |
| `--radius-sm` | 4px | 小按鈕、標籤 |
| `--radius-md` | 8px | 輸入框、一般按鈕 |
| `--radius-lg` | 12px | 卡片 |
| `--radius-xl` | 16px | 大面板、對話框 |
| `--radius-full` | 9999px | 藥丸形按鈕、頭像 |

#### 陰影系統

| 名稱 | 定義 | 用途 |
|------|------|------|
| `--shadow-sm` | `0 1px 3px rgba(26,35,126,0.06)` | 卡片靜止狀態 |
| `--shadow-md` | `0 4px 12px rgba(26,35,126,0.1)` | 卡片 hover |
| `--shadow-lg` | `0 8px 24px rgba(26,35,126,0.15)` | 浮動面板 |
| `--shadow-glow` | `0 0 20px rgba(255,109,0,0.3)` | 低價警報卡片外發光 |

---

### 四、元件設計規則

#### 價格卡片（Price Card）— 最重要的元件

```
┌─────────────────────────────────────────┐
│  ┌──────┐                               │
│  │ 最低價 │ ← 左上角 badge（強調色底）     │
│  └──────┘                               │
│                                         │
│     TWD 6,890    ← 56px 等寬粗體         │
│                                         │
│  台北 → 沖繩｜5/3 - 5/6     ← 副標       │
│  ──────────────────────                 │
│  較你查日期便宜 TWD 1,310  ← 省多少       │
│  [查看詳情]              ← 文字連結       │
└─────────────────────────────────────────┘
```

- 底色：`--color-surface`（白色）
- 邊框：`1px solid --color-border`
- 圓角：`--radius-lg`（12px）
- 陰影：`--shadow-sm`，hover 時升級 `--shadow-md` + translateY(-2px)
- 低價狀態：邊框改 `--color-accent`（2px），外發光 `--shadow-glow`，
  背景加淡橘 `rgba(255,109,0,0.04)`

#### 目的地選擇卡片（Destination Card）

```
┌───────────────────┐
│  [城市背景圖片]     │ ← 高度 120px，底部漸層遮罩
│   ┌─────────────┐ │
│   │  沖繩 OKA    │ │ ← 白字，text-shadow
│   │  那霸        │ │
│   └─────────────┘ │
│  最近低價 TWD 5,890 │ ← 綠色數字
│  ────────────────  │
│  [選擇此目的地]     │ ← 按鈕
└───────────────────┘
```

- 6 張卡片排成 3×2 網格（桌面）/ 2×3（平板）/ 1×6（手機）
- hover：圖片放大 1.05 + 陰影加深
- 選中狀態：邊框改 `--color-accent`（3px）+ 左上角打勾圖示

#### 比價表格（Comparison Table）

| 表頭 | 背景 | 文字 |
|------|------|------|
| 表頭列 | `--color-primary`（天空漸層） | 白色粗體 |
| 奇數列 | `rgba(26,35,126,0.03)` | 正常 |
| 偶數列 | `--color-surface` | 正常 |
| hover 列 | `rgba(26,35,126,0.08)` | — |
| 最低價列 | `rgba(255,109,0,0.08)` | 價格用 `--color-accent` 粗體 + 「最低」badge |

- 圓角：`--radius-lg`
- 邊框：`1px solid --color-border`
- 價格欄右對齊，使用等寬數字字體
- 最後一欄「操作」放圖示按鈕（截圖、連結）

#### 按鈕系統

| 類型 | 背景 | 文字 | 邊框 | hover | 用途 |
|------|------|------|------|-------|------|
| Primary | 日落漸層 | 白色粗體 | 無 | 亮度+10%、shadow-md | 「立即查詢」 |
| Secondary | transparent | `--color-primary` | 1px primary | 淺主色底 | 「啟動監控」 |
| Danger | `--color-danger` | 白色 | 無 | 暗紅 | 「停止監控」 |
| Ghost | transparent | `--color-text-secondary` | 無 | 淺灰底 | 「重設」 |
| Icon | `rgba(255,255,255,0.12)` | 白色 | 無 | 亮度+20% | 頁首圖示鈕 |

- 圓角：`--radius-md`（8px），藥丸形用 `--radius-full`
- 內邊距：12px 24px（標準）、8px 16px（小型）
- 過渡：`transition: all 0.2s ease`
- 停用狀態：opacity 0.5 + cursor not-allowed

#### 輸入欄位

- 高度：44px
- 圓角：`--radius-md`
- 邊框：`1px solid --color-border`
- focus：邊框改 `--color-primary`（2px）+ 外陰影 `0 0 0 3px rgba(26,35,126,0.1)`
- 佔位文字：`--color-text-muted`
- 日期選擇器：原生 `<input type="date">` 搭配自訂圖示

#### 提示框（Alert Box）

| 類型 | 背景 | 左邊框 | 圖示 | 文字 |
|------|------|--------|------|------|
| 資訊 | `#E3F2FD` | `#1565C0`（4px） | 飛機 | `#0D47A1` |
| 成功 | `#E8F5E9` | `#00C853`（4px） | 打勾 | `#1B5E20` |
| 警告 | `#FFF8E1` | `#FFD600`（4px） | 驚嘆 | `#F57F17` |
| 警報 | `#FFF3E0` | `#FF6D00`（4px） | 鈴鐺 | `#E65100` |
| 錯誤 | `#FFEBEE` | `#FF1744`（4px） | 叉叉 | `#B71C1C` |

#### 監控狀態列（Sticky Bar）

- 位置：比價結果區上方，`position: sticky; top: 64px`
- 玻璃效果：`backdrop-filter: blur(12px)`
- 內容：狀態燈號（綠=運行/灰=停止）+ 上次查詢時間 + 下次倒數 + 停止按鈕
- 監控中的脈衝動畫：綠色圓點 `@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }`

---

### 五、版面配置

#### 整體結構

```
┌─── 頁首（sticky，天空漸層）──────────────────────────┐
│ [Logo] 黃仁蝦機票監控    [深色模式] [全螢幕] [GitHub] │
└─────────────────────────────────────────────────────┘

┌─── Hero 區（大標題 + 查詢面板）──────────────────────┐
│                                                      │
│    即時比價，低價不漏接                                │
│    ─────────────────                                 │
│  [目的地▼] [出發日] [回程日] [門檻] [查詢🔍]          │
│                                                      │
└──────────────────────────────────────────────────────┘

┌─── 目的地快選（6 張城市卡片 3×2）────────────────────┐
│  [福岡]  [大阪]  [東京]                               │
│  [沖繩]  [首爾]  [釜山]                               │
└──────────────────────────────────────────────────────┘

┌─── 監控狀態列（sticky）──────────────────────────────┐
│ ● 監控中 | 上次 14:30 | 下次 15:30 (倒數 42:18) [停止]│
└──────────────────────────────────────────────────────┘

┌─── 比價結果（兩欄佈局）──────────────────────────────┐
│  ┌── 左欄 60% ──────────┐ ┌── 右欄 40% ──────────┐  │
│  │ 比價表格               │ │ 最低價大卡片          │  │
│  │ + 價格趨勢折線圖       │ │ + 截圖預覽            │  │
│  └────────────────────┘ └────────────────────┘  │
└──────────────────────────────────────────────────────┘

┌─── 歷史紀錄 + Telegram 設定（手風琴摺疊）────────────┐
│ ▸ 查詢歷史（最近 20 筆）                              │
│ ▸ Telegram 推播設定                                   │
│ ▸ 進階設定（查詢頻率、聲音提醒）                      │
└──────────────────────────────────────────────────────┘

┌─── 頁尾（夜幕漸層）─────────────────────────────────┐
│  資料來源：IATA (International Air Transport Association) via Trip.com | 黃仁蝦機票監控 v2.0             │
│  免責聲明 | GitHub | Licensed under IATA Open Data     │
└──────────────────────────────────────────────────────┘
```

#### 響應式斷點

| 斷點 | 寬度 | 佈局調整 |
|------|------|---------|
| 桌面 | ≥1200px | 兩欄比價（60/40）、城市卡片 3 欄、完整頁首 |
| 小桌面 | ≥992px | 兩欄比價（55/45）、城市卡片 3 欄 |
| 平板 | ≥768px | 比價改單欄堆疊、城市卡片 2 欄、頁首按鈕隱藏文字 |
| 手機 | ≥480px | 全部單欄、城市卡片 2 欄、查詢表單垂直堆疊 |
| 小手機 | <480px | 全部單欄、城市卡片 1 欄、間距縮減 |

最大內容寬度：`max-width: 1200px; margin: 0 auto;`
頁面邊距：桌面 48px / 平板 24px / 手機 16px

---

### 六、動畫與互動效果

| 元素 | 動畫 | 觸發時機 | 持續時間 |
|------|------|---------|---------|
| 價格數字 | 數字滾動（countUp.js 風格） | 查詢結果載入 | 1.2s ease-out |
| 低價警報卡片 | 邊框脈衝 + 外發光呼吸 | 價格 < 門檻 | 2s infinite |
| 查詢按鈕 | 飛機圖示從左飛到右 | 點擊後等待期間 | 循環 |
| 比價表格列 | fadeInUp 逐列出現 | 結果載入 | 每列延遲 50ms |
| 目的地卡片 | hover 放大 1.03 + 陰影加深 | 滑鼠移入 | 0.3s ease |
| 監控脈衝燈 | 綠色圓點呼吸 | 監控啟動中 | 1.5s infinite |
| 深色模式切換 | 全頁面顏色 transition | 切換主題 | 0.3s ease |
| 頁面載入 | 骨架屏 → 淡入實際內容 | 初次載入 | 0.5s |
| 折疊面板 | 高度 slideDown/slideUp | 展開/收合 | 0.25s ease |
| 倒數計時器 | 數字翻頁效果 | 每秒更新 | 0.3s |

#### 低價警報動畫（關鍵效果）
```css
@keyframes alert-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255,109,0,0.4); }
  50% { box-shadow: 0 0 20px 8px rgba(255,109,0,0.15); }
}
@keyframes alert-border {
  0%, 100% { border-color: #FF6D00; }
  50% { border-color: #FF9E40; }
}
.price-card.alert {
  animation: alert-pulse 2s infinite, alert-border 2s infinite;
}
```

---

### 七、圖示系統

使用內嵌 SVG 或 Lucide Icons（CDN），不使用圖片檔。

| 用途 | 圖示 | 大小 |
|------|------|------|
| 查詢按鈕 | 飛機（plane-takeoff） | 20px |
| 監控啟動 | 雷達（radar） | 20px |
| 監控停止 | 暫停（pause-circle） | 20px |
| 低價警報 | 鈴鐺（bell-ring） | 24px |
| 日期選擇 | 日曆（calendar） | 18px |
| 門檻設定 | 標靶（target） | 18px |
| Telegram | 紙飛機（send） | 20px |
| 深色模式 | 太陽/月亮（sun/moon） | 20px |
| 全螢幕 | 展開/縮小（maximize/minimize） | 20px |
| 展開/收合 | 箭頭（chevron-down/up） | 16px |
| 最低價標記 | 獎牌（medal）或向下箭頭 | 16px |
| 外部連結 | 箭頭外射（external-link） | 14px |

---

### 八、可快速替換的配色方案

若要改變整體風格，只需修改 CSS 變數：

**方案 A：航空科技風（預設）**
- primary `#1A237E` / accent `#FF6D00` / bg `#F0F4F8`

**方案 B：海洋清爽風**
- primary `#006064` / accent `#00BFA5` / bg `#E0F7FA`

**方案 C：日系簡約風**
- primary `#37474F` / accent `#FF7043` / bg `#FAFAFA`

**方案 D：櫻花旅行風**
- primary `#880E4F` / accent `#F48FB1` / bg `#FFF5F5`

**方案 E：商務專業風**
- primary `#263238` / accent `#FFC107` / bg `#ECEFF1`

Ask user 選擇配色方案，或提供自訂色碼。

---

## Steps

Step 1: 讀取 @assets/huang_shrimp_flight.py，理解核心邏輯：
    - Trip.com 網址組合規則（dcity=tpe, acity 對照表, ddate, rdate, triptype）
    - 目的地對照表：福岡(fuk)、大阪(osa)、東京(tyo)、沖繩(oka)、首爾(sel)、釜山(pus)
    - 價格抓取邏輯：正則表達式解析日期+票價、最低價比較
    - Telegram 推播邏輯：BOT_TOKEN + CHAT_ID、文字+截圖推播
    - 價格門檻警報機制：低於門檻觸發警報、高於門檻推播純資訊

Step 2: 設計網站架構，Ask user 確認以下選項：
    - 前端框架偏好（純 HTML/CSS/JS 單頁應用 或 React/Vue/Next.js）
    - 是否需要後端 API（Node.js/Python Flask/FastAPI）
    - 部署平台偏好（本機執行、Netlify、Vercel、GitHub Pages）
    - 是否保留 Telegram 推播功能
    - 是否保留 LINE 推播功能，以及要做基礎版或進階版
    - 是否要加入 Aviationstack API（航班狀態 / 機場 / 航線資料）
    - 配色方案選擇（A 航空科技 / B 海洋清爽 / C 日系簡約 / D 櫻花旅行 / E 商務專業 / 自訂）

Step 2.1: 如果使用者選擇加入 Aviationstack：
    - 說明 `AVIATIONSTACKAPIKEY` 是什麼，以及為何不能公開
    - 預設採用「後端代理呼叫 API」模式，不可由前端直接帶 Key 呼叫
    - 生成 `.env` 或環境變數設定教學
    - 如果是教學型內容，加入一段「API Key = 門禁卡」的簡單說明區塊
    - 如果使用者明確說明「只在本機使用」，可額外提供 localStorage / 手動貼入的簡化方案

Step 2.2: 如果使用者選擇 LINE 推播：
    - 基礎版：提供 LINE Bot 申請、Token、`LINE_USER_ID` 取得與推播串接教學
    - 進階版：把 LINE Bot 納入正式產品能力，加入指令、資料庫、Rich menu 與多使用者支援

Step 3: 建立前端介面，嚴格遵循上方「視覺設計系統」的色彩、字型、間距、元件規範：

    3.1 頁首（Header — sticky）：
        - 天空漸層背景
        - 左側：Logo + 標題「黃仁蝦機票監控」
        - 右側：深色模式切換 / 全螢幕 / GitHub 連結
        - 高度 64px

    3.2 Hero 查詢面板：
        - 大標題：「即時比價，低價不漏接」48px 粗體
        - 查詢表單（一列排開，手機版堆疊）：
          出發地固定「台北 TPE」/ 目的地下拉 / 出發日 / 回程日 / 門檻 / 查詢按鈕
        - 單程/來回切換 toggle

    3.3 目的地快選（6 張城市卡片）：
        - 3×2 網格佈局（遵循 Destination Card 元件規範）
        - 每張卡片包含城市背景圖（用 CSS gradient 模擬或 Unsplash API）
        - 顯示該城市最近低價（如果有歷史資料）

    3.4 監控狀態列（Sticky Bar）：
        - 玻璃效果背景
        - 狀態燈號 + 上次/下次查詢時間 + 倒數計時器 + 停止按鈕

    3.5 比價結果儀表板（兩欄 → 手機單欄）：
        - 左欄：比價表格 + 價格趨勢折線圖（Chart.js）
        - 右欄：最低價大卡片（遵循 Price Card 元件規範）+ 截圖預覽

    3.6 摺疊面板區：
        - 查詢歷史（最近 20 筆，localStorage）
        - Telegram 推播設定（Bot Token / Chat ID / 測試按鈕）
        - 進階設定（查詢頻率、聲音提醒開關）

    3.7 頁尾：
        - 夜幕漸層背景
        - 資料來源聲明、版本資訊、GitHub 連結

Step 4: 建立後端 API（如果使用者選擇需要後端）：

    4.1 查詢端點 POST /api/search：
        - 接收：destination, depart_date, return_date, threshold
        - 執行：Playwright 開啟 Trip.com 抓取價格
        - 回傳：JSON { target_price, date_prices[], best_price, best_label, screenshot_base64 }

    4.2 監控端點：
        - POST /api/monitor/start — 啟動背景定時查詢
        - POST /api/monitor/stop — 停止監控
        - GET /api/monitor/status — 查詢監控狀態 + 歷史紀錄

    4.3 Telegram 端點 POST /api/telegram/test — 測試推播

    4.4 Aviationstack 端點（如果使用者選擇加入 API 模式）：
        - GET /api/aviation/flights — 查即時航班資料
        - GET /api/aviation/airports — 查機場資料
        - GET /api/aviation/routes — 查航線資料
        - 後端使用 `AVIATIONSTACKAPIKEY` 環境變數呼叫
        - 前端不可直接看到真實 API Key

    4.5 Check if 使用者選擇純前端方案：
        - 改用 iframe 嵌入 Trip.com 搜尋結果連結
        - 價格比對改為手動輸入模式
        - 監控改為瀏覽器端 setInterval + Notification API

Step 4.6: 如果使用者選擇 LINE 進階版：
    - 建立 webhook 端點接收 LINE 事件
    - 實作以下指令：
      - `/price` 查指定航線價格
      - `/watch` 啟動監控
      - `/stop` 停止監控
      - `/status` 查看監控狀態
    - 使用資料庫保存每位使用者或群組的訂閱條件
    - 提供 Rich menu 一鍵操作
    - 支援多使用者或群組

Step 5: 實作核心功能程式碼：

    5.1 Trip.com URL 產生器（前端 JavaScript）：
        ```javascript
        const DEST_MAP = {
            '福岡': 'fuk', '大阪': 'osa', '東京': 'tyo',
            '沖繩': 'oka', '首爾': 'sel', '釜山': 'pus'
        };
        function buildTripUrl(dest, ddate, rdate, isOneWay) {
            const acity = DEST_MAP[dest];
            const triptype = isOneWay ? 'ow' : 'rt';
            let url = `https://tw.trip.com/flights/showfarefirst?dcity=tpe&acity=${acity}&ddate=${ddate}&triptype=${triptype}&class=y&quantity=1&locale=zh-TW&curr=TWD`;
            if (!isOneWay && rdate) url += `&rdate=${rdate}`;
            return url;
        }
        ```

    5.2 Playwright 爬蟲腳本（後端 Python，完整保留 @assets/huang_shrimp_flight.py 邏輯）：
        - 保留正則表達式解析
        - 保留日期列最低價比較 + 自動點擊截圖
        - 新增：回傳 base64 截圖
        - 新增：寫入 JSON 歷史檔

    5.3 Telegram 推播模組（保留 send_telegram_alert 邏輯）

Step 6: 加入動畫與互動效果（遵循「動畫與互動效果」規範）：
    - 價格數字滾動動畫
    - 低價警報脈衝效果
    - 查詢中飛機載入動畫
    - 比價表格逐列淡入
    - 深色/淺色模式平滑過渡

Step 7: 產出完整檔案結構：
    ```
    flight-monitor-web/
    ├── index.html
    ├── css/
    │   └── style.css           ← 包含完整 CSS 變數系統 + 深色模式
    ├── js/
    │   ├── app.js              ← 主邏輯 + URL 產生器 + DOM 操作
    │   ├── chart.js            ← Chart.js 價格趨勢圖
    │   ├── telegram.js         ← Telegram 推播整合
    │   └── animations.js       ← 動畫效果（數字滾動、脈衝等）
    ├── server/                 ← 後端（如需要）
    │   ├── app.py              ← FastAPI 主程式
    │   ├── scraper.py          ← Playwright 爬蟲（完整保留原始邏輯）
    │   ├── monitor.py          ← 定時監控
    │   └── requirements.txt
    └── README.md
    ```

Step 8: 撰寫 README.md（安裝步驟、啟動指令、部署教學、功能截圖說明）

---

### 小龍蝦 AI 即時回報模式（Colab / Jupyter / 本機 Python）

當使用者選擇此模式時，不生成網頁，改為生成可直接在 Colab 或本機執行的 Python 即時監控系統：

Step A1: 基於 @assets/huang_shrimp_flight.py 重構為模組化架構：
    ```
    lobster-flight-monitor/
    ├── config.py           ← 設定檔（Telegram Token、Chat ID、預設門檻）
    ├── destinations.py     ← 目的地對照表 + URL 產生器
    ├── scraper.py          ← Playwright 爬蟲核心（保留原始正則邏輯）
    ├── notifier.py         ← Telegram 推播模組（文字 + 截圖 + 美化格式）
    ├── monitor.py          ← 定時監控主程式（背景執行緒 + 排程）
    ├── dashboard.py        ← 終端機即時儀表板（rich 套件美化輸出）
    ├── web_report.py       ← 自動產生 HTML 報告頁面（單次快照）
    ├── main.py             ← 統一入口（CLI 參數解析）
    └── requirements.txt
    ```

Step A2: 強化 Telegram 推播格式（比原始版更美觀）：
    推播訊息模板：
    ```
    ✈️ 黃仁蝦機票監控 — {label}
    ━━━━━━━━━━━━━━━━━━━
    📅 查詢時間：{now}

    💰 你查的日期：TWD {target_price:,}
    🏆 近期最低價：TWD {best_price:,}（{best_label}）
    📉 差價：便宜 TWD {diff:,}

    📊 近期比價：
    ┌─────────────┬──────────┐
    │ 日期         │ 價格      │
    ├─────────────┼──────────┤
    │ {date1}     │ TWD {p1} │
    │ {date2}     │ TWD {p2} ◀ 最低 │
    │ {date3}     │ TWD {p3} │
    └─────────────┴──────────┘

    🎯 門檻：TWD {threshold:,}
    {alert_msg}
    ━━━━━━━━━━━━━━━━━━━
    🦞 黃仁蝦機票監控 v2.0
    ```

    低價警報時額外推播：
    ```
    🔔🔔🔔 低價警報！🔔🔔🔔
    ✈️ {label}
    💰 TWD {best_price:,}（門檻 {threshold:,}）
    ⚡ 比門檻便宜 TWD {saving:,}！
    🔗 立即搶票 → {trip_url}
    ```

Step A3: 新增自動產生 HTML 即時報告功能：
    - 每次查詢後自動更新一份 `report.html`
    - 包含比價表格 + 價格趨勢圖（嵌入 Chart.js）
    - 截圖直接 base64 嵌入頁面
    - 可分享連結（本機開啟或上傳到 GitHub Pages）
    - 遵循上方「視覺設計系統」的配色和元件規範

Step A4: CLI 使用方式：
    ```bash
    # 單次查詢
    python main.py --dest 沖繩 --depart 2026-05-01 --return 2026-05-04 --threshold 10000

    # 啟動定時監控（每 60 分鐘）
    python main.py --dest 沖繩 --depart 2026-05-01 --return 2026-05-04 --threshold 10000 --watch --interval 60

    # 多目的地同時監控
    python main.py --multi "沖繩:2026-05-01:2026-05-04:10000,大阪:2026-06-01:2026-06-05:12000"

    # 產生 HTML 報告
    python main.py --dest 沖繩 --depart 2026-05-01 --return 2026-05-04 --report
    ```

Step A5: Colab Notebook 版本：
    - 產生一份 .ipynb，保留原始教材的 Step-by-Step 結構
    - 每個 Cell 有清楚的標題和說明
    - 加入互動式 widget（ipywidgets）：
      目的地下拉 / 日期選擇 / 門檻滑桿 / 啟動/停止按鈕
    - 結果直接在 Notebook 內顯示（HTML 表格 + 內嵌圖表）

---

### 混合版（網頁 + 即時監控 + Telegram 三合一）

Step B1: 整合前端網頁 + 後端監控 + Telegram 推播：
    ```
    flight-monitor-full/
    ├── web/                    ← 前端（同 Step 3-6 的完整網頁）
    │   ├── index.html
    │   ├── css/style.css
    │   └── js/app.js
    ├── server/
    │   ├── app.py              ← FastAPI 主程式
    │   ├── scraper.py          ← Playwright 爬蟲
    │   ├── monitor.py          ← 背景監控排程
    │   ├── notifier.py         ← Telegram 推播
    │   ├── report_generator.py ← 自動產生 HTML 快照報告
    │   └── requirements.txt
    ├── reports/                ← 自動產生的 HTML 報告存放區
    ├── screenshots/            ← 截圖存放區
    └── README.md
    ```

Step B2: WebSocket 即時推送：
    - 後端查到新價格 → WebSocket 推送到前端 → 儀表板即時更新
    - 同時 Telegram 推播
    - 前端顯示「剛剛更新」即時標記

Step B3: 自動產生可分享的 HTML 報告：
    - 每次監控查詢後產生 `reports/report_YYYYMMDD_HHMM.html`
    - 報告頁面自包含（CSS + JS + 截圖全部 inline）
    - 可直接分享給朋友（開啟 .html 即可）
    - Telegram 推播時附上報告連結

## Rules

- MUST 嚴格遵循「視覺設計系統」中的色彩、字型、間距、元件規範
- MUST 所有 CSS 使用 CSS 變數（--color-*、--space-*、--radius-*），方便一鍵換色
- MUST 完整保留原始程式碼中的 Trip.com URL 組合邏輯，不得修改參數格式
- MUST 完整保留目的地對照表（福岡fuk/大阪osa/東京tyo/沖繩oka/首爾sel/釜山pus）
- MUST 完整保留價格正則表達式解析邏輯（日期+TWD+數字格式）
- MUST 完整保留 Telegram 推播的 API 呼叫格式（sendPhoto / sendMessage）
- MUST 使用繁體中文作為預設介面語言
- MUST 預設貨幣為 TWD（新台幣）
- MUST 支援 RWD 響應式設計，遵循斷點規範（1200/992/768/480）
- MUST 支援深色模式，遵循深色模式色碼表
- MUST 前端可由使用者自行輸入的 Telegram / Line 設定，可暫存於 localStorage，但不得寫死在原始碼
- MUST 若使用者要串接 Aviationstack，需清楚教學 `AVIATIONSTACKAPIKEY` 的用途、取得方式與安全風險
- MUST 將 Aviationstack 類 API Key 儲存在環境變數或後端祕密設定，不可暴露在前端
- MUST 若使用者明確限定本機端教學使用，可提供 localStorage 測試模式，但要同步提醒部署時改回環境變數
- MUST 若使用者要保留 LINE 推播，預設使用 `LINE_CHANNEL_ACCESS_TOKEN` 與 `LINE_USER_ID` 作為環境變數命名
- MUST 若使用者選擇 LINE 進階版，需將 `/price`、`/watch`、`/stop`、`/status` 視為核心指令
- MUST 若使用者選擇 LINE 進階版，需提供資料庫保存訂閱條件、Rich menu 與多使用者或群組支援
- MUST 查詢結果包含：指定日期價格、近期日期比價表、最低價標記
- MUST 價格低於門檻時觸發低價警報動畫效果（脈衝 + 外發光 + 邊框變色）
- MUST 所有圖示使用 SVG 或 Lucide Icons，不使用圖片檔案
- MUST 頁面載入使用骨架屏過渡動畫
- MUST 頁首使用 sticky 定位 + 天空漸層背景
- MUST WCAG AA 對比度標準（文字與背景對比 ≥ 4.5:1）
- NEVER 在前端原始碼中暴露 Telegram Bot Token 或 Line Bot Token
- NEVER 在前端原始碼中暴露 Aviationstack API Key
- NEVER 修改 Trip.com 的 URL 參數結構
- NEVER 在沒有使用者明確同意的情況下自動啟動監控
- NEVER 將查詢結果傳送到 Trip.com 和 Telegram 以外的第三方服務
- NEVER 繞過 Trip.com 的 robots.txt 或使用過高頻率的請求（最低間隔 30 分鐘）
- NEVER 使用行內樣式（inline style），所有樣式寫在 style.css
- NEVER 使用硬編碼色碼，必須透過 CSS 變數引用
- Check if 使用者是否已安裝 Node.js → 決定是否使用純 HTML 方案
- Check if 使用者是否已安裝 Python + Playwright → 決定後端技術方案
- Check if 使用者的 Telegram Bot Token 是否有效 → 提供測試推播功能
- Check if 使用者是否要把專案升級成 API + 比價混合模式 → 再決定是否接 Aviationstack
- Check if 使用者偏好深色/淺色 → 預設主題設定
- Ask user 配色方案選擇（A/B/C/D/E 或自訂色碼）
- Ask user 如果目的地需求超出目前支援的 6 個城市
- Ask user 如果需要支援 Trip.com 以外的機票平台

## Example

### 輸入
「幫我用這個機票監控程式，做成一個互動式的機票比價網站，可以即時查詢、看價格趨勢圖、低價推播 Telegram。」

### 輸出
AI 會：
1. 讀取 huang_shrimp_flight.py，理解爬蟲 + 推播邏輯
2. 詢問技術偏好 + 配色方案
3. 根據視覺設計系統，生成完整的網站專案
4. 提供安裝與啟動指令

### 網站功能預覽

```
┌─── 天空漸層頁首 ─────────────────────────────────┐
│ ✈ 黃仁蝦機票監控              [☀/🌙] [⛶] [GitHub]│
└──────────────────────────────────────────────────┘

┌─── Hero 查詢面板 ────────────────────────────────┐
│                                                   │
│       即時比價，低價不漏接                          │
│       ─────────────────                           │
│  台北TPE → [沖繩▼] [2026-05-01] [2026-05-04]     │
│  門檻 [TWD 10,000]  [🔍 立即查詢] [▶ 啟動監控]    │
│                                                   │
└───────────────────────────────────────────────────┘

┌─── 城市卡片 3×2 ─────────────────────────────────┐
│ ┌──────┐ ┌──────┐ ┌──────┐                       │
│ │ 福岡  │ │ 大阪  │ │ 東京  │                       │
│ │¥5,890 │ │¥6,200 │ │¥7,100 │                       │
│ └──────┘ └──────┘ └──────┘                       │
│ ┌──────┐ ┌──────┐ ┌──────┐                       │
│ │ 沖繩  │ │ 首爾  │ │ 釜山  │                       │
│ │¥4,990 │ │¥5,400 │ │¥4,200 │                       │
│ └──────┘ └──────┘ └──────┘                       │
└───────────────────────────────────────────────────┘

┌─── 監控狀態列（sticky + 玻璃效果）───────────────┐
│ ● 監控中 | 14:30 查詢 | 下次 15:30 (42:18) [停止] │
└───────────────────────────────────────────────────┘

┌─── 比價結果 ─────────────────────────────────────┐
│ ┌── 比價表格 ──────────┐ ┌── 最低價卡片 ────────┐│
│ │ 日期      │ 價格      │ │  🏆 最低價            ││
│ │ 5/1-5/4  │ TWD 8,200 │ │                       ││
│ │ 5/2-5/5  │ TWD 7,100 │ │  TWD 6,890            ││
│ │ 5/3-5/6  │ TWD 6,890◀│ │                       ││
│ │ 5/4-5/7  │ TWD 7,500 │ │  台北→沖繩 5/3-5/6   ││
│ ├───────────────────────┤ │  省 TWD 1,310         ││
│ │ [價格趨勢折線圖 📉]   │ │  ⚠ 低於門檻！         ││
│ └───────────────────────┘ └───────────────────────┘│
└───────────────────────────────────────────────────┘

┌─── 夜幕漸層頁尾 ─────────────────────────────────┐
│ IATA (International Air Transport Association) via Trip.com | v1.0 | IATA Licensed | GitHub  │
└───────────────────────────────────────────────────┘
```
