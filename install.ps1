# =====================================================================
#   Claw v3.0  ─  一鍵安裝程式（自包含）
#   Claude × Codex × Gemini  ·  in-session delegation
#
#   by 阿亮老師（曾慶良 主任）
#      新興科技推廣中心主任 · 教育部學科中心研究教師
#      YouTube: @Liang-yt02  ·  Email: 3a01chatgpt@gmail.com
#
#   用法:
#     .\install.ps1                  # 標準安裝
#     .\install.ps1 -SkipPlugins     # 不自動裝 plugin (除錯用)
#     .\install.ps1 -Force           # 強制覆蓋既有檔
#     .\install.ps1 -InstallDir <p>  # 自訂安裝位置
# =====================================================================

[CmdletBinding()]
param(
  [string]$InstallDir = "$env:USERPROFILE\.claude\claw",
  [switch]$SkipPlugins,
  [switch]$SkipAuth,
  [switch]$Force
)

$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING  = 'utf-8'

function Section($t) { Write-Host ""; Write-Host "━━━ $t " -NoNewline -ForegroundColor Cyan; Write-Host ("━" * (62 - $t.Length)) -ForegroundColor Cyan }
function Ok($m)   { Write-Host "  ✓ $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  ⚠ $m" -ForegroundColor Yellow }
function Err($m)  { Write-Host "  ✗ $m" -ForegroundColor Red }
function Info($m) { Write-Host "  · $m" -ForegroundColor DarkGray }

function Write-FileUtf8([string]$Path, [string]$Content) {
  $dir = Split-Path -Parent $Path
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
}

# === 嵌入檔案內容（單一檔案分發核心）====================================

$FILE_CLAW_PS1 = @'
# Claw v3 — Claude Code launcher with codex + gemini plugins (in-session delegation)
# by 阿亮老師（曾慶良 主任）

$ErrorActionPreference = 'Continue'
$env:PYTHONIOENCODING  = 'utf-8'

function Show-About {
  Write-Host ""
  Write-Host "  ╭───────────────────────────────────────────────────────────╮" -ForegroundColor DarkCyan
  Write-Host "  │                  關於作者                                 │" -ForegroundColor DarkCyan
  Write-Host "  ╰───────────────────────────────────────────────────────────╯" -ForegroundColor DarkCyan
  Write-Host ""
  Write-Host "    👨‍🏫 曾慶良 主任 (阿亮老師)" -ForegroundColor Yellow
  Write-Host ""
  Write-Host "    📌 現任職務" -ForegroundColor Cyan
  Write-Host "       🎓 新興科技推廣中心主任"
  Write-Host "       🎓 教育部學科中心研究教師"
  Write-Host "       🎓 臺北市資訊教育輔導員"
  Write-Host ""
  Write-Host "    🏆 獲獎紀錄" -ForegroundColor Cyan
  Write-Host "       🥇 2025 SETEAM 教學專業講師認證"
  Write-Host "       🥇 2024 教育部人工智慧講師認證"
  Write-Host "       🥇 2022、2023 指導學生 XR 專題競賽特優"
  Write-Host "       🥇 2022 VR 教材開發教師組特優"
  Write-Host "       🥇 2019 百大資訊人才獎"
  Write-Host "       🥇 2018、2019 親子天下創新 100 教師"
  Write-Host "       🥇 2018 臺北市特殊優良教師"
  Write-Host "       🥇 2017 教育部行動學習優等"
  Write-Host ""
  Write-Host "    📞 聯絡方式" -ForegroundColor Cyan
  Write-Host "       ▶ YouTube  : " -NoNewline; Write-Host "https://www.youtube.com/@Liang-yt02" -ForegroundColor Red
  Write-Host "       ▶ Facebook : " -NoNewline; Write-Host "https://www.facebook.com/groups/2754139931432955" -ForegroundColor Blue
  Write-Host "       ▶ Email    : " -NoNewline; Write-Host "3a01chatgpt@gmail.com" -ForegroundColor Green
  Write-Host ""
  Write-Host "    📜 © 2026 阿亮老師 版權所有 · 本工具僅供阿亮老師課程學員學習使用" -ForegroundColor DarkGray
  Write-Host ""
}

$showBanner = $true
$forwarded  = @()
foreach ($a in $args) {
  switch -Regex ($a) {
    '^--no-banner$'    { $showBanner = $false; continue }
    '^--about$'        { Show-About; exit 0 }
    '^--setup-help$'   {
      $help = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'setup-plugins.ps1'
      if (Test-Path $help) { & $help } else { Write-Host "找不到 setup-plugins.ps1" -ForegroundColor Red }
      exit 0
    }
    default            { $forwarded += $a }
  }
}

if ($showBanner) {
  # 龍蝦色 ANSI truecolor (PS 7+ / 現代終端機支援)
  $e = [char]27
  $LR  = "$e[38;2;230;75;55m"     # 龍蝦紅 (主色)
  $LO  = "$e[38;2;255;144;112m"   # 龍蝦橙 (高光)
  $LD  = "$e[38;2;160;40;30m"     # 龍蝦深紅 (陰影)
  $W   = "$e[38;2;230;230;230m"   # 白
  $G   = "$e[38;2;130;130;130m"   # 灰 (註解)
  $Y   = "$e[38;2;255;220;100m"   # 黃 (作者/重點)
  $M   = "$e[38;2;255;130;220m"   # 洋紅 (Codex)
  $B   = "$e[38;2;130;200;255m"   # 藍 (Gemini)
  $T   = "$e[38;2;100;230;200m"   # 青綠 (分隔線)
  $RST = "$e[0m"

  Write-Host ""
  Write-Host "    $LR██████╗██╗      █████╗ ██╗    ██╗$RST       $LO🦞 🦞 🦞$RST"
  Write-Host "   $LR██╔════╝██║     ██╔══██╗██║    ██║$RST        $LO🦞 🦞$RST"
  Write-Host "   $LR██║     ██║     ███████║██║ █╗ ██║$RST        $LO🦞 🦞$RST       $Y v3.0$RST"
  Write-Host "   $LR██║     ██║     ██╔══██║██║███╗██║$RST        $LO🦞 🦞$RST       $W Claude × Codex × Gemini$RST"
  Write-Host "   $LR╚██████╗███████╗██║  ██║╚███╔███╔╝$RST         $LO🦞$RST         $G in-session delegation$RST"
  Write-Host "    $LR╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝$RST          $LO🦞$RST"
  Write-Host ""
  Write-Host "    $Y by 阿亮老師（曾慶良 主任）$RST"
  Write-Host "       $G 新興科技推廣中心主任 · 教育部學科中心研究教師 · 臺北市資訊教育輔導員$RST"
  Write-Host "       $G YouTube: @Liang-yt02  ·  Email: 3a01chatgpt@gmail.com$RST"
  Write-Host ""
  Write-Host "    $T━━━━━━━━━━━━━━━━━━━━━ 📋 使用說明 ━━━━━━━━━━━━━━━━━━━━━$RST"
  Write-Host ""
  Write-Host "    $LR🦞 主場$RST    $W 直接打字$RST  $G→ Claude (有對話記憶、cache 命中、最便宜)$RST"
  Write-Host ""
  Write-Host "    $M🤖 Codex$RST   $G(OpenAI 視角，擅長挑戰決策)$RST"
  Write-Host "       $M/codex:review$RST                $G 程式碼審查$RST"
  Write-Host "       $M/codex:adversarial-review$RST    $G 對抗式挑戰你的設計$RST"
  Write-Host "       $M/codex:rescue$RST $W<任務>$RST            $G 委派任務 (修 bug、追問題)$RST"
  Write-Host "       $M/codex:rescue --background$RST   $G 背景跑，繼續對話$RST"
  Write-Host "       ${M}/codex:status${RST} ${G}/${RST} ${M}:result${RST} ${G}/${RST} ${M}:cancel${RST}  ${G}看/拿/取消背景任務${RST}"
  Write-Host ""
  Write-Host "    $B✨ Gemini$RST  $G(1M context, 看整個專案)$RST"
  Write-Host "       $B/gemini:review$RST               $G 程式碼審查 (1M context 一次看完)$RST"
  Write-Host "       $B/gemini:adversarial-review$RST   $G 對抗式挑戰$RST"
  Write-Host "       $B/gemini:rescue$RST $W<任務>$RST           $G 委派任務$RST"
  Write-Host "       $B/gemini:rescue --background$RST  $G 背景跑$RST"
  Write-Host "       ${B}/gemini:status${RST} ${G}/${RST} ${B}:result${RST} ${G}/${RST} ${B}:cancel${RST}  ${G}看/拿/取消背景任務${RST}"
  Write-Host ""
  Write-Host "    $Y🚩 旗標$RST     $G(加在指令後)$RST"
  Write-Host "       $Y--base main$RST       $G 審查 branch 與 main 差異$RST"
  Write-Host "       $Y--background$RST      $G 背景跑，不阻塞對話$RST"
  Write-Host "       $Y--model$RST $W<名稱>$RST    $G 指定模型 (gemini: flash/pro/flash-3/pro-3)$RST"
  Write-Host ""
  Write-Host "    $LO🛠️  MCP 切換$RST  $G(在 PowerShell, 不在 claude 內)$RST"
  Write-Host "       $LO mcp-ls$RST            $G 看目前啟用了哪些 MCP$RST"
  Write-Host "       $LO mcp-on$RST $W<名稱>$RST     $G 載入備援 MCP$RST"
  Write-Host "       $LO mcp-off all$RST       $G 一次卸下全部$RST"
  Write-Host ""
  Write-Host "    $W❓ 啟動器選項$RST"
  Write-Host "       $W claw --about$RST          $G 完整作者資訊 (職務/獎項/聯絡)$RST"
  Write-Host "       $W claw --setup-help$RST     $G plugin 安裝指引$RST"
  Write-Host "       $W claw --no-banner$RST      $G 跳過此 banner 啟動$RST"
  Write-Host ""
  Write-Host "    $T━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$RST"
  Write-Host ""
  Write-Host "    ${G}正在啟動 claude...${RST}"
  Write-Host ""
}

& claude @forwarded
exit $LASTEXITCODE
'@

$FILE_CLAW_BAT = @'
@echo off
chcp 65001 >nul
powershell -NoLogo -ExecutionPolicy Bypass -File "%~dp0claw.ps1" %*
exit /b %ERRORLEVEL%
'@

$FILE_SETUP_PLUGINS = @'
# Claw v3 — plugin 手動安裝指引
# by 阿亮老師（曾慶良 主任）

Write-Host @"

╭─────────────────────────────────────────────────────────────────╮
│  Claw v3 ─ Plugin 手動安裝指引                                  │
╰─────────────────────────────────────────────────────────────────╯

⚡ 快速法 (從 PowerShell 直接執行，不用進 claude session)

   claude plugin marketplace add openai/codex-plugin-cc
   claude plugin install codex@openai-codex
   claude plugin marketplace add abiswas97/gemini-plugin-cc
   claude plugin install gemini@abiswas97-gemini

✋ 互動法 (進入 claude 後在對話中輸入)

   1. claw                                        # 啟動
   2. /plugin marketplace add openai/codex-plugin-cc
   3. /plugin install codex@openai-codex
   4. /plugin marketplace add abiswas97/gemini-plugin-cc
   5. /plugin install gemini@abiswas97-gemini
   6. /reload-plugins
   7. /codex:setup
   8. /gemini:setup

🔑 認證 (若 setup 提示尚未登入)

   Codex 登入:
       !codex login

   Gemini 認證 (擇一):
       !gcloud auth application-default login
       `$env:GOOGLE_API_KEY = "<key from AI Studio>"

🧪 試跑

   /codex:review
   /gemini:review

─────────────────────────────────────────────────────────────────
  by 阿亮老師（曾慶良 主任）
  YouTube: @Liang-yt02  ·  Email: 3a01chatgpt@gmail.com
─────────────────────────────────────────────────────────────────

"@ -ForegroundColor Cyan
'@

$FILE_UNINSTALL = @'
# Claw v3 解除安裝程式
# by 阿亮老師（曾慶良 主任）

[CmdletBinding()]
param(
  [string]$InstallDir = "$env:USERPROFILE\.claude\claw",
  [switch]$KeepPlugins,
  [switch]$KeepProfile
)

function Section($t) { Write-Host ""; Write-Host "━━━ $t " -NoNewline -ForegroundColor Cyan; Write-Host ("━" * (62 - $t.Length)) -ForegroundColor Cyan }
function Ok($m)   { Write-Host "  ✓ $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  ⚠ $m" -ForegroundColor Yellow }
function Info($m) { Write-Host "  · $m" -ForegroundColor DarkGray }

Write-Host ""
Write-Host "  Claw v3 解除安裝" -ForegroundColor Yellow

Section "1/3 移除安裝目錄"
if (Test-Path $InstallDir) {
  Remove-Item $InstallDir -Recurse -Force
  Ok "已刪除 $InstallDir"
} else {
  Info "$InstallDir 不存在，跳過"
}

Section "2/3 卸載 Claude Code plugin"
if ($KeepPlugins) {
  Warn "略過 plugin 卸載 (-KeepPlugins)"
} else {
  foreach ($p in @('codex@openai-codex', 'gemini@abiswas97-gemini')) {
    & claude plugin uninstall $p 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Ok "已卸載: $p" } else { Warn "$p 未卸載 (可能未安裝)" }
  }
}

Section "3/3 清理 PowerShell profile"
if ($KeepProfile) {
  Warn "略過 profile 清理 (-KeepProfile)"
} elseif (Test-Path $PROFILE) {
  $content = Get-Content $PROFILE -Raw
  $marker  = '# === claw v3 (auto-installed) ==='
  $endMark = '# === end claw v3 ==='
  if ($content.Contains($marker)) {
    $cleaned = [regex]::Replace($content, "(?ms)\r?\n?$([regex]::Escape($marker)).*?$([regex]::Escape($endMark))\r?\n?", '')
    Set-Content -Path $PROFILE -Value $cleaned -NoNewline
    Ok "已從 $PROFILE 移除 claw 區塊"
  } else { Info "profile 中無 claw 區塊，跳過" }
}

Write-Host ""
Write-Host "  ✓ 解除安裝完成" -ForegroundColor Green
Write-Host ""
'@

$FILE_MCP_LOAD = @'
# MCP 載入腳本 - 把備援清單裡的 MCP 暫時載回 ~/.claude.json
param(
  [Parameter(Mandatory=$true)]
  [string]$Name
)

$claudeJson = "$env:USERPROFILE\.claude.json"
$presetFile = "$PSScriptRoot\$Name.json"

if (-not (Test-Path $presetFile)) {
  Write-Host "❌ 找不到備援檔: $presetFile" -ForegroundColor Red
  Write-Host "可用的備援:" -ForegroundColor Yellow
  Get-ChildItem $PSScriptRoot -Filter "*.json" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  - $($_.BaseName)"
  }
  exit 1
}

Copy-Item $claudeJson "$claudeJson.auto.bak" -Force

$j = Get-Content $claudeJson -Raw | ConvertFrom-Json -AsHashtable
if (-not $j.ContainsKey('mcpServers') -or $null -eq $j.mcpServers) { $j.mcpServers = @{} }

$preset = Get-Content $presetFile -Raw | ConvertFrom-Json -AsHashtable
$j.mcpServers[$Name] = $preset

$json = $j | ConvertTo-Json -Depth 100
[System.IO.File]::WriteAllText($claudeJson, $json, [System.Text.UTF8Encoding]::new($false))

Write-Host "✅ 已載入 MCP: $Name" -ForegroundColor Green
Write-Host "目前啟用的 MCP:" -ForegroundColor Cyan
$j.mcpServers.Keys | ForEach-Object { Write-Host "  - $_" }
Write-Host ""
Write-Host "⚠️  請關閉並重啟 Claude Code / claw 才會生效" -ForegroundColor Yellow
'@

$FILE_MCP_UNLOAD = @'
# MCP 卸下腳本 - 從 ~/.claude.json 移除指定 MCP（備援檔不會刪）
param(
  [Parameter(Mandatory=$true)]
  [string]$Name
)

$claudeJson = "$env:USERPROFILE\.claude.json"
Copy-Item $claudeJson "$claudeJson.auto.bak" -Force

$j = Get-Content $claudeJson -Raw | ConvertFrom-Json -AsHashtable
if (-not $j.ContainsKey('mcpServers') -or $null -eq $j.mcpServers) { $j.mcpServers = @{} }

if ($Name -eq 'all') {
  $count = $j.mcpServers.Keys.Count
  $j.mcpServers = @{}
  Write-Host "✅ 已卸下全部 $count 個 MCP" -ForegroundColor Green
} else {
  if ($j.mcpServers.ContainsKey($Name)) {
    $j.mcpServers.Remove($Name)
    Write-Host "✅ 已卸下 MCP: $Name" -ForegroundColor Green
  } else {
    Write-Host "ℹ️  MCP 沒在啟用清單裡: $Name" -ForegroundColor Yellow
  }
}

$json = $j | ConvertTo-Json -Depth 100
[System.IO.File]::WriteAllText($claudeJson, $json, [System.Text.UTF8Encoding]::new($false))

Write-Host "目前啟用的 MCP:" -ForegroundColor Cyan
if ($j.mcpServers.Keys.Count -eq 0) {
  Write-Host "  (無 - 啟動最快、context 最乾淨)" -ForegroundColor Gray
} else {
  $j.mcpServers.Keys | ForEach-Object { Write-Host "  - $_" }
}
Write-Host ""
Write-Host "⚠️  請關閉並重啟 Claude Code / claw 才會生效" -ForegroundColor Yellow
'@

$FILE_MCP_LIST = @'
# 顯示目前啟用的 MCP，以及備援清單裡有哪些可載入
$claudeJson = "$env:USERPROFILE\.claude.json"
$j = Get-Content $claudeJson -Raw | ConvertFrom-Json -AsHashtable

Write-Host "=== 目前啟用 (寫在 ~/.claude.json) ===" -ForegroundColor Cyan
if (-not $j.mcpServers -or $j.mcpServers.Keys.Count -eq 0) {
  Write-Host "  (無 - 啟動最快、context 最乾淨)" -ForegroundColor Gray
} else {
  $j.mcpServers.Keys | Sort-Object | ForEach-Object { Write-Host "  ✓ $_" -ForegroundColor Green }
}

Write-Host ""
Write-Host "=== 備援清單 (~/.claude/mcp-presets/) ===" -ForegroundColor Cyan
Get-ChildItem $PSScriptRoot -Filter "*.json" -ErrorAction SilentlyContinue | ForEach-Object {
  $name = $_.BaseName
  $active = $j.mcpServers -and $j.mcpServers.ContainsKey($name)
  $marker = if ($active) { "✓ (已啟用)" } else { "  (未啟用)" }
  $color = if ($active) { 'Green' } else { 'Gray' }
  Write-Host "  $marker $name" -ForegroundColor $color
}

Write-Host ""
Write-Host "用法 (PowerShell profile 已設好 alias):" -ForegroundColor Yellow
Write-Host "  mcp-on <name>     - 載入指定 MCP"
Write-Host "  mcp-off <name>    - 卸下指定 MCP"
Write-Host "  mcp-off all       - 卸下全部"
Write-Host "  mcp-ls            - 顯示目前狀態"
'@

$FILE_MCP_README = @'
# MCP 按需載入清單

> Claude Code 啟動時會把 ~/.claude.json 的 mcpServers 全部載入並注入 context。
> 工具越多 → context 越胖 → 啟動越慢、token 越貴。
> 解法：平常 mcpServers 保持空的（最快），需要時用一個指令切回。

## 用法

```powershell
mcp-ls                       # 看目前啟用了哪些
mcp-on twstockmcpserver      # 載入備援 MCP
mcp-off twstockmcpserver     # 卸下
mcp-off all                  # 一次卸下全部
```

⚠️ 切換後**必須關閉並重啟** Claude Code / claw 才會生效。

## 加入新的備援 MCP

把 MCP server 設定 JSON 存成 `<名稱>.json` 放進此資料夾即可。例如：

```jsonc
// twstockmcpserver.json
{ "type": "http", "url": "https://TW-Stock-MCP-Server.fastmcp.app/mcp" }
```

之後就能 `mcp-on twstockmcpserver`。

---

by 阿亮老師（曾慶良 主任）
'@

# === Banner ===
Write-Host ""
Write-Host "    ██████╗██╗      █████╗ ██╗    ██╗" -ForegroundColor Cyan
Write-Host "   ██╔════╝██║     ██╔══██╗██║    ██║" -ForegroundColor Cyan
Write-Host "   ██║     ██║     ███████║██║ █╗ ██║" -ForegroundColor Cyan
Write-Host "   ██║     ██║     ██╔══██║██║███╗██║" -ForegroundColor Cyan
Write-Host "   ╚██████╗███████╗██║  ██║╚███╔███╔╝" -ForegroundColor Cyan
Write-Host "    ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝ " -ForegroundColor Cyan
Write-Host ""
Write-Host "    Claw v3.0  一鍵安裝程式 (自包含)" -ForegroundColor White
Write-Host "    Claude × Codex × Gemini  ·  in-session delegation" -ForegroundColor DarkGray
Write-Host "    by 阿亮老師（曾慶良 主任）" -ForegroundColor Yellow

# === Step 1: 檢查並自動補裝前置 CLI ===
Section "1/6 檢查並自動補裝前置 CLI"
$cliMap = [ordered]@{
  'claude' = @{ desc = 'Claude Code';   pkg = '@anthropic-ai/claude-code' }
  'codex'  = @{ desc = 'OpenAI Codex';  pkg = '@openai/codex' }
  'gemini' = @{ desc = 'Google Gemini'; pkg = '@google/gemini-cli' }
}

# Node.js 是大魚，必須先有
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  Err "Node.js 未安裝 — 這是必需的基礎依賴"
  Write-Host ""
  Warn "請先安裝 Node.js 18+，然後重新執行此程式："
  Write-Host "    下載頁面: https://nodejs.org" -ForegroundColor Yellow
  Write-Host "    （安裝完記得重開 PowerShell 讓 PATH 生效）" -ForegroundColor DarkGray
  Write-Host ""
  try { Start-Process 'https://nodejs.org' } catch {}
  exit 1
}
Ok "node  (Node.js 18+)"

# 三家 CLI 缺什麼自動補裝
foreach ($cli in $cliMap.Keys) {
  if (Get-Command $cli -ErrorAction SilentlyContinue) {
    Ok "$cli  ($($cliMap[$cli].desc))"
  } else {
    Warn "$cli 未安裝，自動執行: npm install -g $($cliMap[$cli].pkg)"
    & npm install -g $cliMap[$cli].pkg 2>&1 | Out-String | ForEach-Object {
      $_.TrimEnd() -split "`n" | ForEach-Object { if ($_) { Write-Host "    $_" -ForegroundColor DarkGray } }
    }
    if ($LASTEXITCODE -ne 0 -or -not (Get-Command $cli -ErrorAction SilentlyContinue)) {
      Err "$cli 自動安裝失敗 (npm exit $LASTEXITCODE)"
      Warn "請手動執行: npm install -g $($cliMap[$cli].pkg)"
      exit 1
    }
    Ok "$cli 自動安裝完成 ($($cliMap[$cli].desc))"
  }
}

# === Step 2: 寫出檔案 ===
Section "2/6 部署檔案到 $InstallDir"
if (-not (Test-Path $InstallDir)) {
  New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
$mcpDir = "$env:USERPROFILE\.claude\mcp-presets"
if (-not (Test-Path $mcpDir)) {
  New-Item -ItemType Directory -Path $mcpDir -Force | Out-Null
}

$deploy = [ordered]@{
  "$InstallDir\claw.ps1"          = $FILE_CLAW_PS1
  "$InstallDir\claw.bat"          = $FILE_CLAW_BAT
  "$InstallDir\setup-plugins.ps1" = $FILE_SETUP_PLUGINS
  "$InstallDir\uninstall.ps1"     = $FILE_UNINSTALL
  "$mcpDir\load.ps1"              = $FILE_MCP_LOAD
  "$mcpDir\unload.ps1"            = $FILE_MCP_UNLOAD
  "$mcpDir\list.ps1"              = $FILE_MCP_LIST
  "$mcpDir\README.md"             = $FILE_MCP_README
}
foreach ($k in $deploy.Keys) {
  if ((Test-Path $k) -and -not $Force) {
    Warn "已存在: $(Split-Path -Leaf $k)  (用 -Force 可覆蓋)"
    continue
  }
  Write-FileUtf8 $k $deploy[$k]
  Ok (Split-Path -Leaf $k)
}

# === Step 3: 安裝兩個 plugin ===
Section "3/6 安裝 Claude Code plugin"
if ($SkipPlugins) {
  Warn "已略過 plugin 安裝 (-SkipPlugins)"
} else {
  $plugins = @(
    @{ market = 'openai/codex-plugin-cc';     install = 'codex@openai-codex';      label = 'Codex (OpenAI 官方)' }
    @{ market = 'abiswas97/gemini-plugin-cc'; install = 'gemini@abiswas97-gemini'; label = 'Gemini (社群版)' }
  )
  foreach ($p in $plugins) {
    Info "[$($p.label)] 加入 marketplace: $($p.market)"
    & claude plugin marketplace add $p.market 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Warn "marketplace add 退出碼 $LASTEXITCODE (可能已存在)" }
    Info "[$($p.label)] 安裝 plugin: $($p.install)"
    & claude plugin install $p.install 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
      Err "plugin install 失敗 (退出碼 $LASTEXITCODE)"
      Warn "請手動進入 claude 後執行: /plugin install $($p.install)"
    } else {
      Ok "$($p.label) 安裝成功"
    }
  }
}

# === Step 4: 設定 PowerShell profile ===
Section "4/6 設定 PowerShell profile"
if (-not (Test-Path $PROFILE)) {
  New-Item -ItemType File -Path $PROFILE -Force | Out-Null
  Ok "建立 profile: $PROFILE"
}
$marker    = '# === claw v3 (auto-installed) ==='
$endMarker = '# === end claw v3 ==='
$existing  = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
if ($null -eq $existing) { $existing = '' }
if ($existing.Contains($marker)) {
  Warn "profile 已含 claw 設定，跳過 (避免重複)"
} else {
  $block = @"

$marker
if ('$InstallDir' -notin (`$env:PATH -split ';')) {
  `$env:PATH += ';$InstallDir'
}
function mcp-on  { & "`$env:USERPROFILE\.claude\mcp-presets\load.ps1"   `$args[0] }
function mcp-off { & "`$env:USERPROFILE\.claude\mcp-presets\unload.ps1" `$args[0] }
function mcp-ls  { & "`$env:USERPROFILE\.claude\mcp-presets\list.ps1" }
$endMarker
"@
  Add-Content $PROFILE $block
  Ok "已加入 $PROFILE"
  Info "PATH += $InstallDir"
  Info "alias  mcp-on / mcp-off / mcp-ls"
}

# === Step 5: 互動式認證 (Codex + Gemini) ===
Section "5/6 互動式認證 Codex 與 Gemini"
if ($SkipAuth) {
  Warn "已略過認證 (-SkipAuth)。事後請手動執行 codex login 與設定 GOOGLE_API_KEY"
} else {
  # ── Codex ──
  $codexAuthFile = "$env:USERPROFILE\.codex\auth.json"
  if (Test-Path $codexAuthFile) {
    Ok "Codex 已認證 (找到 $codexAuthFile)"
  } else {
    Write-Host ""
    Write-Host "  [Codex 登入]" -ForegroundColor Magenta
    Write-Host "    會跳出瀏覽器登入 ChatGPT，或選擇輸入 OpenAI API Key" -ForegroundColor DarkGray
    $ans = Read-Host "    現在執行 codex login? [Y/n]"
    if ($ans -notmatch '^[Nn]') {
      Info "執行: codex login"
      & codex login
      if (Test-Path $codexAuthFile) {
        Ok "Codex 登入成功"
      } else {
        Warn "Codex 似乎未完成登入，事後可手動執行: codex login"
      }
    } else {
      Warn "略過 Codex 登入，事後請手動執行: codex login"
    }
  }

  # ── Gemini ──
  $geminiKeySet = -not [string]::IsNullOrWhiteSpace([System.Environment]::GetEnvironmentVariable('GOOGLE_API_KEY', 'User')) `
                -or -not [string]::IsNullOrWhiteSpace([System.Environment]::GetEnvironmentVariable('GOOGLE_API_KEY', 'Machine')) `
                -or (Test-Path "$env:USERPROFILE\.config\gcloud\application_default_credentials.json")
  if ($geminiKeySet) {
    Ok "Gemini 已認證 (GOOGLE_API_KEY 已設定 或 gcloud ADC 已存在)"
  } else {
    Write-Host ""
    Write-Host "  [Gemini 認證]" -ForegroundColor Blue
    Write-Host "    最簡單方式: 從 https://aistudio.google.com/app/apikey 取得免費 API Key" -ForegroundColor DarkGray
    Write-Host "    (該頁面登入 Google 帳號 → 點 'Create API key' → 複製)" -ForegroundColor DarkGray
    $key = Read-Host "    貼上 GOOGLE_API_KEY (留空略過, 'gcloud' 改走 gcloud auth)"
    $key = $key.Trim()
    if ($key -eq 'gcloud') {
      if (Get-Command gcloud -ErrorAction SilentlyContinue) {
        Info "執行: gcloud auth application-default login"
        & gcloud auth application-default login
      } else {
        Warn "gcloud 未安裝，請至 https://cloud.google.com/sdk/docs/install 下載"
        Warn "或回頭用 API Key 方式 (從 https://aistudio.google.com/app/apikey 取得)"
      }
    } elseif ($key) {
      [System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', $key, 'User')
      $env:GOOGLE_API_KEY = $key
      Ok "已永久設定 GOOGLE_API_KEY (使用者層級, 重開 PowerShell 後依然有效)"
    } else {
      Warn "略過 Gemini 認證，事後可手動: \$env:GOOGLE_API_KEY = '<key>'"
    }
  }
}

# === Step 6: 完成 ===
Section "6/6 完成"
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "  ✓ 安裝完成！" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "  下一步 (就這一步！):" -ForegroundColor Cyan
Write-Host "    1. 關掉這個 PowerShell 視窗，重新開一個" -ForegroundColor White
Write-Host "    2. 任何位置輸入 " -NoNewline; Write-Host "claw" -ForegroundColor Yellow
Write-Host "    3. 看到 ASCII 大字 CLAW + 進入 Claude Code = 成功 🎉"
Write-Host ""
Write-Host "  進入後可以直接使用:" -ForegroundColor Cyan
Write-Host "    直接打字           " -NoNewline -ForegroundColor White; Write-Host "→ Claude (主場)" -ForegroundColor DarkGray
Write-Host "    /codex:review      " -NoNewline -ForegroundColor Magenta; Write-Host "→ Codex 程式碼審查" -ForegroundColor DarkGray
Write-Host "    /codex:rescue      " -NoNewline -ForegroundColor Magenta; Write-Host "→ 委派 Codex 修 bug" -ForegroundColor DarkGray
Write-Host "    /gemini:review     " -NoNewline -ForegroundColor Blue;    Write-Host "→ Gemini 用 1M context 看整個專案" -ForegroundColor DarkGray
Write-Host "    /gemini:rescue     " -NoNewline -ForegroundColor Blue;    Write-Host "→ 委派 Gemini" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  解除安裝:  " -NoNewline -ForegroundColor DarkGray
Write-Host "& `"$InstallDir\uninstall.ps1`"" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  by 阿亮老師（曾慶良 主任）" -ForegroundColor DarkYellow
Write-Host "  YouTube: @Liang-yt02  ·  Email: 3a01chatgpt@gmail.com" -ForegroundColor DarkGray
Write-Host ""
