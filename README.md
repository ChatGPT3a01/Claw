# 🦞 LiangClaw — 阿亮老師 AI Agent 平台

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Gradio](https://img.shields.io/badge/Gradio-5.0%2B-orange.svg)](https://gradio.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **多模型 × 多介面 × 80+ 教育技能** — 專為教育工作者打造的 AI Agent 平台

---

## ✨ 功能特色

| 功能 | 說明 |
|------|------|
| 🤖 **多模型切換** | Gemini 3、GPT-5.4、Groq (免費)、Claude 4.6 一鍵切換 |
| 🎓 **80+ 教育技能** | 教案設計、素養評量、學習分析、偏鄉教育、研究方法… |
| 🖥️ **Gradio GUI** | 瀏覽器聊天介面，支援串流輸出、模型選擇、技能面板 |
| 📱 **LINE Bot** | 直接在 LINE 群組中對話 |
| ✈️ **Telegram Bot** | `/start`、`/skills`、`/model` 指令 |
| 🔄 **自動 Fallback** | 模型不可用時自動切換下一個 |
| 💾 **Session 管理** | 每位使用者獨立對話歷史 |
| 🧩 **claw-code 引擎** | 內建 prompt 路由與工具匹配 |

---

## 🏗️ 架構

```
┌─────────────────────────────────────────────┐
│               使用者介面層                    │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ Gradio  │ │ LINE Bot │ │ Telegram Bot │  │
│  │  /chat  │ │ /line/   │ │ /telegram/   │  │
│  └────┬────┘ └────┬─────┘ └──────┬───────┘  │
│       └───────────┼──────────────┘           │
│                   ▼                          │
│        ┌──────────────────┐                  │
│        │   FastAPI 主應用  │  REST API        │
│        │   /api/chat      │  /api/skills     │
│        └────────┬─────────┘  /health         │
├─────────────────┼───────────────────────────┤
│                 ▼                            │
│        ┌──────────────────┐                  │
│        │  LiangClawAgent  │  核心協調        │
│        └──┬─────┬─────┬───┘                  │
│           │     │     │                      │
│     ┌─────▼─┐ ┌─▼───┐ ┌▼──────────┐         │
│     │ Model │ │Skill│ │ Session   │         │
│     │Router │ │Reg. │ │ Manager   │         │
│     └──┬────┘ └──┬──┘ └───────────┘         │
│        │         │                           │
│  ┌─────▼──────┐  │  ┌────────────┐           │
│  │ Providers  │  └──│ claw-code  │           │
│  │ Gemini/GPT │     │ PortRuntime│           │
│  │ Groq/Claude│     └────────────┘           │
│  └────────────┘                              │
└─────────────────────────────────────────────┘
```

---

## 🚀 快速開始

### 1. 環境需求

- **Python 3.11+**
- **pip** 套件管理器
- 至少一組 AI API 金鑰

### 2. 安裝

```bash
# 複製專案
cd D:/AI教學與專案實作/專案_Claude_Code/LiangClaw

# 安裝依賴
pip install -r requirements.txt

# 設定 API 金鑰
cp .env.example .env
# 編輯 .env 填入你的金鑰
```

### 3. 設定 API 金鑰

編輯 `.env` 檔案，至少填入一組：

```env
# Google Gemini (推薦 — 免費額度最多)
GEMINI_API_KEY=your_key_here

# OpenAI
OPENAI_API_KEY=your_key_here

# Groq (免費！)
GROQ_API_KEY=your_key_here

# Anthropic
ANTHROPIC_API_KEY=your_key_here
```

### 4. 啟動

```bash
python run.py
```

啟動後：

| 服務 | 網址 |
|------|------|
| Gradio 聊天 | http://localhost:8000/chat |
| API 文件 | http://localhost:8000/docs |
| 健康檢查 | http://localhost:8000/health |

---

## 📡 API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| `POST` | `/api/chat` | 發送訊息 |
| `GET` | `/api/skills` | 列出所有技能 |
| `GET` | `/api/models` | 列出所有模型 |
| `GET` | `/health` | 健康檢查 |
| `POST` | `/line/webhook` | LINE Bot webhook |
| `POST` | `/telegram/webhook` | Telegram Bot webhook |

### 對話範例

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "幫我設計一堂適合偏鄉國小的數學教案",
    "model": "gemini-3-flash"
  }'
```

回應：

```json
{
  "content": "# 偏鄉國小數學教案...",
  "model_used": "gemini-3-flash",
  "session_id": "abc123",
  "usage": {"input_tokens": 150, "output_tokens": 800},
  "skill_used": "lesson-plan-generator"
}
```

---

## 🤖 支援模型

| 模型 | Provider | 說明 |
|------|----------|------|
| `gemini-3-flash` | Google | 快速、免費額度多 ⭐ 預設 |
| `gemini-3-pro` | Google | 最強推理 |
| `gpt-5.4` | OpenAI | 2026 最新 |
| `gpt-5.4-pro` | OpenAI | 最強版本 |
| `llama-3.3-70b-versatile` | Groq | 完全免費 🆓 |
| `qwen-3-32b` | Groq | 免費替代 |
| `claude-opus-4-6` | Anthropic | 最強長文 |
| `claude-sonnet-4-6` | Anthropic | 快速實用 |

---

## 📱 Bot 設定

### LINE Bot

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立 Messaging API Channel
3. 取得 Channel Access Token 和 Channel Secret
4. 設定 Webhook URL: `https://your-domain/line/webhook`
5. 填入 `.env`

### Telegram Bot

1. 與 [@BotFather](https://t.me/BotFather) 對話，建立 Bot
2. 取得 Bot Token
3. 設定 Webhook: `https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-domain/telegram/webhook`
4. 填入 `.env`

---

## 🎓 教育技能

LiangClaw 自動載入 `~/.claude/skills/` 下所有含 `SKILL.md` 的技能。

常用技能分類：

- **教學設計**: 教案產生、PBL、遊戲化學習、SEL 活動
- **學習分析**: 素養評量、同儕互評、學生輪廓
- **研究方法**: 準實驗設計、混合研究、實證自動化
- **偏鄉教育**: 在地化教材、偏鄉平台設計
- **AI 工具**: AI 融入教學、生成式 AI 應用
- **ICT 融入**: 資訊科技融入各科教學

---

## 🧪 測試

```bash
# 執行所有測試
python -m pytest tests/ -v

# 單一模組
python -m pytest tests/test_agent.py -v
python -m pytest tests/test_model_router.py -v
python -m pytest tests/test_skill_loader.py -v
python -m pytest tests/test_interfaces.py -v
```

---

## 📁 專案結構

```
LiangClaw/
├── run.py                  # 一鍵啟動
├── requirements.txt        # Python 依賴
├── .env.example            # API 金鑰範本
├── config/
│   ├── default.yaml        # 全域設定
│   ├── models.yaml         # 模型清單
│   └── personas/
│       └── aliang.yaml     # 阿亮老師人設
├── src/
│   ├── core/
│   │   ├── agent.py        # LiangClawAgent 主類別
│   │   ├── model_router.py # 多模型路由 + fallback
│   │   ├── session_manager.py
│   │   └── providers/      # Gemini / OpenAI / Groq / Claude
│   ├── claw/               # claw-code 引擎 fork
│   ├── skills/             # 技能載入系統
│   └── utils/              # 設定、日誌
├── interfaces/
│   ├── app.py              # FastAPI 主應用
│   ├── gradio_ui.py        # Gradio 聊天 UI
│   ├── line_bot.py         # LINE Bot
│   ├── telegram_bot.py     # Telegram Bot
│   └── message_adapter.py  # 統一訊息格式
├── skills/bundled/         # 精選教育技能
├── docs/
│   ├── teaching-guide.md   # 完整教學手冊
│   └── generate_pdf.py     # MD → PDF 產生器
└── tests/                  # 單元測試
```

---

## 📄 授權

MIT License

---

## 👨‍🏫 作者

**阿亮老師（曾慶良）**

- 教育部數位學習推動辦公室
- 專長：AI 融入教學、偏鄉教育、學習分析
