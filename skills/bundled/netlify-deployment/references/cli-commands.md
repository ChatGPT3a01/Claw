# Netlify CLI 指令速查

## 認證與狀態

```bash
netlify status
netlify login
netlify logout
```

## 站點操作

```bash
netlify init
netlify link
netlify link --id <site-id>
netlify unlink
netlify open
```

## 部署

```bash
netlify deploy --dir=dist
netlify deploy --dir=dist --prod
netlify deploy --dir=dist --prod --message "release note"
netlify deploy --dir=dist --site=<site-id>
```

若未全域安裝，可改：

```bash
npx netlify deploy --dir=dist --prod
```

## 環境變數

```bash
netlify env:list
netlify env:set KEY "value"
netlify env:get KEY
netlify env:unset KEY
```

## Build 與快取

```bash
netlify build
netlify build --clear
```

## 回滾

```bash
netlify rollback
```

## Functions

```bash
netlify functions:serve
netlify dev
```

## 常用判斷

- 要確認是否登入：`netlify status`
- 要確認是否已連站：`netlify status`
- 要先預覽部署：`netlify deploy --dir=...`
- 要正式發布：`netlify deploy --dir=... --prod`
