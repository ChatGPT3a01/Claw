# Netlify 部署故障排除

## 目錄

- [部署失敗 / Build Error](#部署失敗--build-error)
- [404 錯誤 / 路由問題](#404-錯誤--路由問題)
- [資源載入失敗](#資源載入失敗)
- [環境變數無效](#環境變數無效)
- [Deploy 卡住](#deploy-卡住)
- [Node.js 版本問題](#nodejs-版本問題)
- [快取問題](#快取問題)
- [CLI 部署問題](#cli-部署問題)

---

## 部署失敗 / Build Error

### 問題：Build command failed

**常見原因與解決方案：**

```bash
# 1. 本地先測試 build
npm run build

# 2. 檢查是否有缺少的依賴
npm install

# 3. 檢查 Node.js 版本是否匹配
node -v
# 在 Netlify 設定 NODE_VERSION 環境變數
```

### 問題：Out of memory

```toml
# netlify.toml - 增加記憶體
[build.environment]
  NODE_OPTIONS = "--max-old-space-size=4096"
```

### 問題：找不到 build 指令

```toml
# 確認 netlify.toml 的 build command
[build]
  command = "npm run build"  # 確保 package.json 中有此腳本
  publish = "dist"           # 確保輸出目錄正確
```

---

## 404 錯誤 / 路由問題

### 問題：SPA 頁面重新整理後 404

**原因：** 缺少 SPA fallback 重定向。

**解決方案：**

```toml
# netlify.toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

或在發布目錄中建立 `_redirects` 檔案：
```
/*    /index.html   200
```

### 問題：Next.js 動態路由 404

**原因：** 缺少 `generateStaticParams` 或 `params` 未 await。

```typescript
// Next.js 16+：params 是 Promise
export default async function Page({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params;
  // ...
}

export async function generateStaticParams() {
  return [{ id: '1' }, { id: '2' }];
}
```

### 問題：子路徑 404

**原因：** `_redirects` 檔案不在發布目錄中。

```bash
# 確認 _redirects 在正確位置
# React/Vite: public/_redirects -> build 後會在 dist/_redirects
# Next.js: public/_redirects -> build 後會在 out/_redirects
```

---

## 資源載入失敗

### 問題：CSS/JS 載入失敗

**原因：** 路徑問題，使用了絕對路徑但基底路徑不同。

```html
<!-- 錯誤：硬編碼路徑 -->
<link href="/assets/style.css" />

<!-- 正確：使用相對路徑或框架提供的方式 -->
<link href="./assets/style.css" />
```

### 問題：圖片無法顯示

```typescript
// Vite: 使用 import
import logo from './assets/logo.png';
<img src={logo} alt="Logo" />

// 或使用 public 目錄（不經過打包）
<img src="/logo.png" alt="Logo" />
```

---

## 環境變數無效

### 問題：前端讀不到環境變數

**原因：** 未使用框架要求的前綴。

```bash
# Vite 框架
VITE_API_URL=https://api.example.com      # 前端可見
API_SECRET=xxx                              # 僅 server 端可見

# Next.js
NEXT_PUBLIC_API_URL=https://api.example.com # 前端可見
API_SECRET=xxx                              # 僅 server 端可見

# CRA
REACT_APP_API_URL=https://api.example.com   # 前端可見
```

### 問題：環境變數在 build 時未生效

**原因：** 環境變數需要在 build 之前設定。

```bash
# CLI 設定後重新觸發 deploy
netlify env:set VITE_API_URL "https://api.example.com"
netlify deploy --prod
```

### 問題：netlify.toml 中的環境變數被忽略

```toml
# 正確語法
[context.production.environment]
  API_URL = "https://api.example.com"

# 錯誤語法（不支援嵌套）
[build.environment]
  API_URL = "https://api.example.com"  # 這個只在 build 階段有效
```

---

## Deploy 卡住

### 問題：部署一直在 Uploading

```bash
# 清除快取重試
netlify deploy --prod --clear

# 檢查檔案大小（Netlify 限制單檔 10GB，免費版 100MB）
du -sh dist/

# 排除不需要的大型檔案
# 在 .gitignore 或 .netlifyignore 中排除
```

### 問題：部署成功但網站沒更新

```bash
# 1. 確認部署到正確的 site
netlify status

# 2. 清除瀏覽器快取
# Ctrl+F5 或 Cmd+Shift+R

# 3. 清除 CDN 快取（需要在 Dashboard 操作）
# Site settings > Build & deploy > Post processing > Asset optimization
```

---

## Node.js 版本問題

### 問題：Netlify 使用的 Node.js 版本與本地不同

```bash
# 方法 1: 環境變數
netlify env:set NODE_VERSION "20"

# 方法 2: netlify.toml
[build.environment]
  NODE_VERSION = "20"

# 方法 3: .node-version 檔案
echo "20" > .node-version

# 方法 4: .nvmrc 檔案
echo "20" > .nvmrc
```

---

## 快取問題

### 問題：Build 使用了舊的快取

```bash
# 清除 build 快取
netlify build --clear

# 或在 Dashboard: Deploys > Trigger deploy > Clear cache and deploy site
```

### 問題：npm/yarn 快取問題

```toml
# netlify.toml - 清除 npm 快取
[build.environment]
  NPM_FLAGS = "--legacy-peer-deps"
```

---

## CLI 部署問題

### 問題：netlify: command not found

```bash
# 全域安裝
npm install -g netlify-cli

# 或使用 npx
npx netlify-cli deploy --prod
```

### 問題：Not linked to a Netlify site

```bash
# 連結到現有站點
netlify link

# 或建立新站點
netlify init
```

### 問題：直接部署資料夾失敗

```bash
# 確保指定正確的目錄
netlify deploy --dir=./dist --prod

# 如果未連結站點，先連結
netlify link --id YOUR_SITE_ID
netlify deploy --dir=./dist --prod

# 或一次性部署（會提示選擇站點）
netlify deploy --dir=./dist --prod
```

### 問題：認證過期

```bash
# 重新登入
netlify logout
netlify login
```
