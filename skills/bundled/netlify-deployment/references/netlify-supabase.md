# Netlify + Supabase 整合

## 基本原則

先分清楚哪種金鑰可以放前端。

### 可以前端可見

- Supabase URL
- Supabase anon key

常見命名：

- Next.js: `NEXT_PUBLIC_SUPABASE_URL`、`NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Vite: `VITE_SUPABASE_URL`、`VITE_SUPABASE_ANON_KEY`

### 不可前端可見

- `SUPABASE_SERVICE_ROLE_KEY`

這種值只能放：

- Netlify 環境變數
- Netlify Functions / server 端執行環境

## 什麼時候需要 Netlify Functions

需要 Functions 的情況：

- 要使用 service role key
- 要做受保護的 admin 操作
- 要把第三方 API 與 Supabase 串起來
- 不想把敏感邏輯放前端

## 前端直連 Supabase

適合：

- 登入
- 一般查詢
- RLS 已正確設定

部署時檢查：

- 前端環境變數前綴正確
- 重新 build / redeploy
- 不要把 service role key 寫進前端

## Functions 代理模式

典型做法：

1. 前端呼叫 `/.netlify/functions/*`
2. Function 內使用 `SUPABASE_SERVICE_ROLE_KEY`
3. 回傳最小必要資料給前端

## 常見錯誤

- 把 service role key 放進前端 bundle
- 用錯環境變數前綴
- 改完 Netlify 環境變數卻沒重新部署
- RLS 未設好，誤以為是 Netlify 問題
