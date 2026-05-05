# Netlify 工作流檢查清單

## 部署前

- 找出框架
- 找出 build command
- 找出 publish 目錄
- 確認本地 build 可成功
- 確認 `netlify status` 正常
- 確認是否要 preview 還是 production
- 確認是否已有 site link

## 部署中

- preview deploy 先跑一次
- 記錄部署 URL
- 若需正式發布，再加 `--prod`
- 若要指定站點，顯式使用 `--site`

## 部署後

- 檢查首頁是否正常
- 檢查 SPA 子路由是否正常
- 檢查資源載入
- 檢查環境變數是否生效
- 檢查 Functions / API 路徑

## 出錯時先看什麼

- 本地 `npm run build`
- `netlify.toml`
- publish 目錄
- `netlify status`
- redirect 規則
- framework 特有設定
