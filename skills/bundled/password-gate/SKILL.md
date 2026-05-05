---
name: password-gate
description: |
  為靜態 HTML 網站加上 SHA-256 雜湊密碼閘門（Password Gate）。
  支援一般使用者密碼 + 管理員密碼（含新增/刪除密碼的管理面板）。
  密碼不以明文存在原始碼中，全部以 SHA-256 雜湊儲存與比對。
  使用時機：當使用者要求「加密碼保護」「密碼閘門」「password gate」「網站加鎖」
  「限制存取」「加上登入畫面」「密碼登錄視窗」「密碼視窗」「密碼網頁」「密碼網頁登錄」
  「登入密碼」「密碼登入」「加密碼」「網頁密碼」「password login」「login page」
  或任何需要為靜態 HTML 頁面加上前端密碼驗證的場景。
  也適用於已有密碼系統但使用明文、需要升級為 SHA-256 雜湊的情況。
---

# Password Gate — 靜態網站 SHA-256 密碼保護

為任意靜態 HTML 網站加上全螢幕密碼閘門，無需後端伺服器。

> **重要提醒**：這是前端密碼機制，僅作為「閱讀阻擋」用途，不構成真正的安全保護。
> 原始碼中不含明文密碼，但有經驗的使用者仍可透過開發者工具繞過。

## 核心機制

| 元件 | 說明 |
|------|------|
| 雜湊演算法 | `crypto.subtle.digest('SHA-256', ...)` — 瀏覽器原生 API |
| 登入狀態 | `sessionStorage` — 關閉分頁即失效 |
| 密碼清單 | `localStorage` — 儲存 SHA-256 雜湊陣列（非明文） |
| 管理面板 | 輸入管理員密碼後顯示，可新增/刪除使用者密碼 |

## 使用方式

### 方式一：使用腳本自動注入（推薦）

```bash
node <skill-path>/scripts/add-password-gate.js <target.html> \
  --user-password "你的使用者密碼" \
  --admin-password "你的管理員密碼" \
  --title "網站標題" \
  --subtitle "請輸入密碼以進入" \
  --storage-key "my_site_pw_hashes" \
  --session-key "my_site_authed"
```

腳本會：
1. 計算兩組密碼的 SHA-256 雜湊
2. 在 `<body>` 開頭注入密碼閘門 HTML + CSS + JS
3. 原始碼中只留雜湊值，不留明文

### 方式二：手動整合

若目標 HTML 結構特殊或需要高度客製化，按以下步驟手動操作：

#### Step 1：產生 SHA-256 雜湊

```bash
node <skill-path>/scripts/hash-password.js "你的密碼"
```

或用 bash：
```bash
echo -n "你的密碼" | sha256sum
```

#### Step 2：插入 HTML

在 `<body>` 最前面加入密碼閘門 HTML（參考 `assets/password-gate.html`）。

#### Step 3：插入 CSS

在 `<head>` 的 `<style>` 中加入閘門樣式（參考 `assets/password-gate.css`）。

#### Step 4：插入 JS

在頁面底部 `</body>` 前加入密碼邏輯（參考 `assets/password-gate.js`）。
需替換的變數：
- `__ADMIN_HASH__` → 管理員密碼的 SHA-256 雜湊
- `__DEFAULT_HASH__` → 使用者密碼的 SHA-256 雜湊
- `__HASH_STORAGE_KEY__` → localStorage key（如 `my_site_pw_hashes`）
- `__SESSION_KEY__` → sessionStorage key（如 `my_site_authed`）

## 設計規格

### 閘門外觀
- 全螢幕深色漸層背景（`#1a1a2e → #16213e → #0f3460`）
- 毛玻璃卡片（`backdrop-filter: blur(20px)`）
- 浮動 emoji 圖示 + 標題 + 副標題
- 密碼輸入框（含顯示/隱藏切換）
- 漸層送出按鈕
- 錯誤訊息紅字

### 管理員面板
- 點擊「管理員」文字展開
- 輸入管理員密碼後顯示管理面板
- 顯示目前密碼清單（只顯示雜湊前 8 碼 + `...`）
- 可新增密碼（自動轉 SHA-256 後存入）
- 可刪除密碼（至少保留一組）
- 管理員密碼驗證後可直接進入網站

### 雙角色驗證流程

```
使用者輸入密碼
  ├─ SHA-256(輸入) === ADMIN_HASH → 顯示管理面板 + 可進入網站
  ├─ SHA-256(輸入) ∈ localStorage 雜湊清單 → 直接進入網站
  └─ 都不符合 → 顯示「密碼錯誤」
```

## 客製化選項

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `--title` | `密碼保護` | 閘門標題 |
| `--subtitle` | `請輸入密碼以進入` | 閘門副標題 |
| `--emoji` | `⚡` | 閘門圖示（任意 emoji） |
| `--btn-text` | `驗證並進入` | 送出按鈕文字 |
| `--gradient` | `#667eea,#764ba2` | 按鈕漸層色 |
| `--storage-key` | `site_pw_hashes` | localStorage key |
| `--session-key` | `site_authed` | sessionStorage key |
| `--disclaimer` | `本機制僅為閱讀阻擋，非安全保護措施` | 免責聲明文字 |

## 批次處理多個 HTML

若需要對整個資料夾的 HTML 檔案加上密碼保護：

```bash
# 用 Node.js 批次處理
for f in slides/CH*.html; do
  node <skill-path>/scripts/add-password-gate.js "$f" \
    --user-password "@AISkill2026" \
    --admin-password "Aa@0981737608" \
    --storage-key "skill_course_pw_hashes" \
    --session-key "skill_course_authenticated"
done
```

> 腳本具備冪等性：若偵測到已有密碼閘門（`id="passwordGate"` 或 `id="pwOverlay"`），會跳過不重複注入。

## 檔案結構

```
password-gate/
├── SKILL.md              ← 本文件
├── assets/
│   ├── password-gate.html  ← 閘門 HTML 片段（含佔位符）
│   ├── password-gate.css   ← 閘門 CSS 樣式
│   └── password-gate.js    ← 閘門 JS 邏輯（SHA-256）
└── scripts/
    ├── add-password-gate.js  ← 自動注入腳本
    └── hash-password.js      ← SHA-256 雜湊產生工具
```
