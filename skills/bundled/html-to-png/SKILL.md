---
name: html-to-png
description: >
  [已整併] 此技能已併入 markitdown 萬能轉換器。
  請改用 markitdown skill（方向 3：HTML→PNG）。
deprecated: true
redirect: markitdown
---

# HTML 轉 PNG 截圖（已整併至 markitdown）

> **此技能已整併至 `markitdown` skill。**
> 請改用 `markitdown`（方向 3：HTML→PNG）。
>
> 快速替代：`python convert.py --input page.html --direction html-to-png`

---

以下為舊版內容（僅供參考）：

# HTML 轉 PNG 截圖工具（舊版）

將 .html 檔案透過無頭瀏覽器渲染後截圖，產出 .png 圖片。

## 前置檢查

1. 確認 Node.js 已安裝：
   ```bash
   node --version
   ```
   需要 Node.js 18+

2. 確認 puppeteer 已安裝。如果目標資料夾沒有 node_modules/puppeteer，先安裝：
   ```bash
   cd <目標資料夾>
   npm install puppeteer
   ```

## 使用方式

### 方式 A：使用現有轉換腳本

如果目標資料夾已有 `html_to_png.js`，直接執行：

```bash
# 轉換所有（跳過已有 PNG 的）
node html_to_png.js

# 強制全部重新轉換
node html_to_png.js --force

# 只轉特定章節
node html_to_png.js --chapter CH13
```

### 方式 B：單檔快速轉換

對於單一檔案，使用以下 Node.js 內聯腳本：

```bash
node -e "
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });
  const htmlPath = process.argv[1].replace(/\\\\/g, '/');
  const pngPath = htmlPath.replace(/\\.html$/, '.png');
  await page.goto('file:///' + htmlPath, { waitUntil: 'networkidle0', timeout: 15000 });
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: pngPath, fullPage: true, type: 'png' });
  console.log('✅ 完成：' + pngPath);
  await browser.close();
})();
" "<HTML檔案的完整路徑>"
```

### 方式 C：批次轉換（無現有腳本時）

如果目標資料夾沒有 `html_to_png.js`，建立一個：

```javascript
// html_to_png.js — 完整腳本
const fs = require('fs');
const path = require('path');
const BASE_DIR = __dirname;

function findHtmlFiles(dir) {
  let results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === 'node_modules') continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results = results.concat(findHtmlFiles(fullPath));
    } else if (entry.name.endsWith('.html')) {
      results.push(fullPath);
    }
  }
  return results.sort();
}

async function main() {
  const args = process.argv.slice(2);
  const force = args.includes('--force');
  let chapter = null;
  const chIdx = args.indexOf('--chapter');
  if (chIdx !== -1 && args[chIdx + 1]) chapter = args[chIdx + 1].toUpperCase();

  console.log('🖼️  HTML → PNG 批次轉換工具\n');

  let htmlFiles = findHtmlFiles(BASE_DIR);
  if (chapter) {
    htmlFiles = htmlFiles.filter(f => path.basename(path.dirname(f)).toUpperCase().includes(chapter));
  }

  const toConvert = [];
  let skipped = 0;
  for (const f of htmlFiles) {
    const png = f.replace(/\.html$/, '.png');
    if (fs.existsSync(png) && !force) skipped++;
    else toConvert.push(f);
  }

  console.log(`HTML 總數：${htmlFiles.length}｜跳過：${skipped}｜需轉換：${toConvert.length}\n`);
  if (toConvert.length === 0) { console.log('✅ 全部已完成！'); return; }

  const puppeteer = require('puppeteer');
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });

  let ok = 0, fail = 0;
  for (let i = 0; i < toConvert.length; i++) {
    const f = toConvert[i];
    const png = f.replace(/\.html$/, '.png');
    const rel = path.relative(BASE_DIR, f);
    process.stdout.write(`[${i+1}/${toConvert.length}] ${rel}`);
    try {
      await page.goto('file:///' + f.replace(/\\/g, '/'), { waitUntil: 'networkidle0', timeout: 15000 });
      await new Promise(r => setTimeout(r, 1500));
      await page.screenshot({ path: png, fullPage: true, type: 'png' });
      const kb = (fs.statSync(png).size / 1024).toFixed(0);
      console.log(` ✅ (${kb} KB)`);
      ok++;
    } catch (e) { console.log(` ❌ ${e.message}`); fail++; }
  }

  await browser.close();
  console.log(`\n🎉 完成！成功 ${ok}，失敗 ${fail}`);
}

main().catch(e => { console.error(e); process.exit(1); });
```

## 注意事項

- 轉換前確保 HTML 檔案能在瀏覽器中正常顯示
- 預設 viewport 寬度 1280px，可視需求調整
- 網路字型（Google Fonts）需要網路連線才能正確渲染
- `node_modules` 資料夾會自動跳過，不會誤轉
- 已有同名 .png 的會自動跳過，加 `--force` 強制重轉
- 產出的 PNG 為全頁截圖（fullPage），高度依內容自動調整

## 常見問題

| 問題 | 解法 |
|------|------|
| puppeteer 安裝失敗 | 確保 Node.js 18+，嘗試 `npm install puppeteer --ignore-scripts` 再 `npx puppeteer browsers install chrome` |
| 字型顯示方塊 | HTML 使用了本地字型，改用 Google Fonts 或確保系統有安裝該字型 |
| 截圖空白 | 檢查 HTML 的 file:// 路徑是否正確，Windows 路徑需轉為正斜線 |
| 圖片太大 | 調整 viewport 寬度或使用 `clip` 參數裁切特定區域 |
