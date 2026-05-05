# LiangClaw 完整安裝佈署教學

> 阿亮老師 AI Agent 平台 — 從安裝到上線的完整指南

---

## 目錄

1. [環境準備](#ch1)
2. [安裝步驟](#ch2)
3. [GUI 使用教學（Gradio）](#ch3)
4. [LINE Bot 設定](#ch4)
5. [Telegram Bot 設定](#ch5)
6. [技能管理](#ch6)
7. [模型切換教學](#ch7)
8. [部署到雲端](#ch8)
9. [常見問題 FAQ](#ch9)

---

<a id="ch1"></a>
## Ch1: 環境準備

### 1.1 Python 安裝

LiangClaw 需要 **Python 3.11** 或更新版本。

**Windows:**
1. 前往 https://www.python.org/downloads/
2. 下載 Python 3.11+ 安裝程式
3. 安裝時勾選 **"Add Python to PATH"**
4. 驗證：開啟命令提示字元，輸入 `python --version`

**macOS / Linux:**
```bash
# macOS (Homebrew)
brew install python@3.11

# Ubuntu / Debian
sudo apt update && sudo apt install python3.11 python3.11-venv
```

### 1.2 取得 API 金鑰

你至少需要一組 AI API 金鑰。推薦從 Gemini（免費額度最多）或 Groq（完全免費）開始。

| Provider | 取得方式 | 費用 |
|----------|---------|------|
| **Google Gemini** | https://aistudio.google.com/apikey | 免費額度充足 |
| **Groq** | https://console.groq.com/keys | 完全免費 |
| **OpenAI** | https://platform.openai.com/api-keys | 按量付費 |
| **Anthropic** | https://console.anthropic.com/ | 按量付費 |

### 1.3 （選用）LINE / Telegram 金鑰

如需 Bot 功能，另外準備：

- **LINE Bot**: LINE Developers Console → Channel Access Token + Channel Secret
- **Telegram Bot**: @BotFather → Bot Token

---

<a id="ch2"></a>
## Ch2: 安裝步驟

### 2.1 取得專案

```bash
cd D:/AI教學與專案實作/專案_Claude_Code/LiangClaw
```

### 2.2 建立虛擬環境（建議）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2.3 安裝依賴

```bash
pip install -r requirements.txt
```

主要安裝項目：

| 套件 | 用途 |
|------|------|
| fastapi + uvicorn | Web 後端伺服器 |
| gradio | 聊天 GUI 介面 |
| httpx | 非同步 HTTP 呼叫 |
| python-telegram-bot | Telegram Bot SDK |
| line-bot-sdk | LINE Bot SDK |
| pyyaml | YAML 設定檔解析 |
| python-dotenv | .env 環境變數載入 |
| pytest | 單元測試 |

### 2.4 設定環境變數

```bash
cp .env.example .env
```

用文字編輯器開啟 `.env`，填入你的金鑰：

```env
# 至少填一個
GEMINI_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...

# (選填)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# LINE Bot (選填)
LINE_CHANNEL_ACCESS_TOKEN=
LINE_CHANNEL_SECRET=

# Telegram Bot (選填)
TELEGRAM_BOT_TOKEN=
```

### 2.5 啟動

```bash
python run.py
```

你會看到：

```
╔═══════════════════════════════════════════╗
║  🦞 LiangClaw v1.0.0                     ║
║  阿亮老師 AI Agent 平台                    ║
║                                           ║
║  GUI:       http://localhost:8000/chat     ║
║  API Docs:  http://localhost:8000/docs     ║
║  Health:    http://localhost:8000/health    ║
╚═══════════════════════════════════════════╝
```

### 2.6 驗證安裝

1. 瀏覽器開啟 http://localhost:8000/health → 應回傳 `{"status":"ok"}`
2. 瀏覽器開啟 http://localhost:8000/chat → 看到 Gradio 聊天介面
3. 瀏覽器開啟 http://localhost:8000/docs → 看到 Swagger API 文件

---

<a id="ch3"></a>
## Ch3: GUI 使用教學（Gradio）

### 3.1 進入聊天介面

啟動後，瀏覽器開啟：

```
http://localhost:8000/chat
```

### 3.2 介面說明

| 區域 | 功能 |
|------|------|
| 左側對話區 | 多輪對話，支援複製按鈕 |
| 左下輸入框 | 輸入訊息，按 Enter 或送出按鈕 |
| 右側模型選單 | 下拉選擇模型（Gemini/GPT/Groq/Claude） |
| 右側快速指令 | 常用教育指令捷徑 |
| 右側狀態 | 顯示目前模型、使用 token 數 |

### 3.3 範例對話

試著輸入以下指令：

```
幫我設計一堂適合偏鄉國小三年級的數學教案，主題是分數
```

系統會自動匹配「教案產生器」技能，產生完整教案。

其他範例：
- `設計一份素養導向的自然科評量`
- `幫我規劃一學期的資訊融入教學計畫`
- `分析這份學生成績資料的學習趨勢`
- `設計一個遊戲化的英語學習活動`

### 3.4 模型切換

在右側下拉選單選擇不同模型：

- **gemini-3-flash** — 快速回覆，適合一般對話
- **gemini-3-pro** — 需要深度推理時使用
- **gpt-5.4** — OpenAI 最新模型
- **llama-3.3-70b-versatile** — Groq 免費模型
- **claude-opus-4-6** — 擅長長文分析

---

<a id="ch4"></a>
## Ch4: LINE Bot 設定

### 4.1 建立 LINE Channel

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 登入 LINE 帳號
3. 建立 Provider（如果尚未建立）
4. 建立新 Channel → 選擇 **Messaging API**
5. 填寫 Channel 名稱（例如「阿亮 AI 助教」）

### 4.2 取得金鑰

在 Channel 設定頁面：

1. **Basic settings** → 複製 **Channel secret**
2. **Messaging API** → 點 **Issue** 產生 **Channel access token**

### 4.3 設定 .env

```env
LINE_CHANNEL_ACCESS_TOKEN=你的_access_token
LINE_CHANNEL_SECRET=你的_secret
```

### 4.4 設定 Webhook URL

你需要一個公開的 HTTPS 網址。本機開發可用 ngrok：

```bash
# 安裝 ngrok
# https://ngrok.com/download

ngrok http 8000
```

ngrok 會產生一個公開網址，例如 `https://abc123.ngrok.io`。

在 LINE Developers Console → Messaging API：
- **Webhook URL**: `https://abc123.ngrok.io/line/webhook`
- 啟用 **Use webhook**
- 關閉 **Auto-reply messages**

### 4.5 測試

1. 在 LINE 中加入你的 Bot 好友
2. 傳送任意訊息
3. Bot 應回覆 AI 回應

---

<a id="ch5"></a>
## Ch5: Telegram Bot 設定

### 5.1 建立 Bot

1. 在 Telegram 搜尋 **@BotFather**
2. 傳送 `/newbot`
3. 依提示輸入 Bot 名稱和 username
4. 取得 Bot Token（格式：`123456:ABC-DEF...`）

### 5.2 設定 .env

```env
TELEGRAM_BOT_TOKEN=你的_bot_token
```

### 5.3 設定 Webhook

使用 ngrok（同 LINE Bot 設定）取得公開網址後：

```bash
curl "https://api.telegram.org/bot你的TOKEN/setWebhook?url=https://abc123.ngrok.io/telegram/webhook"
```

成功回應：
```json
{"ok": true, "result": true, "description": "Webhook was set"}
```

### 5.4 可用指令

| 指令 | 說明 |
|------|------|
| `/start` | 開始對話，顯示歡迎訊息 |
| `/help` | 顯示說明 |
| `/skills` | 列出所有可用教育技能 |
| `/model gemini-3-flash` | 切換模型 |

直接輸入文字即可對話。

### 5.5 測試

1. 在 Telegram 搜尋你的 Bot
2. 傳送 `/start`
3. 傳送 `幫我設計教案`

---

<a id="ch6"></a>
## Ch6: 技能管理

### 6.1 技能載入來源

LiangClaw 自動掃描兩個位置：

1. `~/.claude/skills/` — Claude Code 全域技能目錄
2. `skills/bundled/` — 專案內建技能

### 6.2 技能結構

每個技能是一個目錄，至少包含 `SKILL.md`：

```
skill-name/
├── SKILL.md           # (必要) 技能說明與 prompt
├── manifest.json      # (選用) 名稱、標籤、版本
├── scripts/           # (選用) 可執行腳本
└── references/        # (選用) 參考資料
```

### 6.3 manifest.json 範例

```json
{
  "name": "lesson-plan-generator",
  "displayName": "教案產生器",
  "version": "1.0.0",
  "description": "根據教學目標自動生成教案",
  "author": "阿亮老師",
  "tags": ["teaching-design", "教案", "lesson-plan"]
}
```

### 6.4 新增技能

1. 在 `~/.claude/skills/` 或 `skills/bundled/` 建立新目錄
2. 撰寫 `SKILL.md`（技能 prompt 與說明）
3. 選擇性加入 `manifest.json`
4. 重啟 LiangClaw

### 6.5 移除技能

直接刪除該技能目錄，重啟即可。

### 6.6 查看已載入技能

- **API**: `GET http://localhost:8000/api/skills`
- **Gradio**: 右側快速指令面板
- **Telegram**: `/skills` 指令

---

<a id="ch7"></a>
## Ch7: 模型切換教學

### 7.1 設定預設模型

編輯 `config/default.yaml`：

```yaml
models:
  default: "gemini-3-flash"
  fallback_chain:
    - "gemini-3-flash"
    - "llama-3.3-70b-versatile"
    - "gpt-5.4"
```

### 7.2 Fallback 機制

當主模型 API 呼叫失敗時，系統自動嘗試 fallback chain 中的下一個模型。

例如：gemini-3-flash 失敗 → 自動切換 llama-3.3-70b-versatile (Groq 免費)。

### 7.3 各介面切換方式

| 介面 | 方法 |
|------|------|
| Gradio GUI | 右側下拉選單選擇 |
| REST API | 請求 body 加 `"model": "gpt-5.4"` |
| Telegram | `/model gpt-5.4` |
| LINE Bot | 目前不支援切換（使用預設模型） |

### 7.4 模型選擇建議

| 場景 | 推薦模型 |
|------|---------|
| 一般對話 | gemini-3-flash |
| 深度推理 | gemini-3-pro 或 gpt-5.4-pro |
| 長文寫作 | claude-opus-4-6 |
| 免費使用 | llama-3.3-70b-versatile (Groq) |
| 最快回覆 | gemini-3-flash |

---

<a id="ch8"></a>
## Ch8: 部署到雲端

### 8.1 使用 ngrok（臨時方案）

適合本機開發與測試：

```bash
ngrok http 8000
```

取得公開網址後設定 LINE / Telegram webhook。

> 注意：ngrok 免費版每次啟動網址會變，需重新設定 webhook。

### 8.2 部署到 Render

1. 將專案推上 GitHub
2. 前往 https://render.com/ 建立帳號
3. New → Web Service → 連結 GitHub repo
4. 設定：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py --host 0.0.0.0 --port $PORT`
5. 在 Environment 加入所有 API 金鑰
6. Deploy

### 8.3 部署到 Railway

1. 前往 https://railway.app/
2. New Project → Deploy from GitHub repo
3. 設定環境變數（同 .env）
4. Railway 自動偵測 Python 並部署

### 8.4 部署到 Google Cloud Run

```bash
# 建立 Dockerfile
# 省略詳細步驟，參見 Google Cloud 文件

gcloud run deploy liangclaw \
  --source . \
  --region asia-east1 \
  --allow-unauthenticated
```

### 8.5 注意事項

- 確保雲端平台的環境變數已設定所有 API 金鑰
- LINE / Telegram webhook URL 需更新為雲端網址
- Render 免費方案會有冷啟動延遲（約 30 秒）
- 建議使用 Railway 或 Render 的 paid plan 用於正式環境

---

<a id="ch9"></a>
## Ch9: 常見問題 FAQ

### Q1: 啟動時顯示 "Missing packages"

```
[ERROR] Missing packages: gradio, uvicorn
```

**A**: 執行 `pip install -r requirements.txt` 安裝依賴。

### Q2: 啟動時顯示 "No API keys found"

```
[WARN] No API keys found in .env!
```

**A**: 確認 `.env` 檔案存在且至少填入一組 API 金鑰。

### Q3: 對話時顯示 "模型呼叫失敗"

**A**:
- 確認 API 金鑰有效
- 檢查網路連線
- 嘗試切換其他模型
- 查看終端機錯誤訊息

### Q4: LINE Bot 沒有回應

**A**:
- 確認 ngrok 正在運行
- 確認 Webhook URL 正確（含 `/line/webhook` 路徑）
- 確認 LINE Developers Console 中 Webhook 已啟用
- 查看 LiangClaw 終端機是否收到請求

### Q5: Telegram Bot 沒有回應

**A**:
- 確認 Webhook 已設定：`curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
- 確認 Bot Token 正確
- 查看 LiangClaw 終端機日誌

### Q6: Gradio 介面打不開

**A**:
- 確認 gradio 已安裝：`pip install gradio`
- 確認瀏覽器存取的是 `http://localhost:8000/chat`（注意 `/chat` 路徑）
- 查看終端機是否有 `[WARN] Gradio UI not loaded` 訊息

### Q7: 如何新增自己的技能？

**A**: 在 `~/.claude/skills/` 建立目錄，加入 `SKILL.md` 檔案，重啟 LiangClaw。詳見 Ch6。

### Q8: 如何只使用免費模型？

**A**: 在 `.env` 只填 `GROQ_API_KEY`，預設模型改為 `llama-3.3-70b-versatile`：

```yaml
# config/default.yaml
models:
  default: "llama-3.3-70b-versatile"
  fallback_chain:
    - "llama-3.3-70b-versatile"
```

### Q9: 如何更新 LiangClaw？

**A**: 重新複製最新檔案到專案目錄，保留你的 `.env` 設定。

### Q10: Session 資料存在哪裡？

**A**: `data/sessions/` 目錄下，每個使用者一個 JSON 檔案。可直接刪除清除對話記錄。

---

*LiangClaw v1.0.0 — 阿亮老師 AI Agent 平台*
