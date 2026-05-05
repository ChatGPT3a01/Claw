#!/usr/bin/env node
/**
 * 自動為靜態 HTML 檔案注入 SHA-256 密碼閘門
 *
 * 用法:
 *   node add-password-gate.js <target.html> [options]
 *
 * 選項:
 *   --user-password <pw>     使用者密碼（必填）
 *   --admin-password <pw>    管理員密碼（必填）
 *   --title <text>           閘門標題（預設: 密碼保護）
 *   --subtitle <text>        閘門副標題（預設: 請輸入密碼以進入）
 *   --emoji <emoji>          閘門圖示（預設: ⚡）
 *   --btn-text <text>        按鈕文字（預設: 驗證並進入）
 *   --gradient <c1,c2>       按鈕漸層色（預設: #667eea,#764ba2）
 *   --storage-key <key>      localStorage key（預設: site_pw_hashes）
 *   --session-key <key>      sessionStorage key（預設: site_authed）
 *   --disclaimer <text>      免責聲明
 *   --dry-run                只印出結果，不寫入檔案
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// --- Parse args ---
const args = process.argv.slice(2);
const targetFile = args.find(a => !a.startsWith('--'));

if (!targetFile) {
  console.error('錯誤：請指定目標 HTML 檔案');
  process.exit(1);
}

function getArg(name, def) {
  const i = args.indexOf('--' + name);
  return i !== -1 && args[i + 1] ? args[i + 1] : def;
}

const hasFlag = (name) => args.includes('--' + name);

const userPw     = getArg('user-password', '');
const adminPw    = getArg('admin-password', '');
const title      = getArg('title', '密碼保護');
const subtitle   = getArg('subtitle', '請輸入密碼以進入');
const emoji      = getArg('emoji', '⚡');
const btnText    = getArg('btn-text', '驗證並進入');
const gradient   = getArg('gradient', '#667eea,#764ba2');
const storageKey = getArg('storage-key', 'site_pw_hashes');
const sessionKey = getArg('session-key', 'site_authed');
const disclaimer = getArg('disclaimer', '本機制僅為閱讀阻擋，非安全保護措施');
const dryRun     = hasFlag('dry-run');

if (!userPw || !adminPw) {
  console.error('錯誤：--user-password 和 --admin-password 為必填');
  process.exit(1);
}

// --- SHA-256 ---
function sha256(str) {
  return crypto.createHash('sha256').update(str).digest('hex');
}

const adminHash   = sha256(adminPw);
const defaultHash = sha256(userPw);
const [g1, g2]    = gradient.split(',').map(s => s.trim());

console.log(`管理員密碼雜湊: ${adminHash}`);
console.log(`使用者密碼雜湊: ${defaultHash}`);

// --- Read target ---
const filePath = path.resolve(targetFile);
if (!fs.existsSync(filePath)) {
  console.error(`錯誤：檔案不存在 ${filePath}`);
  process.exit(1);
}

let html = fs.readFileSync(filePath, 'utf8');

// --- Idempotent check ---
if (html.includes('id="passwordGate"') || html.includes('id="pwOverlay"')) {
  console.log(`跳過：${filePath} 已有密碼閘門`);
  process.exit(0);
}

// --- Load templates ---
const skillDir = path.join(__dirname, '..');
const tplHtml  = fs.readFileSync(path.join(skillDir, 'assets', 'password-gate.html'), 'utf8');
const tplCss   = fs.readFileSync(path.join(skillDir, 'assets', 'password-gate.css'), 'utf8');
const tplJs    = fs.readFileSync(path.join(skillDir, 'assets', 'password-gate.js'), 'utf8');

// --- Replace placeholders in HTML template ---
let gateHtml = tplHtml
  .replace(/__EMOJI__/g, emoji)
  .replace(/__TITLE__/g, title)
  .replace(/__SUBTITLE__/g, subtitle)
  .replace(/__DISCLAIMER__/g, disclaimer)
  .replace(/__BTN_TEXT__/g, btnText);

// --- Replace placeholders in CSS ---
let gateCss = tplCss
  .replace(/__GRADIENT_1__/g, g1)
  .replace(/__GRADIENT_2__/g, g2)
  .replace(/__GRADIENT_1_33__/g, g1 + '33')
  .replace(/__GRADIENT_1_40__/g, g1 + '40')
  .replace(/__GRADIENT_1_50__/g, g1 + '50');

// --- Replace placeholders in JS ---
let gateJs = tplJs
  .replace(/__ADMIN_HASH__/g, adminHash)
  .replace(/__DEFAULT_HASH__/g, defaultHash)
  .replace(/__HASH_STORAGE_KEY__/g, storageKey)
  .replace(/__SESSION_KEY__/g, sessionKey);

// --- Inject CSS into <head> ---
const cssBlock = `\n<style>\n${gateCss}\n</style>\n`;
if (html.includes('</head>')) {
  html = html.replace('</head>', cssBlock + '</head>');
} else {
  html = cssBlock + html;
}

// --- Inject HTML after <body> ---
if (html.includes('<body>')) {
  html = html.replace('<body>', '<body>\n' + gateHtml);
} else if (html.match(/<body[^>]*>/)) {
  html = html.replace(/<body[^>]*>/, match => match + '\n' + gateHtml);
} else {
  html = gateHtml + html;
}

// --- Inject JS before </body> ---
const jsBlock = `\n<script>\n${gateJs}\n</script>\n`;
if (html.includes('</body>')) {
  html = html.replace('</body>', jsBlock + '</body>');
} else {
  html = html + jsBlock;
}

// --- Output ---
if (dryRun) {
  console.log('\n--- DRY RUN (不寫入檔案) ---\n');
  console.log(html.substring(0, 2000) + '\n...(截斷)');
} else {
  fs.writeFileSync(filePath, html, 'utf8');
  console.log(`✅ 密碼閘門已注入: ${filePath}`);
}
