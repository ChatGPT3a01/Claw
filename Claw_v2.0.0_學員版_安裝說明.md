# 🦞 Claw v2.0 — 三 AI CLI 切換器（學員安裝指南）

> Claude · Gemini · Codex 一鍵切換  
> Terminal REPL + Web UI 雙模式  
> 阿亮老師 Claude Code 聖經配套

---

## 一、系統需求

| 項目 | 版本 | 備註 |
|------|------|------|
| Python | 3.11+ | [官網下載](https://www.python.org/downloads/) |
| Node.js | 18+ | [官網下載](https://nodejs.org/)（用來裝三家官方 CLI） |
| 作業系統 | Windows 10/11、macOS、Linux | 主要在 Windows 11 測試 |

---

## 二、安裝步驟（5 分鐘搞定）

### 1. 解壓縮

把 `Claw_v2.0.0_學員版_xxxxxxxx.zip` 解壓到你習慣的工作目錄，例如：
```
D:\我的AI工具\Claw_v2.0\
```

### 2. 安裝 Python 套件

開啟 PowerShell（或 cmd），切換到解壓後的資料夾：
```powershell
cd D:\我的AI工具\Claw_v2.0
pip install -r requirements.txt
```

### 3. 安裝三家官方 AI CLI

**這三家 CLI 是 Claw 路由的目標**，至少裝一家才能用：

```powershell
# Anthropic Claude Code（/cld 用）
npm install -g @anthropic-ai/claude-code

# Google Gemini CLI（/gld 用，免費 60 req/min）
npm install -g @google/gemini-cli

# OpenAI Codex CLI（/cod 用）
npm install -g @openai/codex
```

### 4. 設定 API Key

複製範本：
```powershell
copy .env.example .env
notepad .env
```

至少填一個 API key 進去。或者用各 CLI 自己的登入方式（推薦）：
```powershell
claude login    # ChatGPT 帳號或 Anthropic API key
gemini          # 第一次執行會引導 Google 登入
codex login     # ChatGPT 訂閱或 OpenAI API key
```

---

## 三、開始使用

### 方式 A：Terminal REPL（推薦）

```powershell
.\claw.bat
```

進入後會看到：

```
🦞 Claw — 三 AI CLI 切換器 v2.0.0

Claude Code（主環境，永遠的起點）
       ↓ 安裝 Claw plugin
       ├─ /cld <prompt>   → 直接用 Claude 處理
       ├─ /gld <prompt>   → 把任務丟給 Gemini CLI
       ├─ /cod <prompt>   → 把任務丟給 Codex CLI
       │
       └─ /cod:review     → Codex 審查
          /cod:rescue     → Codex 委派
          /gld:review     → Gemini 審查（新增）
          /gld:rescue     → Gemini 委派（新增）
```

直接打（**預設主引擎是 CLD**）：
```
claw·cld> 你好，請用一句話介紹你自己       ← 直接打字 → 走主引擎（cld）
claw·cld> /use gld                           ← 切換主引擎為 Gemini
claw·gld> 你好                               ← 現在走 gld
claw·gld> /cod 寫個 Python 排序              ← 一次性指定 cod，主引擎不變
claw·gld> /cod:review --base main            ← 進階指令仍可隨時呼叫
```

提示符會顯示當前主引擎（`claw·cld` / `claw·gld` / `claw·cod`），顏色也會跟著變。

### 方式 B：Web UI（瀏覽器）

```powershell
python run.py
```

開瀏覽器到 [http://localhost:8000/chat](http://localhost:8000/chat)，輸入框直接打 slash 指令。

---

## 四、指令速查

> 💡 **預設主引擎：CLD（Claude）**。直接打文字（不帶 `/`）會自動送主引擎。  
> 想換主引擎打 `/use gld` 或 `/use cod`，想一次性指定就用 `/cld /gld /cod`。

| 指令 | 引擎 | 說明 |
|------|------|------|
| （直接打字） | 主引擎 | 自動送目前主引擎（預設 cld） |
| `/use cld\|gld\|cod` | — | 切換主引擎 |
| `/cld <prompt>` | Claude Code | 預設 sonnet-4-6，加 `--pro` 用 opus-4-7 |
| `/gld <prompt>` | Gemini CLI | 預設 3-flash，加 `--pro` 用 3.1-pro |
| `/cod <prompt>` | Codex CLI | 預設 gpt-5.4，加 `--pro` 用 gpt-5.4-pro |
| `/cod:review [--base main]` | Codex | 程式碼審查（可加 `--background` 背景跑） |
| `/cod:adversarial-review` | Codex | 對抗式審查，挑戰設計決策 |
| `/cod:rescue <task>` | Codex | 委派任務修 bug |
| `/gld:review` | Gemini | Gemini 1M context 看全專案 |
| `/gld:rescue <task>` | Gemini | 委派任務給 Gemini |
| `/<eng>:status` | 任一 | 查背景任務（eng = cld/gld/cod） |
| `/<eng>:result` | 任一 | 取得任務結果 |
| `/<eng>:cancel` | 任一 | 取消背景任務 |
| `/help` | — | 完整指令說明 |
| `/skills` | — | 列出 80+ 內建技能 |
| `/web` | — | 在瀏覽器開啟 Web UI |
| `/quit` | — | 離開 |

---

## 五、進階：把 `claw` 設為全域指令

要讓 `claw` 在「**任何資料夾**」都能直接執行（不限於解壓目錄），有兩種做法：

### 推薦：跑一鍵安裝腳本（不需管理員權限）

```powershell
# PowerShell（推薦）
.\install_global.ps1

# 或 CMD
install_global.bat
```

執行後會把 Claw 資料夾加進**使用者 PATH**，永久生效。**關掉視窗、開新的終端機**，在任何資料夾打：

```powershell
claw
```

就能進入 REPL。

### 手動法（如果腳本被擋）

1. 按 `Win + R` → 輸入 `sysdm.cpl` → 進階 → 環境變數
2. 在「使用者變數」編輯 `Path`，新增 Claw 解壓目錄（如 `D:\我的AI工具\Claw_v2.0`）
3. 重開 PowerShell / CMD，打 `claw` 試試

---

## 六、常見問題

**Q：`Unknown command: /cld`？**  
A：你應該在 Claw 裡（打 `claw.bat` 進入），不是在 Claude Code 裡。Claude Code 不認識 `/cld`，那是 Claw 的指令。

**Q：`gemini`/`claude`/`codex` 找不到？**  
A：第二步沒做完。確認 `npm install -g` 三行都跑過，並且 npm 全域目錄有加 PATH（通常 nvm 會自動處理）。

**Q：Gemini 回 429 錯誤？**  
A：免費版有限制（60 req/min, 1000 req/day）。等一下再試，或登入付費帳號。

**Q：要不要每家都裝？**  
A：不用。只裝你會用的就好，Claw 啟動時會偵測哪些 CLI 可用。

---

## 七、回報問題

阿亮老師：iddmail@ycsh.tp.edu.tw

---

🦞 **Happy Switching!**
