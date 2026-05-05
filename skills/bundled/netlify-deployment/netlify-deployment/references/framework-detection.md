# 框架偵測與部署模板選擇

- 看 `package.json`
- 看 `vite.config.*`
- 看 `next.config.*`
- 看 `nuxt.config.*`
- 看 `astro.config.*`
- 看 `svelte.config.*`
- 看 `angular.json`
- 看 `netlify.toml`

常見規則：

- Next.js static: `out`
- Vite: `dist`
- Nuxt generate: `.output/public`
- SvelteKit: `build`
- Astro static: `dist`
- Hugo: `public`
