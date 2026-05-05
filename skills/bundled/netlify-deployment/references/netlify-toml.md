# `netlify.toml` 快速規則

## 最小靜態站配置

```toml
[build]
  command = "npm run build"
  publish = "dist"
```

## SPA 路由回退

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

適用：

- React SPA
- Vue SPA
- Vite SPA
- Angular SPA

## Next.js static export

```toml
[build]
  command = "npm run build"
  publish = "out"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

## Nuxt static generate

```toml
[build]
  command = "npx nuxi generate"
  publish = ".output/public"
```

## Functions 目錄

```toml
[functions]
  directory = "netlify/functions"
  node_bundler = "esbuild"
```

## Edge Functions

```toml
[[edge_functions]]
  function = "hello"
  path = "/edge-hello"
```

## Build 環境變數

```toml
[build.environment]
  NODE_VERSION = "20"
  NODE_OPTIONS = "--max-old-space-size=4096"
```

## Production context

```toml
[context.production.environment]
  APP_ENV = "production"
```

## 常見錯誤

- `publish` 寫成原始碼資料夾，而不是 build 輸出資料夾
- SPA 缺少 `/* -> /index.html`
- 把秘密值直接硬寫進 `netlify.toml`
- framework 已有專用 adapter，卻仍用錯 publish 目錄
