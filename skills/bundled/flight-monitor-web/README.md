# 機票監控互動網站 — AI Skill 使用教學

## 這是什麼？

這個 Skill 能讓 AI（Claude Code / Codex 類代理）根據「黃仁蝦機票監控」的 Python 程式碼，
自動生成一個完整的**互動式機票比價網站**，也能擴充成「票價監控 + 航班資訊 API」的混合版本，具備：

- 即時查詢 Trip.com 機票價格
- 視覺化比價儀表板 + 價格趨勢圖
- 低價警報推播 Telegram
- 定時自動監控
- 可選擇串接 Aviationstack 補充航班狀態 / 機場 / 航線資料

---

## 資料夾結構

```
flight-monitor-web/
├── SKILL.md                      ← AI 讀這個（Skill 主檔案）
├── README.md                     ← 你讀這個（使用教學）
└── assets/
    └── huang_shrimp_flight.py    ← 黃仁蝦機票監控程式碼
```

---

## 先理解這個技能怎麼用

這個 Skill 的核心不是直接提供一個現成網站，而是讓 AI 依照：

- `assets/huang_shrimp_flight.py` 的票價監控邏輯
- `SKILL.md` 的介面規格與產出規則

自動替你生成一個新的網站專案，或把既有專案補強成完整的航班監控應用。

如果你想讓 AI 直接開始產生，可用這類提示：

```text
幫我用 flight-monitor-web 技能，做一個機票監控網站。
```

```text
幫我把這個技能做成「Trip.com 比價 + Aviationstack 航班資訊」混合版網站。
```

```text
幫我做純前端版本，不要後端，但保留 Telegram 設定區與價格歷史。
```

---

## 使用步驟

### 前置準備

1. **安裝 Claude Code**（如果還沒裝）
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **確認 Node.js 18+ 已安裝**
   ```bash
   node -v
   ```

3. **確認 Python 3.10+ 已安裝**（如果要用後端爬蟲功能）
   ```bash
   python --version
   ```

4. **確認 Playwright 已安裝**（如果要用後端爬蟲功能）
   ```bash
   pip install playwright
   playwright install chromium
   ```

---

## API Key / Token 教學

這個技能已經整合「教學型說明」與「安全實務」，你可以直接拿來教學生。

### `AVIATIONSTACKAPIKEY` 是什麼？

- 它是你在 Aviationstack 申請到的 API Key
- 本質上就是呼叫航空資料 API 的「門禁卡」
- 沒有這把 Key，就不能合法使用該服務的資料端點

### 怎麼申請 Aviationstack API Key？

你可以照這個流程申請：

1. 到官網註冊：`https://aviationstack.com`
2. 點選註冊或免費方案
3. 完成 Email 驗證與登入
4. 進入 Dashboard
5. 找到你的 API Key
6. 複製下來，之後用在 `AVIATIONSTACKAPIKEY`

你可以這樣教學生：

- `API Key` 就像網站服務發給你的門禁卡
- 註冊後，平台會給你一組專屬金鑰
- 之後程式呼叫 API 時，要把這組金鑰一起帶上

### Aviationstack 可以拿來做什麼？

- 即時航班狀態
- 機場資料
- 航線資料
- 飛機與航空公司資訊

### 這個技能什麼時候需要 `AVIATIONSTACKAPIKEY`？

- 只做 Trip.com 比價網站：不一定需要
- 要加上航班狀態、機場資訊、API 型查詢面板：建議加入
- 要把網站升級成「智慧航班助理」：建議加入

### 很重要：不要公開 API Key

- 不要放 GitHub
- 不要寫死在前端 JavaScript
- 不要直接貼在 `index.html`

正確做法是放在環境變數，讓後端或本機執行環境去讀取。

如果你的情境是：

- 免費方案 API Key
- 只在本機教學或個人練習
- 不會部署到公開網站

那麼風險會低很多。這種情況下，你可以在本機測試時暫時手動貼入設定值；
但只要準備上傳、分享或部署，仍然建議改回環境變數或後端代理模式。

### Windows PowerShell 設定範例

```powershell
$env:AVIATIONSTACKAPIKEY="你的APIKey"
$env:TELEGRAM_BOT_TOKEN="你的BotToken"
$env:TELEGRAM_CHAT_ID="你的ChatID"
$env:LINE_CHANNEL_ACCESS_TOKEN="你的LineChannelAccessToken"
$env:LINE_USER_ID="你的LineUserId"
```

### 怎麼把 API Key 給這個 Skill？

這個 Skill 目前支援兩種做法。

#### 做法 A：用環境變數給 Skill

這是最推薦的方式。

1. 開啟 PowerShell
2. 先輸入：

```powershell
$env:AVIATIONSTACKAPIKEY="你的AviationstackAPIKey"
```

3. 如果你也要用 Telegram，再補：

```powershell
$env:TELEGRAM_BOT_TOKEN="你的TelegramBotToken"
$env:TELEGRAM_CHAT_ID="你的TelegramChatID"
```

如果你要用 LINE Bot，再補：

```powershell
$env:LINE_CHANNEL_ACCESS_TOKEN="你的LineChannelAccessToken"
$env:LINE_USER_ID="你的LineUserId"
```

4. 在同一個終端機視窗內啟動 Claude Code / Codex 或執行相關程式
5. 此時 Skill 產生的 Python 程式或後端程式就能讀到這些值

也就是說，Skill 不是靠你把 Key 寫進 `SKILL.md`，而是靠執行環境去提供這些值。

#### 臨時設定 vs 永久設定

上面的 `$env:...` 寫法是「只對目前這個 PowerShell 視窗有效」。

如果你關掉視窗，之後要再開新的終端機，就需要重新設定一次。

如果你想讓電腦之後都能直接讀到，可以改用永久設定。

#### Windows 永久設定方式 1：使用 `setx`

在 PowerShell 執行：

```powershell
setx AVIATIONSTACKAPIKEY "你的AviationstackAPIKey"
setx TELEGRAM_BOT_TOKEN "你的TelegramBotToken"
setx TELEGRAM_CHAT_ID "你的TelegramChatID"
setx LINE_CHANNEL_ACCESS_TOKEN "你的LineChannelAccessToken"
setx LINE_USER_ID "你的LineUserId"
```

注意：

- `setx` 設定後，不會回寫到目前這個 PowerShell 視窗
- 你要關掉目前終端機，再開一個新的 PowerShell，設定才會生效

你可以開新視窗後驗證：

```powershell
echo $env:AVIATIONSTACKAPIKEY
echo $env:TELEGRAM_BOT_TOKEN
echo $env:TELEGRAM_CHAT_ID
echo $env:LINE_CHANNEL_ACCESS_TOKEN
echo $env:LINE_USER_ID
```

#### Windows 永久設定方式 2：用系統介面手動加入

1. 在 Windows 搜尋輸入「環境變數」
2. 打開「編輯系統環境變數」
3. 點「環境變數」
4. 在「使用者變數」區塊按「新增」
5. 依序加入：

- 變數名稱：`AVIATIONSTACKAPIKEY`
- 變數值：你的 Aviationstack API Key

- 變數名稱：`TELEGRAM_BOT_TOKEN`
- 變數值：你的 Telegram Bot Token

- 變數名稱：`TELEGRAM_CHAT_ID`
- 變數值：你的 Telegram Chat ID

- 變數名稱：`LINE_CHANNEL_ACCESS_TOKEN`
- 變數值：你的 LINE Messaging API Channel Access Token

- 變數名稱：`LINE_USER_ID`
- 變數值：你的 LINE 使用者 ID

6. 全部按確定
7. 重新開啟 PowerShell 或你的開發工具

#### 建議怎麼選？

- 只是測試今天能不能跑：用 `$env:...`
- 之後會常常用這個 Skill：用 `setx` 或系統環境變數
- 只是做本機前端示範：可用 localStorage 測試模式

#### 做法 B：本機測試時，手動貼到網站設定區

如果你只是：

- 本機自己測試
- 教學示範
- 不公開部署

那可以請 AI 生成一個「設定面板」，讓你把 API Key 貼進去，再存到 `localStorage`。

這種情況你可以這樣對 Skill 說：

```text
幫我做本機教學版，Aviationstack API Key 由使用者手動輸入並暫存在 localStorage。
```

如果你要走標準安全做法，則可以這樣說：

```text
幫我做有後端的版本，Aviationstack API Key 從環境變數 AVIATIONSTACKAPIKEY 讀取，不要暴露在前端。
```

### Python 讀取範例

```python
import os

aviationstack_api_key = os.getenv("AVIATIONSTACKAPIKEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
line_channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_user_id = os.getenv("LINE_USER_ID")
```

### 怎麼申請 LINE Bot？

如果很多使用者習慣用 LINE，這個技能可以分成兩層來做。

#### 第一層：基礎版

先教你怎麼：

- 申請 LINE Bot
- 拿到 Token
- 拿到 `LINE_USER_ID`
- 成功收到推播

#### 第二層：進階版

再加上：

- 完整對話機器人
- 多指令解析
- 資料庫
- Rich menu

下面先寫第一層，也就是大多數人最先需要的「基礎版 LINE 推播整合」。

申請流程：

1. 到 `https://developers.line.biz/` 註冊並登入
2. 進入 `LINE Developers Console`
3. 建立 Provider
4. 建立 `Messaging API` Channel
5. 在 Channel 設定中啟用 Messaging API
6. 取得 `Channel access token`
7. 取得要接收通知的 `User ID`

### LINE Bot 需要哪些值？

- `LINE_CHANNEL_ACCESS_TOKEN`
  這是呼叫 LINE Messaging API 的授權 Token
- `LINE_USER_ID`
  這是你要接收推播的 LINE 使用者 ID

### 怎麼取得 LINE User ID？（基礎版）

常見做法有兩種：

1. 讓你的 LINE Bot 接收使用者訊息，再從 webhook event 取出 `userId`
2. 使用你自己已有的 LINE Bot 後台或 webhook 紀錄查看 `source.userId`

如果是教學版，最簡單的做法通常是：

- 先建立一個最基礎可用的 LINE Bot
- 把 webhook 指到你自己的測試端點
- 傳一則訊息給 Bot
- 從 webhook 收到的 JSON 內找到 `source.userId`

### 怎麼把 LINE Bot 設定給這個 Skill？（基礎版）

如果你想讓 Skill 生成 LINE 推播版網站或後端，可以直接這樣說：

```text
幫我用 flight-monitor-web 技能做一個機票監控網站，通知方式改成 LINE Bot，請從 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_USER_ID 讀取設定。
```

如果你要 Telegram 和 LINE 都保留，也可以這樣說：

```text
幫我保留 Telegram 與 LINE 兩種推播方式，Telegram 用 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID，LINE 用 LINE_CHANNEL_ACCESS_TOKEN / LINE_USER_ID。
```

### 進階版 LINE Bot 可以擴充到什麼程度？

如果你要的是第二層，也就是完整 LINE Bot，README 建議你把需求直接講清楚，像這樣：

```text
幫我把 flight-monitor-web 升級成完整 LINE Bot 版本，要有 webhook、指令解析、資料庫、Rich menu。
```

你也可以指定更細的功能：

- `/price` 查詢指定航線價格
- `/watch` 啟動價格監控
- `/stop` 停止監控
- `/status` 查看目前監控狀態
- 使用資料庫保存每位使用者的訂閱條件
- 用 Rich menu 提供常用操作按鈕
- 支援多使用者或群組

如果你要把這一層直接當成完整版需求，可以這樣理解：

- `/price` 查指定航線價格
- `/watch` 啟動監控
- `/stop` 停止監控
- `/status` 查看監控狀態
- 資料庫保存訂閱條件
- Rich menu 一鍵操作
- 支援多使用者或群組

### README 的建議閱讀順序

如果你是第一次做，建議這樣走：

1. 先完成基礎版 LINE 推播整合
2. 確認通知能正常送達
3. 再升級成進階版完整 LINE Bot

這樣做的好處是：

- 先把推播打通
- 先拿到 `LINE_USER_ID`
- 之後再加 webhook 指令、資料庫、Rich menu，比較不會卡住

### 對 Skill 下指令的建議寫法

如果你已經申請好 API Key，並且已經放進環境變數，可以直接這樣對 AI 說：

```text
幫我用 flight-monitor-web 技能做一個機票監控網站，並加入 Aviationstack。API Key 會從環境變數 AVIATIONSTACKAPIKEY 讀取。
```

如果你只是本機練習，可以這樣說：

```text
幫我做本機版 flight-monitor-web，Aviationstack API Key 由前端設定區手動輸入即可。
```

### Aviationstack API 呼叫範例

```text
https://api.aviationstack.com/v1/flights?access_key=你的APIKEY
```

---

### Step 1：安裝 Skill

將整個 `flight-monitor-web` 資料夾複製到 Claude Code 的 Skill 目錄：

**全域安裝（所有專案都能用）：**
```bash
cp -r flight-monitor-web/ ~/.claude/skills/flight-monitor/
```

**專案安裝（僅限特定專案）：**
```bash
cp -r flight-monitor-web/ ./your-project/.claude/skills/flight-monitor/
```

**驗證安裝：**
在 Claude Code 中輸入：
```
/skills
```
確認看到「機票監控互動網站產生器」。

---

### Step 2：啟動 Skill（基本用法）

在 Claude Code 中輸入：

```
幫我用機票監控程式做一個互動式比價網站
```

AI 會自動：
1. 讀取 huang_shrimp_flight.py
2. 詢問你的技術偏好
3. 判斷你要不要加入 Aviationstack API 擴充
4. 生成完整網站程式碼

---

### Step 3：回答 AI 的問題

AI 會問你幾個問題來客製化網站：

| 問題 | 建議選項 | 說明 |
|------|---------|------|
| 前端框架？ | **純 HTML/CSS/JS** | 最簡單，零依賴，適合快速部署 |
| 需要後端嗎？ | **要（Python FastAPI）** | 才能用 Playwright 即時爬蟲 |
| 部署平台？ | **本機執行** 或 **Netlify** | 本機最快，Netlify 可分享 |
| 保留 Telegram？ | **是** | 外出也能收到低價警報 |
| 帳號系統？ | **否** | 個人使用不需要 |
| 要加 Aviationstack 嗎？ | **看需求** | 想做航班資訊面板、航班追蹤或智慧助理時建議開 |

---

### Step 4：設定 Telegram 推播（選用）

如果要使用 Telegram 低價警報功能：

1. **建立 Bot**
   - 在 Telegram 搜尋 `@BotFather`
   - 輸入 `/newbot`
   - 取得 Bot Token（格式：`123456:ABC-DEF...`）

2. **取得 Chat ID**
   - 在 Telegram 搜尋 `@userinfobot`
   - 傳任意訊息
   - 取得你的 Chat ID（純數字）

3. **填入網站設定**
   - 開啟網站 → Telegram 設定區
   - 貼上 Bot Token 和 Chat ID
   - 點「測試推播」確認成功
   - 如果只是本機使用，暫存於瀏覽器 localStorage 也可以

### Step 4-1：設定 Aviationstack（選用）

如果你要讓網站顯示：

- 航班狀態
- 機場資訊
- 航線資料
- API 型智慧查詢

請先到 `https://aviationstack.com` 註冊並取得 API Key。

建議做法：

1. 將 API Key 設成環境變數 `AVIATIONSTACKAPIKEY`
2. 由後端 API 代為呼叫 Aviationstack
3. 前端只呼叫你自己的 `/api/*` 端點，不直接暴露 Key

本機教學版可接受的簡化做法：

1. 在本機頁面設定區手動貼入免費 API Key
2. 儲存在 localStorage 僅供自己測試
3. 若之後要部署，再切換成環境變數版本

如果你是在教學情境中示範，可以直接這樣講：

`API Key = 網路服務的門禁卡。`

---

### Step 5：啟動網站

**純前端方案（最簡單）：**
```bash
# 進入生成的專案目錄
cd flight-monitor-web

# 用任一靜態伺服器開啟
npx serve .
# 或
python -m http.server 8080
```
打開瀏覽器 → `http://localhost:8080`

**有後端方案（完整功能）：**
```bash
# 安裝後端依賴
cd flight-monitor-web/server
pip install -r requirements.txt

# 啟動後端
python app.py

# 另開終端，啟動前端
cd ..
npx serve .
```

---

### Step 6：開始使用

1. **選擇目的地**：福岡 / 大阪 / 東京 / 沖繩 / 首爾 / 釜山
2. **選擇日期**：出發日 + 回程日
3. **設定門檻**：例如 TWD 10,000
4. **點「立即查詢」**：看到即時比價結果 + 價格趨勢圖
5. **點「啟動監控」**：AI 會定時幫你盯，低價自動推播 Telegram

---

## 進階用法

### 客製化提示詞範例

如果你想要更具體的網站風格，可以這樣說：

```
幫我做一個機票監控網站，要有以下功能：
- 深色主題，科技風格
- 價格趨勢用折線圖顯示
- 低價時整個頁面閃紅色警報
- 手機版也要能完整操作
- 加上城市的美圖當背景
```

如果你想把 `參考.md` 那種 API 教學風格一起融入網站或教材，可以直接這樣說：

```text
幫我把 Aviationstack API Key 的用途、取得方式、環境變數與安全觀念，一起融入這個機票監控網站的教學區塊。
```

```text
幫我做成智慧航班助理，前端查票價，後端用 Aviationstack 提供航班資訊，並解釋 API Key 是什麼。
```

### 新增目的地

如果需要支援更多城市，告訴 AI：

```
幫我新增曼谷（bkk）和新加坡（sin）到機票監控網站
```

### 部署到 Netlify

```
幫我把機票監控網站部署到 Netlify
```

---

## 支援的目的地

| 目的地 | 機場代碼 | Trip.com 代碼 |
|--------|---------|--------------|
| 福岡   | FUK     | fuk          |
| 大阪   | KIX     | osa          |
| 東京   | NRT/HND | tyo          |
| 沖繩   | OKA     | oka          |
| 首爾   | ICN     | sel          |
| 釜山   | PUS     | pus          |

出發地固定為：**台北桃園 TPE**

---

## 常見問題

### Q: 沒有 Python / Playwright 怎麼辦？
A: 告訴 AI「我沒有安裝 Python，幫我做純前端版本」。
AI 會改用 iframe 嵌入 Trip.com 或手動輸入價格的方案。

### Q: Telegram 推播失敗？
A: 檢查 Bot Token 和 Chat ID 是否正確。
在網站的 Telegram 設定區點「測試推播」驗證。

### Q: 價格抓不到？
A: Trip.com 頁面載入需要時間，Playwright 預設等 8 秒。
如果經常失敗，告訴 AI「把等待時間加到 15 秒」。

### Q: 可以加其他航班平台嗎？
A: 可以！告訴 AI「幫我加上 Skyscanner 比價」，AI 會新增對應的爬蟲模組。

### Q: `AVIATIONSTACKAPIKEY` 一定要有嗎？
A: 不一定。純 Trip.com 比價模式可以先不接；如果要做航班狀態、機場資料、航線 API，才建議加入。

### Q: 為什麼不能把 API Key 直接寫在前端？
A: 因為瀏覽器原始碼會被看見，等於把門禁卡公開。正確做法是放在環境變數，並由後端代理呼叫。

### Q: 如果只是本機、免費 Key，直接放在 localStorage 可以嗎？
A: 可以，做教學示範或個人練習通常沒問題。只是這應該視為「本機測試模式」，不是公開部署的標準做法。

---

## 注意事項

- 本工具僅供個人使用，請勿用於商業爬蟲
- 查詢頻率建議不低於 30 分鐘一次，避免被 Trip.com 封鎖
- Telegram Bot Token 是敏感資訊，請勿公開分享
- Aviationstack API Key 是敏感資訊，請勿公開分享
- Line Bot Token 是敏感資訊，請勿公開分享
- 機票價格會即時變動，查詢結果僅供參考
- 資料來源：IATA (International Air Transport Association) via Trip.com (tw.trip.com)
