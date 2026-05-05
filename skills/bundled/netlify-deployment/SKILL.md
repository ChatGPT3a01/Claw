---
name: netlify-deployment
description: Deploy, update, troubleshoot, or configure projects on Netlify using the Netlify CLI. Use when the user asks to deploy to Netlify, push a built folder, link an existing site, create a new site, configure `netlify.toml`, set environment variables, fix Netlify build/runtime issues, wire Netlify Functions or Edge Functions, integrate Supabase on Netlify, or choose the correct publish directory and build command for frameworks like Next.js, React, Vue, Nuxt, SvelteKit, Astro, Hugo, Angular, or static HTML.
---

# Netlify Deployment

優先把這個技能當成「可執行工作流」，不是只有指令備忘錄。

## 核心做法

先判斷部署模式，再決定指令：

1. 如果專案已經有可部署輸出資料夾，例如 `dist`、`out`、`build`、`public`，優先走資料夾直推：
   - `netlify deploy --dir <publish-dir>`
   - 正式版加 `--prod`
2. 如果專案還沒 build，先找正確框架與 publish 目錄，再 build 後部署。
3. 如果站點尚未連結，先確認要建立新站還是連結既有站。
4. 如果部署失敗，先檢查本地 build、publish 目錄、登入狀態、`netlify.toml`、環境變數，再看錯誤種類。

## 執行順序

### Step 1: 檢查目前專案狀態

優先確認：

- 是否存在 `package.json`
- 是否存在 `netlify.toml`
- 是否已有輸出資料夾：`dist`、`out`、`build`、`public`、`.output/public`
- 是否能判斷框架
- 是否已經安裝 Netlify CLI
- 是否已登入 Netlify
- 是否已連結站點
- 是否有 `netlify/functions`、`netlify/edge-functions`
- 是否使用 Supabase 或其他後端服務

如果已經有明確輸出資料夾，優先直接部署，不要先做多餘重構。

### Step 2: 判斷使用哪種部署模式

#### 模式 A：資料夾直推

用在：

- 使用者明確要「直接部署這個資料夾」
- 專案已經 build 完成
- 只是更新靜態站內容

標準流程：

```bash
netlify deploy --dir=dist
netlify deploy --dir=dist --prod
```

#### 模式 B：專案 build 後部署

用在：

- 專案還沒 build
- 需要先確認框架的 build command 與 publish 目錄
- 需要修正 `netlify.toml`

先讀 [references/frameworks.md](references/frameworks.md) 與 [references/deployment-patterns.md](references/deployment-patterns.md)。

若框架不明確，先讀 [references/framework-detection.md](references/framework-detection.md)。

#### 模式 C：修復型部署

用在：

- Build 失敗
- 404 / 路由錯誤
- 環境變數無效
- 站點沒更新

先讀 [references/troubleshooting.md](references/troubleshooting.md)。

## CLI 使用規則

### 優先順序

1. 優先使用 `netlify` CLI
2. 若系統沒有全域安裝，優先使用 `npx netlify`
3. 只有在使用者明確要求全域安裝時，才安裝 `netlify-cli`

### 登入與認證

先檢查 `netlify status`。

- 若成功，繼續
- 若失敗，改走 `netlify login`
- 若使用者已有 token，可用 `NETLIFY_AUTH_TOKEN`

### 站點連結

如果尚未連結站點，先判斷：

- 要建立新站：使用 `netlify deploy` 或 `netlify init`
- 要連結既有站：使用 `netlify link --id <site-id>`

若已知 site ID，優先顯式指定，避免部署到錯誤站點。

## `netlify.toml` 規則

部署前若發現專案缺少 `netlify.toml`，且使用者需要穩定可重複部署，主動建立。

至少確認：

- `[build].command`
- `[build].publish`
- SPA 需要的 `[[redirects]]`
- Functions / Edge Functions 目錄

詳細寫法參閱：

- [references/netlify-toml.md](references/netlify-toml.md)
- [references/frameworks.md](references/frameworks.md)
- [references/framework-detection.md](references/framework-detection.md)

## 環境變數規則

不要把秘密值直接寫進 repo。

優先用：

- `netlify env:set`
- Netlify Dashboard 的 Environment variables

如果使用者要前端可見變數，必須使用對應框架前綴，不能混用。

如果專案含 Supabase，優先確認：

- 哪些值只能 server side 使用
- 哪些值是前端公開 anon key
- 是否需要 Netlify Functions 代為保護 service role key

## Windows 優先

這個技能在 Windows 環境中，優先提供 PowerShell 指令。

若需要一鍵部署腳本：

- Bash 環境用 [scripts/deploy.sh](scripts/deploy.sh)
- Windows PowerShell 用 [scripts/deploy.ps1](scripts/deploy.ps1)

## 常見決策

### 使用者說「幫我部署到 Netlify」

先做：

1. 找框架與輸出目錄
2. 若尚未 build，先 build
3. 若未登入或未連結，先補齊
4. 先做 preview deploy，確認後再 `--prod`

### 使用者說「直接把這個資料夾推上去」

先確認資料夾存在，再直接：

```bash
netlify deploy --dir=<folder>
```

若使用者明確要正式版，再加：

```bash
netlify deploy --dir=<folder> --prod
```

### 使用者說「網站部署成功但 404」

優先檢查：

- 是否是 SPA
- 是否缺少 `/* -> /index.html`
- `_redirects` 是否進到 publish 目錄
- Next.js 是否是 static export 還是 SSR

### 使用者說「環境變數沒生效」

優先檢查：

- 是 build-time 還是 runtime 變數
- 前端變數前綴是否正確
- 是否重新部署
- 是否設錯 site / context

### 使用者說「我要 Netlify + Supabase」

優先檢查：

- 是純前端 Supabase，還是需要 Functions 保護敏感金鑰
- 前端是否只暴露 anon key
- service role 是否只放在 Netlify 環境變數與 server 端
- redirect / API proxy 是否需要補

先讀 [references/netlify-supabase.md](references/netlify-supabase.md)。

## 讀哪些參考檔

- 需要框架特化部署方式時，讀 [references/frameworks.md](references/frameworks.md)
- 需要選擇部署模式或標準流程時，讀 [references/deployment-patterns.md](references/deployment-patterns.md)
- 需要寫或修正 `netlify.toml` 時，讀 [references/netlify-toml.md](references/netlify-toml.md)
- 需要判斷框架與 publish 目錄時，讀 [references/framework-detection.md](references/framework-detection.md)
- 需要排錯時，讀 [references/troubleshooting.md](references/troubleshooting.md)
- 需要進階功能時，讀 [references/advanced.md](references/advanced.md)
- 需要 CLI 指令對照時，讀 [references/cli-commands.md](references/cli-commands.md)
- 需要 Netlify + Supabase 整合時，讀 [references/netlify-supabase.md](references/netlify-supabase.md)

## 產出要求

完成部署任務時，回覆至少包含：

- 使用了哪個 publish 目錄
- 使用了哪個 build 指令
- 是 preview 還是 production deploy
- 若有修改，列出 `netlify.toml`、環境變數、重定向、框架設定的變更
- 若失敗，說明卡在哪一步與下一個最小修復動作
