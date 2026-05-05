# Claw 對話記憶 / 開發脈絡紀錄

> 記錄每次重大改造的「為什麼這樣設計」「踩過什麼坑」「決策依據」。
> 這份檔案不是 changelog（changelog 給使用者看），而是給未來自己／協作者讀的設計脈絡。

---

## 2026-05-05 — Claw v2.0 誕生（從 LiangClaw 重生）

### 起點：使用者的需求

使用者在閱讀 `openai/codex-plugin-cc` 後，提出整合構想：

> 「把 codex-plugin-cc 的機制 + 自架 GeminiCLI 教學整合到 LiangClaw 中，
>  多一個 `/gld` 指令（Gemini 自動執行），有點像 `/cld`。
>  最開始進去時不要打 liang 也不要顯示 liang，改為 claw。
>  進去時除了 /cld 等等的指令，也秀一下其他的重要指令。」

### 關鍵決策過程

**Q1：自架 GeminiCLI 是什麼？**
最初我以為要自己重寫 Gemini CLI，但使用者糾正：「Google 本來就有 Gemini CLI」。
→ 改為 wrapper `@google/gemini-cli`（Google 官方開源）。
→ 同理：`/cld` 包 `@anthropic-ai/claude-code`、`/cod` 包 `@openai/codex`。

**Q2：方向 A / B / C？**
- A：terminal REPL（仿 Claude Code 體驗）
- B：Gradio Web UI 加 slash 路由
- C：兩者都做
→ 使用者選 **C**。

**Q3：CH18 改名 / CH23 LiangClaw 處理？**
- CH18：徹底改名為 `CH18_Claw三AI切換器`
- CH23：保留 LiangClaw 字樣，僅標註為「Claw 多模型平台前身」
→ 使用者授權「直接處理」，採 A1+C2。

### 三 AI 角色分工（仿 codex-plugin-cc 精神）

```
Claude Code（主環境，永遠的起點）
       ↓ 安裝 Claw
       ├─ /cld → 直接用 Claude
       ├─ /gld → 把任務丟給 Gemini，回報結果
       └─ /cod → 把任務丟給 Codex，回報結果
```

「主環境 + 副手」模型：主環境永遠在 Claude Code（或 Claw REPL），
其他 AI 是被叫進來做特定工作（審查、委派、跑大 context、出第二意見）的副手。

### 踩過的坑（給未來自己）

1. **Windows subprocess 找不到 .CMD shim**
   `subprocess.run(["gemini", ...])` 失敗。修法：用 `shutil.which()` 拿完整路徑。
   見 `src/core/cli_router.py::_build_cmd`。

2. **Codex 拒絕在非 git 目錄執行**
   報 `Not inside a trusted directory`。修法：每個 codex subcommand 都加 `--skip-git-repo-check`。
   注意旗標位置在 subcommand 之後（`codex review --skip-git-repo-check`），不是全域旗標。

3. **claw.bat 中文註解被 cmd.exe 誤判為指令**
   `'��這個資料夾加進' is not recognized as ...` — cp950 解讀錯。
   修法：移除中文 REM + `chcp 65001` + `PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1`。

4. **Rich `dim` 樣式在亮色終端看不見**
   使用者截圖反映文字對比度太低。修法：
   - `dim` → `bold default`（用終端預設色加粗）
   - 樹狀符號 → `bright_blue`
   - 規則：避免任何「灰階偏淺」的樣式。

5. **沒有預設主引擎，每次都要打 /cld 才能說話**
   UX 痛點。修法：`DEFAULT_ENGINE = "cld"`，純文字自動加前綴；
   `/use cld|gld|cod` 切換；提示符顯示當前主引擎並換顏色（`claw·cld>` 青色）。

6. **build_student_zip.py 把舊 zip 也打進去（俄羅斯娃娃）**
   修法：每次重打前先 `rm -f Claw_v*_學員版_*.zip`；`.gitignore` 也排除。

### 設計原則（給未來改 Claw 的人）

- **不重做 LLM**：三家官方 CLI 都是現成的，Claw 只是 subprocess wrapper + 統一 REPL。
  禁止把 LLM 邏輯（API 直呼、token 算費）寫進 Claw 本體。
- **slash command 是唯一的路由方式**：不要再加 magic word 或 NLP 路由。
  使用者打 `/cld /gld /cod` 是最清晰的意圖表達。
- **背景任務存在 `.claw/jobs/<job_id>.json`**：runtime 紀錄，不進 git。
  job_id 格式 `<engine>-<8 char hex>`。stdout/stderr 寫到同名 .stdout/.stderr 旁邊檔。
- **預設不假設 API Key 模式**：使用者可以用各 CLI 自己的登入（`claude login`/
  `gemini` 互動引導 / `codex login`），也可以用 `.env`。Claw 不強迫。

### 本次改造的檔案清單

新增：
- `claw.py`（REPL 入口，含 Banner + 樹狀架構 + /use 主引擎切換）
- `claw.bat` / `claw.ps1`（Windows 啟動器，UTF-8 強制）
- `install_global.bat` / `install_global.ps1`（一鍵全域 PATH 安裝）
- `src/core/cli_router.py`（三 AI subprocess wrapper，含 parse_slash / dispatch）
- `build_student_zip.py`（學員包打包腳本）
- `docs/CONVERSATION_LOG.md`（這份檔案）

改寫：
- `interfaces/gradio_ui.py`（slash 指令解析 + 架構面板）
- `interfaces/app.py`（標題改 Claw API）
- `run.py`（啟動 Banner 改三 AI 切換器版本）
- `README.md`（從 LiangClaw 改寫成 Claw v2.0 完整版）
- `.gitignore`（補強：排除 .claw/jobs、學員 zip、pytest cache）

聖經書配套（外部）：
- 書籍 CH18 主檔重寫成 Claw 三 AI 版本
- CH18 資料夾改名為 `CH18_Claw三AI切換器`
- 簡報 Part5 全文批次替換 liang → Claw / Liang → Claw
- 教師手冊 + 實作手冊 build.py 重 build
- 附錄 A 新增「Part 5：Claw 三 AI CLI 切換器」區塊
- 書籍章節規劃 / 序言對應更新
- CH23 LiangClaw 標註為「Claw 多模型平台前身」

### 上 GitHub

- 帳號：`ChatGPT3a01`
- Repo：<https://github.com/ChatGPT3a01/Claw>
- 第一次 commit 涵蓋 1024 個檔案
- 學員安裝改為 `git clone https://github.com/ChatGPT3a01/Claw.git` 主路線，
  zip 解壓作為「離線教室」備援。

### 待辦（如果未來要做）

- [ ] 把 Claw 也做成 Claude Code Plugin（讓使用者在 Claude Code 內就能 `/cld /gld /cod`）
- [ ] 第六篇 Part6_第六篇_CH22-25.html 還有零星 LiangClaw 字樣可考慮加註
- [ ] CH23 多模型平台主檔也許可加一段「現在已升級為 Claw v2.0」的 banner
- [ ] 加 GitHub Actions：自動測試 + 自動打包學員 zip 為 release

---

## 模板（未來新事件複製這段）

```
## YYYY-MM-DD — 事件標題

### 起點
（使用者的需求 / 觸發點）

### 關鍵決策
（為什麼這樣選，不是那樣選）

### 踩過的坑
（給未來的自己留路標）

### 改動的檔案
（哪些新增、哪些改寫）
```
