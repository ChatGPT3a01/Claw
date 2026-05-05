# 🦞 Claw v3.0

> **Claude × Codex × Gemini  ·  in-session delegation**
>
> 一鍵安裝，三家 AI 在同一個 Claude Code session 裡協作。
> 真 session、prompt cache 命中、不冷啟動、token 省 ~90%。

---

## 🎯 解決什麼問題？

如果你曾經被「同時用三家 AI CLI」搞煩過：
- 切視窗切到頭暈
- 對話歷史丟失
- 每次都從零冷啟動
- token 消耗很快爆表

**Claw v3** 改變遊戲規則 ─ 把 Codex 與 Gemini 變成 Claude Code 的「委派子任務」，全程留在主 session：

| 場景 | 舊做法 | Claw v3 做法 |
|---|---|---|
| 想讓 Codex 審查程式碼 | 切到 codex CLI、貼程式碼、問問題、再貼回來 | `/codex:review` |
| 想讓 Gemini 用 1M context 看整個專案 | 切到 gemini CLI、想辦法給檔案 | `/gemini:review` |
| 對抗式挑戰自己的設計 | 自己跟自己吵 | `/codex:adversarial-review` |
| 委派任務給較便宜的模型 | 開新視窗 | `/codex:rescue --background` |

---

## 🚀 一鍵安裝

### 前置條件

確認以下 CLI 都已安裝：

| CLI | 安裝指令 |
|---|---|
| Node.js 18+ | https://nodejs.org |
| Claude Code | `npm install -g @anthropic-ai/claude-code` |
| OpenAI Codex | `npm install -g @openai/codex` |
| Google Gemini | `npm install -g @google/gemini-cli` |

### 安裝 Claw

**方法 A ─ 從 GitHub 下載 install.ps1 直接跑（推薦）**

```powershell
iwr https://raw.githubusercontent.com/ChatGPT3a01/Claw/main/install.ps1 -OutFile install.ps1
.\install.ps1
```

**方法 B ─ Git clone**

```powershell
git clone https://github.com/ChatGPT3a01/Claw.git
cd Claw
.\install.ps1
```

`install.ps1` 會自動：
1. ✅ 檢查前置 CLI
2. ✅ 部署 `claw` 命令到 `~/.claude/claw/`
3. ✅ 透過 `claude plugin install` 安裝 Codex 與 Gemini plugin
4. ✅ 設定 PowerShell profile（PATH + `mcp-on/off/ls` alias）
5. ✅ 顯示下一步動作

### 首次認證（安裝後做一次）

關閉並重開 PowerShell，輸入 `claw` 進入 Claude Code 後執行：

```
/codex:setup
/gemini:setup
```

如果提示要登入：

```
!codex login                                  # Codex 登入
!gcloud auth application-default login        # Gemini 認證 (擇一)
$env:GOOGLE_API_KEY = "<key from AI Studio>"  # 或用 API key
```

---

## 📖 用法

### 啟動

```powershell
claw                  # 開啟 Claude Code（含花俏 banner、預設自動模式）
claw --no-banner      # 不顯示 banner
claw --about          # 看作者資訊
claw --setup-help     # 看 plugin 安裝指引
claw --safe           # 關閉自動模式（每件事都問你）
```

### 🌟 最簡單用法（推薦學員，0 學習成本）

進入 claude 後，**直接用中文跟它說想做什麼**：

```
你：請 Codex 審查我剛寫的程式碼
你：讓 Gemini 用 1M context 看整個專案
你：派 Codex 修這個 bug
```

→ Claude 聽得懂、會自動派工，**完全不用記指令**。

### 進階：在 Claude 對話內可用的指令

| 指令 | 說明 |
|---|---|
| `/codex:review` | Codex 程式碼審查 |
| `/codex:adversarial-review` | Codex 對抗式挑戰設計決策 |
| `/codex:rescue <task>` | 委派任務給 Codex（修 bug、追問題）|
| `/codex:status` `/codex:result` `/codex:cancel` | 管理 Codex 背景任務 |
| `/gemini:review` | Gemini 程式碼審查（1M context）|
| `/gemini:adversarial-review` | Gemini 對抗式挑戰 |
| `/gemini:rescue <task>` | 委派任務給 Gemini |
| `/gemini:status` `/gemini:result` `/gemini:cancel` | 管理 Gemini 背景任務 |

支援 `--background`、`--base <ref>`、`--model <name>` 等 flag。完整文件：
- Codex: https://github.com/openai/codex-plugin-cc
- Gemini: https://github.com/abiswas97/gemini-plugin-cc

### 🤖 自動模式（預設啟用）

三家 AI 都預設走自動模式，減少詢問、自主判斷處理：

| AI | 自動設定 | 等於 |
|---|---|---|
| **Claude** | `--dangerously-skip-permissions` + `CLAUDE_CODE_NO_FLICKER=1` | 跳過所有權限詢問 |
| **Codex** | `~/.codex/config.toml` 寫入 `approval_policy="on-request"` `sandbox_mode="workspace-write"` | 相當於 `codex --full-auto` |
| **Gemini** | `~/.gemini/settings.json` 寫入 `approvalMode="auto_edit"` | 自動允許編輯類工具 |

不喜歡可以用 `claw --safe` 啟動，或手動編輯上述 config 檔案。

### MCP 按需切換（包在裡面送）

避免一次載太多 MCP 工具拖慢啟動：

```powershell
mcp-ls                        # 看目前啟用的 MCP
mcp-on twstockmcpserver       # 載入備援 MCP
mcp-off twstockmcpserver      # 卸下
mcp-off all                   # 一次卸下全部
```

把 MCP server 設定 JSON 存成 `<名稱>.json` 放進 `~/.claude/mcp-presets/` 即可。

---

## 🔧 解除安裝

```powershell
& "$env:USERPROFILE\.claude\claw\uninstall.ps1"
```

可選 flag：
- `-KeepPlugins`：保留 Codex / Gemini plugin
- `-KeepProfile`：保留 PowerShell profile 設定

---

## 🏗️ 架構

```
你輸入 claw
     ↓
PowerShell launcher 顯示 banner
     ↓
進入 Claude Code 主 session（cache 命中、有對話記憶）
     ↓
     ├─ /codex:*   → 透過 codex-plugin-cc 委派 OpenAI Codex
     │              （Codex app server 常駐，不冷啟動）
     │
     └─ /gemini:*  → 透過 gemini-plugin-cc 委派 Google Gemini
                    （ACP 持續會話，不冷啟動）
```

**為什麼不是 wrapper？**
舊版 Claw v2 是包在 Claude/Codex/Gemini CLI 外面的 Python 程式，每次發訊都重啟子進程 → 失去 prompt cache、context 歷史每次重送。
v3 改成 Claude Code plugin 模型：主 session 不動，子任務透過 plugin 委派。

---

## 👨‍🏫 關於作者

<div align="center">

### 曾慶良 主任（阿亮老師）

<table>
<tr>
<td width="50%">

**📌 現任職務**

🎓 新興科技推廣中心主任<br>
🎓 教育部學科中心研究教師<br>
🎓 臺北市資訊教育輔導員

</td>
<td width="50%">

**🏆 獲獎紀錄**

🥇 2025 SETEAM 教學專業講師認證<br>
🥇 2024 教育部人工智慧講師認證<br>
🥇 2022、2023 指導學生 XR 專題競賽特優<br>
🥇 2022 VR 教材開發教師組特優<br>
🥇 2019 百大資訊人才獎<br>
🥇 2018、2019 親子天下創新 100 教師<br>
🥇 2018 臺北市特殊優良教師<br>
🥇 2017 教育部行動學習優等

</td>
</tr>
</table>

### 📞 聯絡方式

[![YouTube](https://img.shields.io/badge/YouTube-@Liang--yt02-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/@Liang-yt02)
[![Facebook](https://img.shields.io/badge/Facebook-3A科技研究社-blue?style=for-the-badge&logo=facebook)](https://www.facebook.com/groups/2754139931432955)
[![Email](https://img.shields.io/badge/Email-3a01chatgpt@gmail.com-green?style=for-the-badge&logo=gmail)](mailto:3a01chatgpt@gmail.com)

</div>

---

## 📜 授權聲明

**© 2026 阿亮老師 版權所有**

本專案僅供「阿亮老師課程學員」學習使用。

### ⚠️ 禁止事項

- ❌ 禁止修改本專案內容
- ❌ 禁止轉傳或散布
- ❌ 禁止商業使用
- ❌ 禁止未經授權之任何形式使用

如有任何授權需求，請聯繫作者。

---

<div align="center">

## 🌟 喜歡這個專案嗎？

如果這個工具對你有幫助，請給我們一個 ⭐ Star！

<br>

**Made with ❤️ by 阿亮老師**

<br>

[⬆️ 回到頂部](#-claw-v30)

---

© 2026 阿亮老師 版權所有

</div>
