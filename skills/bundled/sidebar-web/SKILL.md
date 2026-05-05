---
name: sidebar-web
description: |
  將一批 Markdown 檔案整合成可互動瀏覽的側邊欄導覽網站（HTML+CSS+JS 單頁應用）。
  當使用者說「做成側邊欄網頁」「側邊欄網頁」「做成網頁瀏覽」「整合成網站」「把這些 md 做成網站」
  或任何將多個 Markdown/文件整合成可瀏覽網站的需求時，使用此技能。
  也適用於：教師手冊網站、課程教材網站、文件瀏覽器、知識庫網站、技術文件站等場景。
  核心特色：左側導覽目錄 + 中央 Markdown 內容渲染 + 頂部快捷列 + 底部作者資訊，
  無需伺服器，直接瀏覽器開啟即可使用。
---

# 側邊欄導覽網站建構指南

## 概述

此技能將一組 Markdown 檔案轉換為一個精美的單頁式互動網站，具備：
- 左側固定導覽目錄（支援群組展開/收合）
- 中央 Markdown 內容即時渲染（marked.js + highlight.js）
- 頂部固定橫幅（標題 + 快捷按鈕）
- 底部作者資訊區（多層結構）
- 完全離線可用，瀏覽器直接開啟

## 執行流程

### Step 1：盤點來源檔案

掃描使用者指定的目錄，找出所有 .md 檔案，確認：
- 檔案數量和清單
- 每個檔案的 H1 標題（用於導覽列顯示）
- 是否有群組/子分類結構（例如某些 md 需要歸在同一個父類下）
- 是否有圖片素材需要一起搬移

### Step 2：收集客製化資訊

向使用者確認：
1. **網站標題**：頂部橫幅顯示的主標題和副標題
2. **配色偏好**：預設使用暖色系，可依需求調整（見下方配色方案）
3. **頂部快捷按鈕**：全螢幕、社群連結、Email 等（可自訂）
4. **作者/底部資訊**：作者名稱、職稱、社群連結、授權聲明
5. **導覽結構**：是否需要群組展開（例如某些章節有子章節）

如果使用者是「阿亮老師」，可直接引用 `aliang-author-info` skill 的資訊。

### Step 3：建立檔案結構

```
<目標目錄>/website/
├── index.html          ← 主頁面
├── style.css           ← 樣式表
├── script.js           ← 互動邏輯
├── data/
│   └── units.js        ← 內容資料（由 build.py 產生）
├── assets/             ← 圖片等素材
└── build.py            ← 重建 units.js 的腳本
```

### Step 4：產生 build.py

build.py 的職責：讀取所有 md 檔 → 產生 `data/units.js`。

重點設計：
- 定義 UNITS 陣列，每個單元包含 `id`、`folder`、`file`、`title`、`shortTitle`、`parent`
- 支援群組標題（`isGroup: True`，不含內容）和子單元（`parent` 指向群組 id）
- 使用 `json.dumps` 將 md 內容安全地嵌入 JS
- Windows 相容：print 語句避免 emoji（cp950 編碼不支援）
- 輸出格式：`const UNITS_DATA = [...];\n`

參考模板：`references/build_template.py`

### Step 5：執行 build.py

```bash
py -3 build.py
```

確認產出的 units.js 包含所有單元。

### Step 6：產生 index.html

HTML 結構：

```html
<body>
  <!-- 頂部固定橫幅 -->
  <header class="site-header">
    <button class="menu-toggle">...</button>     <!-- 手機版漢堡選單 -->
    <div class="header-content">
      <h1 class="site-title">主標題</h1>
      <p class="site-subtitle">副標題</p>
    </div>
    <div class="header-actions">                  <!-- 右側快捷按鈕 -->
      <!-- YouTube / Facebook / Email / 全螢幕 等 -->
    </div>
  </header>

  <div class="main-layout">
    <nav class="sidebar">
      <div class="sidebar-header">...</div>       <!-- 目錄標題 -->
      <ul class="nav-list">...</ul>               <!-- 導覽清單 -->
      <div class="sidebar-footer">               <!-- 底部設定按鈕 -->
        <button class="settings-btn">設定</button>
      </div>
    </nav>
    <div class="sidebar-resizer"></div>           <!-- 拖拉把手 -->
    <div class="settings-panel">...</div>         <!-- 設定面板（文字大小 + 色彩風格） -->
    <div class="overlay"></div>                   <!-- 手機遮罩 -->
    <main class="content">
      <div class="content-inner">...</div>        <!-- Markdown 內容 -->
    </main>
  </div>

  <!-- 底部作者資訊（三層） -->
  <footer class="site-footer">
    <div class="footer-author">...</div>          <!-- 作者介紹 -->
    <div class="footer-links">...</div>           <!-- 社群連結 -->
    <div class="footer-license">...</div>         <!-- 授權聲明 -->
  </footer>
</body>
```

外部依賴（CDN）：
- `marked.js`：Markdown → HTML 渲染
- `highlight.js` + 語言包（python, bash, json, javascript, xml, css）
- highlight.js 主題：`atom-one-light`（暖色系友好）

參考模板：`references/index_template.html`

### Step 7：產生 style.css

參考模板：`references/style_template.css`

#### 預設配色方案（暖色系）

| CSS 變數 | 色碼 | 用途 |
|----------|------|------|
| `--color-bg` | `#FDF8F0` | 頁面背景（米白） |
| `--color-sidebar` | `#F5E6D3` | 側邊欄背景（奶茶） |
| `--color-primary` | `#D4A574` | 主色調（暖棕） |
| `--color-accent` | `#E8976B` | 強調色（柔和橘） |
| `--color-text` | `#3D2B1F` | 主文字（深咖啡） |
| `--color-code-bg` | `#F9F2EB` | 程式碼背景（淺暖灰） |
| `--color-footer-bg` | `#3D2B1F` | 頁尾背景（深咖啡） |

#### 色彩風格切換（設定面板內建 4 種主題）

設定面板中除了文字大小，還提供 **色彩風格** 區塊，讓使用者即時切換整站配色。
切換原理：在 `<body>` 上加對應 class（如 `theme-ocean`），用 CSS 覆蓋 `:root` 變數。
`warm` 為預設，不加 class；其餘三種各加一個 `body.theme-{name}` 區塊。
選擇存入 `localStorage` key `color-theme`，重開自動還原。

##### 4 種主題一覽

| data-theme | 名稱 | header 漸層 | sidebar | primary | accent | footer-bg | footer-license |
|------------|------|-------------|---------|---------|--------|-----------|----------------|
| `warm` | 暖棕奶茶（預設） | `#5C3D2E → #3D2B1F` | `#F5E6D3` | `#D4A574` | `#E8976B` | `#3D2B1F` | `#2C1E14` |
| `ocean` | 冷靜海洋 | `#2C5F7C → #1B3A4B` | `#E8ECF1` | `#5B7FA5` | `#4A90D9` | `#1B3A4B` | `#122830` |
| `forest` | 森林自然 | `#3E5C2A → #2E3D1F` | `#E0EDD3` | `#6B9B5A` | `#8BC34A` | `#2E3D1F` | `#1F2A14` |
| `sakura` | 櫻花粉柔 | `#5C2D33 → #3D1F22` | `#FFE4E4` | `#D4838A` | `#E8636B` | `#3D1F22` | `#2C1418` |

##### 每個主題的完整 CSS 變數（以 ocean 為例）

```css
body.theme-ocean {
  --color-bg: #F5F7FA;
  --color-sidebar: #E8ECF1;
  --color-sidebar-hover: #D8DFE8;
  --color-sidebar-active: #5B7FA5;
  --color-primary: #5B7FA5;
  --color-primary-dark: #486A8C;
  --color-accent: #4A90D9;
  --color-text: #2D3748;
  --color-text-light: #4A5568;
  --color-text-muted: #718096;
  --color-border: #CBD5E0;
  --color-code-bg: #EDF2F7;
  --color-code-border: #D2DCE6;
  --color-white: #FFFFFF;
  --color-footer-bg: #1B3A4B;
  --color-footer-text: #E8ECF1;
  --shadow-sm: 0 1px 3px rgba(45, 55, 72, 0.08);
  --shadow-md: 0 4px 12px rgba(45, 55, 72, 0.1);
  --shadow-lg: 0 8px 24px rgba(45, 55, 72, 0.12);
}
body.theme-ocean .site-header {
  background: linear-gradient(135deg, #2C5F7C 0%, #1B3A4B 100%);
}
body.theme-ocean .footer-license { background: #122830; }
body.theme-ocean .copy-btn.copied { background: #2B6CB0; }
```

其餘 `forest`、`sakura` 同樣結構，替換對應色碼即可（見上方一覽表）。

##### 設定面板 HTML（色彩風格區塊）

放在文字大小 `.settings-group` 之後：

```html
<div class="settings-group">
  <label class="settings-label">色彩風格</label>
  <div class="theme-grid" id="themeOptions">
    <button class="theme-card active" data-theme="warm">
      <div class="theme-preview">
        <span class="tp-bar" style="background:#5C3D2E"></span>
        <span class="tp-bar" style="background:#F5E6D3"></span>
        <span class="tp-bar" style="background:#D4A574"></span>
        <span class="tp-bar" style="background:#E8976B"></span>
      </div>
      <span class="theme-name">暖棕奶茶</span>
    </button>
    <button class="theme-card" data-theme="ocean">
      <div class="theme-preview">
        <span class="tp-bar" style="background:#1B3A4B"></span>
        <span class="tp-bar" style="background:#E8ECF1"></span>
        <span class="tp-bar" style="background:#5B7FA5"></span>
        <span class="tp-bar" style="background:#4A90D9"></span>
      </div>
      <span class="theme-name">冷靜海洋</span>
    </button>
    <button class="theme-card" data-theme="forest">
      <div class="theme-preview">
        <span class="tp-bar" style="background:#2E3D1F"></span>
        <span class="tp-bar" style="background:#E0EDD3"></span>
        <span class="tp-bar" style="background:#6B9B5A"></span>
        <span class="tp-bar" style="background:#8BC34A"></span>
      </div>
      <span class="theme-name">森林自然</span>
    </button>
    <button class="theme-card" data-theme="sakura">
      <div class="theme-preview">
        <span class="tp-bar" style="background:#5C2D33"></span>
        <span class="tp-bar" style="background:#FFE4E4"></span>
        <span class="tp-bar" style="background:#D4838A"></span>
        <span class="tp-bar" style="background:#E8636B"></span>
      </div>
      <span class="theme-name">櫻花粉柔</span>
    </button>
  </div>
</div>
```

##### 主題選擇卡 CSS

```css
.theme-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.theme-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 8px;
  background: var(--color-white);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}
.theme-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}
.theme-card.active {
  border-color: var(--color-accent);
  background: var(--color-code-bg);
  box-shadow: 0 0 0 1px var(--color-accent);
}
.theme-preview {
  display: flex; gap: 4px; width: 100%; height: 28px;
  border-radius: var(--radius-sm); overflow: hidden;
}
.tp-bar { flex: 1; border-radius: 3px; }
.theme-name {
  font-size: 12px; font-weight: 600;
  color: var(--color-text); white-space: nowrap;
}
```

##### script.js 主題切換邏輯

需要的常數與 DOM：
```js
const themeOptions = document.getElementById('themeOptions');
var STORAGE_KEY_THEME = 'color-theme';
var THEME_LIST = ['warm', 'ocean', 'forest', 'sakura'];
```

restoreSettings 中加入：
```js
var savedTheme = localStorage.getItem(STORAGE_KEY_THEME) || 'warm';
setTheme(savedTheme);
```

initSettingsPanel 中加入事件監聽：
```js
if (themeOptions) {
  themeOptions.addEventListener('click', function (e) {
    var btn = e.target.closest('.theme-card');
    if (!btn) return;
    var theme = btn.getAttribute('data-theme');
    setTheme(theme);
    localStorage.setItem(STORAGE_KEY_THEME, theme);
  });
}
```

setTheme 函式：
```js
function setTheme(theme) {
  THEME_LIST.forEach(function (t) {
    document.body.classList.remove('theme-' + t);
  });
  if (theme !== 'warm') {
    document.body.classList.add('theme-' + theme);
  }
  if (themeOptions) {
    var cards = themeOptions.querySelectorAll('.theme-card');
    cards.forEach(function (card) {
      card.classList.toggle('active', card.getAttribute('data-theme') === theme);
    });
  }
}
```

#### 設計規範
- 間距基數：8px（8, 16, 24, 32, 48, 64）
- 字型：`"Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif`
- 等寬字型：`"Fira Code", "Source Code Pro", "Consolas", monospace`
- 圓角：sm 4px / md 8px / lg 12px
- WCAG AA 對比度

#### 響應式斷點
- 桌面：側邊欄固定 280px，按鈕顯示圖示+文字
- 平板（≤1024px）：按鈕隱藏文字標籤
- 手機（≤768px）：側邊欄改為漢堡選單抽屜，全寬內容區
- 小螢幕（≤480px）：進一步縮減間距

### Step 8：產生 script.js

核心功能：
1. **導覽列動態建構**：從 UNITS_DATA 產生 `<li>` 按鈕
2. **群組展開/收合**：點擊群組標題切換子單元可見性
3. **Markdown 渲染**：`marked.parse()` + `hljs.highlight()` 程式碼高亮
4. **程式碼複製按鈕**：為每個 `<pre>` 加上 hover 顯示的「複製」按鈕
5. **手機選單**：漢堡按鈕開關側邊欄 + 遮罩層
6. **全螢幕切換**：Fullscreen API + 圖示切換
7. **鍵盤導航**：左右方向鍵切換上/下一單元
8. **回到頂部按鈕**：滾動超過 400px 時顯示
9. **側邊欄拖拉調整寬度**：右邊框可拖拉（200px~500px），寬度存入 localStorage
10. **設定面板**：側邊欄底部齒輪按鈕，點擊開啟設定面板
11. **文字大小切換**：「適中/大/超大」三段，存入 localStorage，套用 CSS class
12. **色彩風格切換**：4 種主題（暖棕奶茶/冷靜海洋/森林自然/櫻花粉柔），切換 body class 覆蓋 CSS 變數，存入 localStorage key `color-theme`
13. **設定持久化**：側邊欄寬度、文字大小、色彩風格存入 localStorage，重開自動還原

參考模板：`references/script_template.js`

### Step 9：測試驗證

1. 在瀏覽器中開啟 index.html
2. 檢查：導覽切換是否正常、Markdown 渲染是否正確、程式碼高亮是否生效
3. 測試全螢幕按鈕、複製按鈕、鍵盤導航
4. 縮小視窗測試響應式設計

### Step 10：提供使用說明

告知使用者：
1. 日後更新 md 內容後，執行 `py -3 build.py` 即可重新產生 units.js
2. 直接開啟 index.html 即可瀏覽
3. 若需部署，整個 website/ 資料夾上傳即可（純靜態）

---

## 頂部快捷按鈕設計

按鈕使用圓角膠囊形（桌面版顯示圖示+文字，平板/手機版只顯示圖示）。
常見按鈕類型：

| 類型 | SVG | 說明 |
|------|-----|------|
| 全螢幕 | expand arrows | 切換 Fullscreen API，圖示隨狀態變化 |
| YouTube | play triangle in box | 外連到 YouTube 頻道 |
| Facebook | f logo | 外連到 FB 社團/粉專 |
| Email | envelope | mailto: 連結 |
| GitHub | octocat | 外連到 GitHub repo |

按鈕樣式：`background: rgba(255,255,255,0.12)`，hover 時加亮。
全螢幕啟用時加 `.fullscreen-active` class 高亮。

---

## 底部作者資訊區設計

三層結構：

### 第一層：作者介紹（`.footer-author`）
- 背景：側邊欄色
- 左側照片 + 右側文字（姓名、職稱標籤、獲獎列表）
- 手機版改為上下堆疊

### 第二層：社群連結（`.footer-links`）
- 背景：深色
- 水平排列的彩色按鈕（YouTube 紅、Facebook 藍、Email 主色）

### 第三層：授權聲明（`.footer-license`）
- 背景：最深色
- 置中文字，小字號

---

## 注意事項

- build.py 的 print 語句避免使用 emoji（Windows cp950 編碼不支援）
- 使用 `json.dumps(content, ensure_ascii=False)` 確保中文正確
- units.js 使用 `<script>` 標籤載入（非 fetch），確保 file:// 協定下也能運作
- highlight.js 語言包按需載入，常用：python, bash, json, javascript, xml, css
- 側邊欄使用 `position: fixed`，內容區使用 `margin-left: var(--sidebar-width)`
- footer 也需要 `margin-left: var(--sidebar-width)`，手機版歸零
