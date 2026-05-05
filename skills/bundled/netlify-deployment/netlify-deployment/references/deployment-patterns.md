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

## 2. Build 後部署

1. 確認框架
2. 確認 build command
3. 確認 publish 目錄
4. 本地執行 build
5. 部署 preview
6. 確認後再部署 production

## 3. 連結既有站

```bash
netlify link --id <site-id>
netlify deploy --dir=dist --prod
```

## 4. Preview 優先

```bash
netlify deploy --dir=dist
```

## 5. Production 直推

```bash
netlify deploy --dir=dist --prod
```
