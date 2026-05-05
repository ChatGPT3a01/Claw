#!/usr/bin/env node
/**
 * SHA-256 密碼雜湊產生工具
 * 用法：node hash-password.js "你的密碼"
 * 用法：node hash-password.js "密碼1" "密碼2" "密碼3"
 */
const crypto = require('crypto');

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('用法: node hash-password.js <password> [password2] ...');
  console.error('範例: node hash-password.js "@AISkill2026"');
  process.exit(1);
}

args.forEach(pw => {
  const hash = crypto.createHash('sha256').update(pw).digest('hex');
  console.log(`${pw}  →  ${hash}`);
});
