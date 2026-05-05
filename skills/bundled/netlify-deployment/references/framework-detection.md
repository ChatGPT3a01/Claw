# 框架偵測與部署模板選擇

## 先看哪些檔案

- `package.json`
- `vite.config.*`
- `next.config.*`
- `nuxt.config.*`
- `astro.config.*`
- `svelte.config.*`
- `angular.json`
- `netlify.toml`

## 依相依套件判斷

### Next.js

- `dependencies.next`
- 常見 publish：
  - static export: `out`
  - SSR/plugin: 交給 Netlify plugin

### Vite React / Vue

- `vite`
- `react` 或 `vue`
- publish: `dist`

### Nuxt 3

- `nuxt`
- static generate: `.output/public`
- SSR: 通常需 plugin / preset

### SvelteKit

- `@sveltejs/kit`
- `@sveltejs/adapter-netlify`
- publish: `build`

### Astro

- `astro`
- static: `dist`
- server: 看 adapter 設定

### Hugo

- `config.toml` 或 `hugo.toml`
- publish: `public`

### Angular

- `angular.json`
- publish: `dist/<project>/browser` 或 `dist/<project>`

## 選模板規則

1. 先沿用現有 `netlify.toml`
2. 若缺少，再依框架補最小配置
3. 若是 SPA，一定檢查 redirect fallback
4. 若是 SSR，不要誤用純靜態 publish 目錄
