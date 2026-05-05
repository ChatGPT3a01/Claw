# Netlify 部署模式

## 1. 資料夾直推

用在已經有 build 輸出時。

常見 publish 目錄：

- `dist`
- `out`
- `build`
- `public`
- `.output/public`

指令：

```bash
netlify deploy --dir=dist
netlify deploy --dir=dist --prod
```

適合：

- 靜態網站
- 臨時預覽
- 快速更新既有站點

## 2. Build 後部署

先在本地驗證 build，再部署。

標準順序：

1. 確認框架
2. 確認 build command
3. 確認 publish 目錄
4. 本地執行 build
5. 部署 preview
6. 確認後再部署 production

## 3. 建立新站

用在尚未綁定任何 Netlify site。

做法：

- 互動式 `netlify deploy`
- 或先 `netlify init`

如果使用者沒有指定 site name，可接受 Netlify 自動產生。

## 4. 連結既有站

用在專案已有對應 Netlify site。

```bash
netlify link --id <site-id>
netlify deploy --dir=dist --prod
```

若已知 site ID，優先明確指定，避免誤部署。

## 5. Preview 優先

預設先做 preview deploy，比直接推 production 更安全。

```bash
netlify deploy --dir=dist
```

適合：

- 第一次部署
- 不確定重定向或資源路徑
- 正在修 bug

## 6. Production 直推

只在以下情況直接 `--prod`：

- 使用者明確要求
- 站點已穩定
- 本地 build 已驗證
- publish 目錄明確

```bash
netlify deploy --dir=dist --prod
```

## 7. 使用 token 認證

適合 CI 或非互動環境。

```bash
NETLIFY_AUTH_TOKEN=xxxx netlify deploy --dir=dist --prod
```

Windows PowerShell：

```powershell
$env:NETLIFY_AUTH_TOKEN="xxxx"
netlify deploy --dir=dist --prod
```

## 8. 建議回覆格式

完成部署後，至少回報：

- 站點名稱或 site ID
- preview / production URL
- build command
- publish 目錄
- 是否修改 `netlify.toml`
