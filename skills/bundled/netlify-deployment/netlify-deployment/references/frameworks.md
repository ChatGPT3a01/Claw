# 各框架 Netlify 部署詳細配置

## 目錄

- [Next.js (Static Export)](#nextjs-static-export)
- [Next.js (SSR with Netlify)](#nextjs-ssr-with-netlify)
- [React + Vite](#react--vite)
- [Vue + Vite](#vue--vite)
- [Nuxt 3](#nuxt-3)
- [SvelteKit](#sveltekit)
- [Astro](#astro)
- [Hugo](#hugo)
- [Gatsby](#gatsby)
- [Angular](#angular)
- [11ty (Eleventy)](#11ty-eleventy)

---

## Next.js (Static Export)

### next.config.ts

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  images: { unoptimized: true },
  trailingSlash: true,
};

export default nextConfig;
```

### netlify.toml

```toml
[build]
  command = "npm run build"
  publish = "out"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### 注意事項

- `output: 'export'` 不支援 API Routes、Middleware、ISR
- Next.js 16+ 動態路由 `params` 是 Promise，必須 `await`
- 所有動態路由需要 `generateStaticParams`

---

## Next.js (SSR with Netlify)

使用 `@netlify/plugin-nextjs` 支援完整 SSR。

### 安裝

```bash
npm install @netlify/plugin-nextjs
```

### netlify.toml

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

### 注意事項

- 支援 API Routes、Middleware、ISR、SSR
- 自動將 API Routes 轉為 Netlify Functions
- 支援 Image Optimization（透過 Netlify Image CDN）
- 不需要 `output: 'export'`

---

## React + Vite

### netlify.toml

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### 注意事項

- SPA 必須設定 `/* -> /index.html` 重定向
- 環境變數前綴：`VITE_`
- base URL：在 `vite.config.ts` 中設定 `base: '/'`

---

## Vue + Vite

### netlify.toml

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Vue Router 設定

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(), // 使用 HTML5 History Mode
  routes: [...]
});
```

---

## Nuxt 3

### 靜態生成（SSG）

```bash
npx nuxi generate
```

```toml
[build]
  command = "npx nuxi generate"
  publish = ".output/public"
```

### SSR 模式

```bash
npm install @netlify/plugin-nuxt
```

```toml
[build]
  command = "npx nuxi build"
  publish = "dist"

[[plugins]]
  package = "@netlify/plugin-nuxt"
```

### nuxt.config.ts

```typescript
export default defineNuxtConfig({
  nitro: {
    preset: 'netlify'  // SSR 模式需要
  }
});
```

---

## SvelteKit

### 安裝 Adapter

```bash
npm install @sveltejs/adapter-netlify
```

### svelte.config.js

```javascript
import adapter from '@sveltejs/adapter-netlify';

export default {
  kit: {
    adapter: adapter({
      edge: false,        // 使用 Netlify Functions
      split: false         // 所有路由打包為單一 Function
    })
  }
};
```

### netlify.toml

```toml
[build]
  command = "npm run build"
  publish = "build"
```

---

## Astro

### 靜態模式（預設）

```toml
[build]
  command = "npm run build"
  publish = "dist"
```

### SSR 模式

```bash
npx astro add netlify
```

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import netlify from '@astrojs/netlify';

export default defineConfig({
  output: 'server',
  adapter: netlify()
});
```

---

## Hugo

### netlify.toml

```toml
[build]
  command = "hugo"
  publish = "public"

[build.environment]
  HUGO_VERSION = "0.140.0"

[context.production.environment]
  HUGO_ENV = "production"
```

### 注意事項

- 務必指定 `HUGO_VERSION`，Netlify 預設版本較舊
- Hugo 的主題需透過 `git submodule` 或 Hugo Modules 引入

---

## Gatsby

### netlify.toml

```toml
[build]
  command = "gatsby build"
  publish = "public"

[[plugins]]
  package = "netlify-plugin-gatsby-cache"
```

### 安裝快取外掛

```bash
npm install netlify-plugin-gatsby-cache
```

---

## Angular

### netlify.toml

```toml
[build]
  command = "ng build"
  publish = "dist/<project-name>/browser"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### 注意事項

- 發布目錄為 `dist/<project-name>/browser`（Angular 17+ 新路徑）
- 舊版 Angular：`dist/<project-name>`

---

## 11ty (Eleventy)

### netlify.toml

```toml
[build]
  command = "npx @11ty/eleventy"
  publish = "_site"
```

### 注意事項

- 預設輸出目錄為 `_site`
- 可在 `.eleventy.js` 中自訂輸出目錄
