# 🦞 Claw — 三 AI CLI 切換器

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Node 18+](https://img.shields.io/badge/Node-18%2B-339933.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Gradio](https://img.shields.io/badge/Gradio-5.0%2B-orange.svg)](https://gradio.app/)
[![Rich](https://img.shields.io/badge/Rich-CLI-purple.svg)](https://rich.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Claude · Gemini · Codex 一鍵切換**
> 把三家官方 AI CLI 收進同一個 REPL，靠 `/cld` `/gld` `/cod` 統一指揮 — 不用再切換終端視窗。
> 仿 [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) 機制，再加上 Gemini 線。

---

## ✨ 核心能力

```
Claude Code（主環境，永遠的起點）
       ↓ 安裝 Claw
       ├─ /cld <prompt>   → 直接用 Claude 處理（其實就是 Claude Code 自己）
       ├─ /gld <prompt>   → 把任務丟給 Gemini CLI，回報結果
       ├─ /cod <prompt>   → 把任務丟給 Codex CLI，回報結果
       │
       └─ /cod:review     → Codex 審查（仿 codex-plugin-cc）
          /cod:rescue     → Codex 委派
          /gld:review     → Gemini 審查（新增）
          /gld:rescue     → Gemini 委派（新增）
```

| 引擎 | 預設模型 | `--pro` 模型 | 強項 |
|------|---------|------------|------|
| **Claude** | claude-sonnet-4-6 | claude-opus-4-7 | 主導決策、agentic、長 context |
| **Gemini** | gemini-3-flash-preview | gemini-3.1-pro-preview | 1M token 看全專案、免費 60 req/min |
| **Codex** | gpt-5.4 | gpt-5.4-pro | OpenAI 視角、對抗式審查 |

---

## 🚀 黃金三步（學員安裝）

```bash
# 1. 取得程式碼
git clone https://github.com/ChatGPT3a01/Claw.git
cd Claw

# 2. 安裝依賴 + 全域指令（一次永久生效）
pip install -r requirements.txt
.\install_global.ps1                # PowerShell（推薦）
# 或 install_global.bat              # CMD

# 3. 關掉視窗、開新 PowerShell（任何資料夾都行）
claw
```

進去就看到三 AI 架構樹狀圖、指令面板、CLI 安裝偵測。

---

## 📦 系統需求 + 三家官方 CLI

| 項目 | 版本 | 安裝 |
|------|------|------|
| Python | 3.11+ | <https://www.python.org/downloads/> |
| Node.js | 18.18+ | <https://nodejs.org/> |
| Claude Code CLI | latest | `npm install -g @anthropic-ai/claude-code` |
| Gemini CLI | latest | `npm install -g @google/gemini-cli` |
| Codex CLI | latest | `npm install -g @openai/codex` |

> 💡 三家 CLI 至少裝一家就能用 Claw，三家都裝才能體驗完整切換。
> 各家登入：`claude login` / `gemini`（首次互動引導）/ `codex login`。

---

## 🎮 互動體驗

進 REPL 後，**預設主引擎是 `cld`**，提示符會顯示當前主引擎並換顏色：

```
claw·cld> 你好                       ← 直接打字 → 走主引擎 cld（青色）
claw·cld> /use gld                    ← 切主引擎為 Gemini
claw·gld> 你好                        ← 改走 gld（綠色）
claw·gld> /cod 寫個 Python 排序       ← 一次性指定 cod，主引擎不變
claw·gld> /cod:review --base main     ← Codex 程式碼審查
claw·gld> /gld:review                 ← Gemini 1M context 看全專案
claw·gld> /cod:status                 ← 查看背景任務
claw·gld> /help                       ← 完整指令面板
claw·gld> /quit                       ← 離開
```

### 完整指令一覽

| 指令 | 說明 |
|------|------|
| `/cld <prompt>` | Claude Code |
| `/gld <prompt>` | Gemini CLI |
| `/cod <prompt>` | Codex CLI |
| `/use cld\|gld\|cod` | 切換主引擎（之後直接打字就送主引擎） |
| `/cod:review [--base main]` | Codex 程式碼審查（可加 `--background`） |
| `/cod:adversarial-review` | 對抗式審查，挑戰設計決策 |
| `/cod:rescue <task>` | 委派任務給 Codex 修 bug |
| `/gld:review [--base main]` | Gemini 審查（1M context 看全專案） |
| `/gld:rescue <task>` | 委派任務給 Gemini |
| `/<eng>:status [job_id]` | 查看背景任務（eng = cld/gld/cod） |
| `/<eng>:result [job_id]` | 取得已完成任務結果 |
| `/<eng>:cancel [job_id]` | 取消背景任務 |
| `/health` | 重新偵測三家 CLI 安裝狀態 |
| `/skills` | 列出 80+ 內建技能 |
| `/web` | 開啟 Gradio Web UI |
| `/quit` | 離開 |

### 共用旗標

| 旗標 | 說明 |
|------|------|
| `--pro` | 切到該家「最強」模型 |
| `--mini` | 切到「迷你/便宜」模型（目前僅 cod 支援 gpt-5.4-mini） |
| `--background` / `--bg` | 任務丟背景跑，不卡 REPL |
| `--base <ref>` | review 子指令限定：比對基準分支 |
| `--model <name>` | 直接指定模型名稱（覆寫上面三檔） |
| `--effort low/medium/high` | rescue 子指令限定：推理力度 |
| `--resume` / `--fresh` | rescue 子指令限定：續用上次 / 重新開始 |

---

## 🌐 Web UI 模式

```powershell
python run.py
```

開瀏覽器到 <http://localhost:8000/chat>，輸入框直接打 slash 指令（與 REPL 同一套）。

UI 額外提供：
- 「📖 完整指令說明」折疊面板
- 「🩺 引擎安裝檢查」即時偵測
- 一般訊息（不帶 `/`）走原本 `/api/chat`（model_router 自動選 provider）

---

## 🔄 學員端更新方式

```bash
cd D:\我的AI工具\Claw
git pull
```

不需要重發 zip，永遠拿最新版。

---

## 🧰 一個工作日的三 AI 用法

| 時段 | 任務 | 用哪個 | 為什麼 |
|------|------|--------|--------|
| 早上 | 設計新功能架構 | `/cld --pro` | Claude opus 深度規劃 |
| 上午 | 寫骨架程式碼 | Claude Code 主環境直接寫 | 不離開主環境 |
| 中午 | 整個專案級的 review | `/gld:review` | Gemini 1M context 免費 |
| 下午 | 對抗式設計審查 | `/cod:adversarial-review` | Codex 用不同視角挑戰 |
| 傍晚 | 修 CI 上的 flaky test | `/cod:rescue --background` | 丟背景跑，邊做別的 |
| 收工前 | 生成 PR 描述 | `/gld 一段繁體中文 PR 描述` | flash 快又免費 |

---

## 📁 專案結構

```
Claw/
├── claw.py                  # terminal REPL 入口
├── claw.bat / claw.ps1      # Windows 啟動器
├── install_global.bat/ps1   # 一鍵全域 PATH 安裝
├── run.py                   # Web UI 啟動腳本（FastAPI + Gradio）
├── build_student_zip.py     # 學員包打包腳本
├── src/
│   ├── core/
│   │   ├── cli_router.py    # 三 AI subprocess wrapper（核心）
│   │   ├── agent.py         # 多模型 Agent
│   │   ├── model_router.py  # 一般訊息的模型路由
│   │   └── providers/       # 各家 API provider 封裝
│   ├── claw/                # Claude Code 鏡像層（指令快照、權限、session）
│   ├── skills/              # 技能載入器
│   └── tools/               # 工具實作（Read / Write / Bash / Glob / Grep ...）
├── interfaces/
│   ├── app.py               # FastAPI 主應用
│   ├── gradio_ui.py         # Web UI（含 slash 指令解析）
│   ├── line_bot.py          # LINE Bot Webhook
│   └── telegram_bot.py      # Telegram Bot Webhook
├── skills/bundled/          # 80+ 內建教育技能
├── config/                  # 預設設定（personas / models）
└── tests/                   # pytest 測試
```

---

## 🦐 Claw 與 codex-plugin-cc 的差異

| 面向 | codex-plugin-cc | **Claw** |
|------|-----------------|---------|
| 引擎數量 | 2（Claude + Codex） | **3**（+ Gemini） |
| 安裝形式 | Claude Code Plugin | 獨立 terminal REPL + Web UI |
| Gemini review | ✗ | ✅（`/gld:review` 1M context） |
| Web UI | ✗ | ✅（Gradio） |
| 多介面 | terminal | terminal + Web + LINE + Telegram |
| 內建技能 | ✗ | ✅ 80+ 教育用技能庫 |

---

## 📚 教學書配套

本專案是「**Claude Code 聖經：從入門到實戰全攻略**」**第五篇 CH18** 的實作配套。
書中以這個專案為案例，逐步教學從 0 到 1 建立三 AI CLI 切換器。

- 書籍主檔：`第五篇/CH18_Claw三AI切換器/CH18_Claw三AI切換器.md`
- 簡報：`簡報/Part5_第五篇_CH18-21.html`
- 教師手冊 / 實作手冊：`簡報/teacher-manual/` 與 `簡報/practice-manual/`

---

## 👨‍🏫 作者

**曾慶良（阿亮老師）**
- 新興科技推廣中心主任
- 教育部人工智慧講師認證
- Email：iddmail@ycsh.tp.edu.tw

---

## 📜 License

MIT License — 自由用、自由改、商用都行。

---

## 🆘 常見問題

**Q：`Unknown command: /cld`？**
A：你應該在 Claw 裡（打 `claw` 進入），不是在 Claude Code 裡。Claude Code 不認識 `/cld`。

**Q：`gemini` / `claude` / `codex` 找不到？**
A：三家 CLI 沒裝完。回頭做「系統需求」那一節的 `npm install -g`。

**Q：`/cod` 報 `Not inside a trusted directory`？**
A：Claw 已經自動加了 `--skip-git-repo-check`，請更新到最新版（`git pull`）。

**Q：Gemini 回 429 錯誤？**
A：免費版有限制（60 req/min, 1000 req/day）。等一下再試，或登入付費帳號。

**Q：要不要每家都裝？**
A：不用。只裝你會用的就好，Claw 啟動時會偵測哪些 CLI 可用。

---

🦞 **Happy Switching!** — 把對的問題丟給對的 AI，比硬要一個 AI 全包更省錢、更高品質。
