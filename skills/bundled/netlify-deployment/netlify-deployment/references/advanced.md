# Netlify 進階功能

## 目錄

- [Netlify Functions](#netlify-functions)
- [Edge Functions](#edge-functions)
- [表單處理](#表單處理)
- [Split Testing](#split-testing)
- [Build Plugins](#build-plugins)
- [Deploy Notifications](#deploy-notifications)
- [Large Media](#large-media)

---

## Netlify Functions

Serverless 函數，自動部署為 AWS Lambda。

### 基本結構

```
netlify/
  functions/
    hello.ts        # -> /.netlify/functions/hello
    api/
      users.ts      # -> /.netlify/functions/api-users
```

### 範例函數

```typescript
// netlify/functions/hello.ts
import type { Handler } from "@netlify/functions";

export const handler: Handler = async (event, context) => {
  const name = event.queryStringParameters?.name || "World";
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: `Hello, ${name}!` }),
  };
};
```

### netlify.toml 配置

```toml
[functions]
  directory = "netlify/functions"
  node_bundler = "esbuild"

# 將 /api/* 代理到 Functions
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

### 排程函數

```typescript
// netlify/functions/scheduled.ts
import { schedule } from "@netlify/functions";

export const handler = schedule("@daily", async () => {
  console.log("每天執行一次");
  return { statusCode: 200 };
});
```

---

## Edge Functions

在 CDN 邊緣節點執行，低延遲。

### 基本結構

```
netlify/
  edge-functions/
    hello.ts
```

### 範例

```typescript
// netlify/edge-functions/hello.ts
import type { Context } from "@netlify/edge-functions";

export default async (request: Request, context: Context) => {
  return new Response("Hello from the Edge!", {
    headers: { "content-type": "text/plain" },
  });
};

export const config = { path: "/edge-hello" };
```

### netlify.toml 配置

```toml
[[edge_functions]]
  function = "hello"
  path = "/edge-hello"
```

---

## 表單處理

Netlify 內建表單收集功能，無需後端。

### HTML 表單

```html
<form name="contact" method="POST" data-netlify="true">
  <input type="hidden" name="form-name" value="contact" />
  <input type="text" name="name" required />
  <input type="email" name="email" required />
  <textarea name="message"></textarea>
  <button type="submit">送出</button>
</form>
```

### React 表單

```jsx
function ContactForm() {
  return (
    <form name="contact" method="POST" data-netlify="true">
      <input type="hidden" name="form-name" value="contact" />
      <input type="text" name="name" />
      <input type="email" name="email" />
      <button type="submit">送出</button>
    </form>
  );
}
```

**收件位置**: Netlify Dashboard > Forms

---

## Split Testing

A/B 測試不同版本的網站。

### 設定步驟

1. 在 Netlify Dashboard > Split Testing
2. 選擇要測試的 Branch
3. 設定流量分配比例
4. 啟用測試

### netlify.toml

```toml
# Branch A 配置
[context.branch-a]
  command = "npm run build"

# Branch B 配置
[context.branch-b]
  command = "npm run build:variant"
```

---

## Build Plugins

擴展 Netlify 建置流程的外掛系統。

### 常用 Plugins

```toml
# 快取 Next.js 建置
[[plugins]]
  package = "@netlify/plugin-nextjs"

# 快取 Gatsby 建置
[[plugins]]
  package = "netlify-plugin-gatsby-cache"

# 自動生成 sitemap
[[plugins]]
  package = "netlify-plugin-sitemap"

# Lighthouse 效能檢測
[[plugins]]
  package = "@netlify/plugin-lighthouse"
```

### 自訂 Plugin

```javascript
// plugins/my-plugin/index.js
module.exports = {
  onPreBuild: ({ utils }) => {
    console.log("Build 前執行");
  },
  onBuild: ({ utils }) => {
    console.log("Build 中執行");
  },
  onPostBuild: ({ utils }) => {
    console.log("Build 後執行");
  },
};
```

```toml
[[plugins]]
  package = "./plugins/my-plugin"
```

---

## Deploy Notifications

### 設定 Webhook

**Dashboard 路徑**: Site settings > Build & deploy > Deploy notifications

支援：
- Slack 通知
- Email 通知
- Webhook（自訂 URL）
- GitHub commit status

---

## Large Media

Git LFS 整合，大型檔案存儲。

```bash
# 安裝
netlify lm:setup

# 追蹤大型檔案
git lfs track "*.jpg" "*.png" "*.mp4"

# 提交 .lfsconfig 和 .gitattributes
git add .lfsconfig .gitattributes
git commit -m "Set up Netlify Large Media"
```
