---
name: github-pages-deployment
description: GitHub Pages 靜態網站部署完整指南。支援 Next.js、React、Vue 等靜態網站部署到 GitHub Pages。包含配置檢查、動態路由修正、部署流程、常見問題解決、CDN 緩存管理、強制更新等。使用時機：(1) 部署 Next.js/React 靜態網站到 GitHub Pages，(2) 修正部署後的 404 錯誤，(3) 解決資源載入失敗，(4) 優化部署流程，(5) 要求「部署到 GitHub Pages」或「修復部署問題」。關鍵詞：GitHub Pages、部署、Next.js、靜態輸出、gh-pages、CDN、404、部署指南。
---

# GitHub Pages 部署指南

Next.js、React 等靜態網站完整的 GitHub Pages 部署解決方案。

## 概述

GitHub Pages 是免費的靜態網站託管服務，但部署時需要注意許多細節。這個 skill 提供完整的部署流程、常見問題解決方案和優化技巧。

## 部署前必備檢查

### 1. Next.js 配置 (`next.config.ts`)

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // ✅ 必須：靜態輸出模式
  output: 'export',

  // ✅ 必須：GitHub Pages 子路徑（倉庫名稱）
  // 如果是 username.github.io 則設為 ''
  basePath: '/your-repo-name',

  // ✅ 必須：禁用圖片優化
  images: {
    unoptimized: true,
  },

  // ✅ 必須：啟用尾隨斜線（避免 404）
  trailingSlash: true,
};

export default nextConfig;
```

**關鍵配置解釋：**

- **`output: 'export'`** - 生成靜態 HTML，不能使用伺服器功能
- **`basePath`** - 如果部署在子路徑（如 `https://user.github.io/repo/`），設為 `'/repo'`；如果是個人頁面則不需要
- **`images.unoptimized`** - 禁用 Next.js 的圖片優化（因為無伺服器支援）
- **`trailingSlash`** - 所有路由都加上尾隨斜線，避免 404 錯誤

### 2. Next.js 16+ 動態路由修正

**⚠️ 重要**：Next.js 16 開始，動態路由的 `params` 是 Promise。

**❌ 錯誤寫法（會導致空白頁面）：**

```typescript
export default function Page({ params }: { params: { id: string } }) {
  const data = getData(params.id); // ❌ 錯誤
  return <div>{data}</div>;
}
```

**✅ 正確寫法：**

```typescript
export default async function Page({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const resolvedParams = await params; // ✅ 必須 await
  const data = getData(resolvedParams.id);
  return <div>{data}</div>;
}

// metadata 也要修改
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params; // ✅ 必須 await
  return {
    title: `Page ${resolvedParams.id}`,
  };
}
```

### 3. 路由連結檢查

**所有內部連結必須有尾隨斜線**（因為設了 `trailingSlash: true`）

```typescript
// ❌ 錯誤
<Link href="/about">About</Link>
<Link href="/blog/post-1">Post</Link>

// ✅ 正確
<Link href="/about/">About</Link>
<Link href="/blog/post-1/">Post</Link>
```

### 4. 部署腳本設置 (`package.json`)

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "predeploy": "npm run build",
    "deploy": "gh-pages -d out -t"
  },
  "devDependencies": {
    "gh-pages": "^6.3.0"
  }
}
```

**說明：**
- `predeploy` - 自動在 deploy 前執行 build
- `deploy` - 使用 `gh-pages` 工具部署 `out` 目錄

## 完整部署流程

### 步驟 1：首次部署

```bash
# 1. 安裝 gh-pages 工具
npm install --save-dev gh-pages

# 2. 構建專案
npm run build

# 3. 檢查 out 目錄是否有 .nojekyll
# 如果沒有，必須創建
touch out/.nojekyll

# 4. 部署到 GitHub Pages
npm run deploy

# 5. 等待 2-3 分鐘讓 CDN 更新
```

### 步驟 2：GitHub 設置

1. 進入你的 GitHub 倉庫
2. 點擊 **Settings**
3. 左側菜單找到 **Pages**
4. 設置：
   - **Source**: 選擇 `Deploy from a branch`
   - **Branch**: 選擇 `gh-pages` 和 `/(root)`
5. 點擊 **Save**

### 步驟 3：驗證部署

```bash
# 訪問你的網站
# https://username.github.io/repo-name/

# 或查看部署歷史
git log origin/gh-pages --oneline -5
```

## 常見問題與解決方案

### ❌ 問題 1：404 錯誤 - 所有動態路由頁面都是 404

**原因：**
- Next.js 16+ params 是 Promise 但未 await
- 靜態生成時找不到 params，生成了 404 頁面

**✅ 解決方案：**

```typescript
// 修改所有動態路由頁面
interface PageProps {
  params: Promise<{ id: string }>; // ✅ 加上 Promise
}

export default async function Page({ params }: PageProps) {
  const resolvedParams = await params; // ✅ await params
  // 使用 resolvedParams.id
}
```

### ❌ 問題 2：`_next` 資源無法載入

**症狀：**頁面顯示但樣式和 JavaScript 都沒有加載。

**原因：**缺少 `.nojekyll` 文件，GitHub Pages 使用 Jekyll 處理，忽略 `_next` 目錄。

**✅ 解決方案：**

```bash
# 在 out 目錄創建 .nojekyll
touch out/.nojekyll

# 重新部署
npm run deploy
```

### ❌ 問題 3：部署後仍然是舊版本

**原因：**
1. gh-pages 分支未更新
2. CDN 緩存延遲（正常需要 2-5 分鐘）
3. 瀏覽器緩存

**✅ 解決方案：**

```bash
# 1. 檢查 gh-pages 分支是否更新
git fetch origin
git log origin/gh-pages --oneline -5

# 2. 強制清除並重新部署
rm -rf .next out node_modules/.cache
npm run build
touch out/.nojekyll
npm run deploy

# 3. 使用 Ctrl+F5 或 Cmd+Shift+R 強制刷新瀏覽器
# 等待 2-5 分鐘讓 CDN 更新
```

### ❌ 問題 4：圖片無法顯示

**原因：**
1. 未設置 `basePath`
2. 圖片路徑錯誤
3. 未禁用圖片優化

**✅ 解決方案：**

```typescript
// next.config.ts
export default {
  basePath: '/repo-name',
  images: {
    unoptimized: true, // ✅ 必須禁用
  },
};

// 使用圖片（會自動加上 basePath）
<Image
  src="/image.png"
  alt="..."
/>
```

### ❌ 問題 5：動態路由無法生成

**原因：**`generateStaticParams` 未正確設置或返回錯誤的路徑。

**✅ 解決方案：**

```typescript
export async function generateStaticParams() {
  // 必須返回所有可能的 params
  return [
    { id: '1' },
    { id: '2' },
    { id: '3' },
  ];
}

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = await params;
  // ...
}
```

## CDN 緩存管理

### 為什麼部署後需要等待？

GitHub Pages 使用 CDN（內容分發網路），更新會逐漸傳播到各個伺服器。

**典型時間表：**
- `npm run deploy` 執行完 → CDN 開始更新
- 2-3 分鐘 → 大多數用戶看到新版本
- 5-15 分鐘 → 所有 CDN 節點都更新完成

### 強制檢查更新

```bash
# 查看原始檔案（不經過 CDN 緩存）
curl -I https://raw.githubusercontent.com/user/repo/gh-pages/index.html

# 或在 GitHub 上直接檢查 gh-pages 分支
# https://github.com/user/repo/tree/gh-pages
```

### 瀏覽器緩存

```
Ctrl+F5 或 Cmd+Shift+R → 完全刷新（跳過瀏覽器緩存）
```

## 重新部署流程（更新現有網站）

```bash
# 1. 修改代碼後，提交到 main/master
git add .
git commit -m "更新內容"
git push origin main

# 2. 清除舊的構建文件
rm -rf .next out node_modules/.cache

# 3. 重新構建
npm run build

# 4. 確保 .nojekyll 存在
touch out/.nojekyll

# 5. 部署
npm run deploy

# 6. 驗證 gh-pages 分支已更新
git log origin/gh-pages --oneline -1

# 7. 等待 2-3 分鐘，然後用 Ctrl+F5 刷新瀏覽器
```

## 部署前測試

```bash
# 1. 本地構建靜態輸出
npm run build

# 2. 安裝 serve（本地伺服器）
npm install -g serve

# 3. 在本地測試靜態輸出
serve out

# 4. 訪問 http://localhost:3000
# 測試所有路由、連結、圖片是否正常

# 5. 確認無誤後再部署
npm run deploy
```

## 部署檢查清單

部署前必須確認以下事項：

- [ ] `next.config.ts` 有 `output: 'export'`
- [ ] `next.config.ts` 有正確的 `basePath`（如果需要）
- [ ] `next.config.ts` 有 `trailingSlash: true`
- [ ] `next.config.ts` 有 `images.unoptimized: true`
- [ ] 所有動態路由的 params 已加上 `Promise<>` 並 `await`
- [ ] 所有 `generateMetadata` 也已 `await` params
- [ ] 所有 Link 連結都有尾隨斜線 `/`
- [ ] `out/.nojekyll` 文件存在
- [ ] 本地測試通過（`npx serve out`）
- [ ] GitHub Pages 設置為 gh-pages 分支
- [ ] gh-pages 分支已更新

## 快速修復腳本

創建 `scripts/deploy.sh`：

```bash
#!/bin/bash

echo "🧹 清除舊的構建文件..."
rm -rf .next out node_modules/.cache

echo "🔨 構建專案..."
npm run build

echo "📝 創建 .nojekyll..."
touch out/.nojekyll

echo "🚀 部署到 GitHub Pages..."
npx gh-pages -d out -t

echo "✅ 部署完成！"
echo "⏰ 請等待 2-3 分鐘讓 CDN 緩存更新"
echo "🌐 訪問: https://username.github.io/repo-name/"
```

使用方式：

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 重要提醒

1. **CDN 緩存延遲**：GitHub Pages 部署後需要 2-5 分鐘才能全球同步
2. **瀏覽器緩存**：使用 `Ctrl+F5`（Windows）或 `Cmd+Shift+R`（Mac）強制刷新
3. **檢查原始文件**：訪問 `https://raw.githubusercontent.com/user/repo/gh-pages/path/to/file` 確認文件是否已更新
4. **動態路由必須預先生成**：所有路由必須在 `generateStaticParams` 中定義
5. **環境變數不會被部署**：`.env.local` 只在構建時讀取，不會包含在部署的靜態檔案中

## 參考資源

- **Next.js Static Exports**：https://nextjs.org/docs/app/building-your-application/deploying/static-exports
- **GitHub Pages 官方文檔**：https://docs.github.com/en/pages
- **gh-pages npm 套件**：https://www.npmjs.com/package/gh-pages
- **Deployment Troubleshooting**：https://docs.github.com/en/pages/getting-started-with-github-pages/troubleshooting-custom-domains-and-github-pages

## 成功部署的標誌

✅ 你將看到：
- 域名正確變成 `https://username.github.io/repo-name/`
- 所有頁面都能正常加載（包括動態路由）
- 圖片、樣式、JavaScript 都正常顯示
- 所有連結都可以點擊並導向正確頁面
- 沒有任何 404 或資源載入錯誤

🎉 完成！你的網站現在已成功部署到 GitHub Pages！
