---
name: readme-beautification
description: GitHub README 美化和設計規範。包含 badge 徽章、表格排版、Emoji 使用指南、顏色代碼、作者資訊區塊、授權聲明等。用於美化和規範化 GitHub 專案的 README.md 檔案。使用時機：(1) 創建新的 GitHub 專案 README，(2) 升級現有 README 外觀，(3) 套用專業設計風格，(4) 添加 badge、表格、作者資訊，(5) 要求「美化 README」或「設計 README」。關鍵詞：README、美化、設計、GitHub、badge、徽章、表格、排版、風格、Emoji、作者。
---

# README 美化與設計

專業的 GitHub README 設計規範和美化指南。

## 概述

創建一份精美的 README 是展現專案的第一步。這個 skill 提供完整的設計系統，讓你的 GitHub 專案看起來專業、清晰且吸引人。

## 必備設計元素

### 1. 頂部區塊（置中對齊）

README 的第一眼非常重要。使用置中區塊加上 emoji 和 badge：

```markdown
<div align="center">

# 📊 專案標題（加上相關 Emoji）

### 副標題簡短說明

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-線上簡報-blue?style=for-the-badge&logo=github)](網址)
[![License](https://img.shields.io/badge/授權-阿亮老師課程專用-red?style=for-the-badge)](LICENSE)

</div>
```

**關鍵點：**
- 使用 `<div align="center">` 置中內容
- 加上相關的 emoji（📊、📈、📋 等）
- 添加 badge 顯示重要連結和授權

### 2. Badge 徽章系統

**必備徽章：**
- GitHub Pages 連結（藍色）
- 授權聲明（紅色）

**技術標籤（依專案內容）：**

```markdown
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white)
```

**Badge 產生工具：** [shields.io](https://shields.io)

### 3. 課程/功能內容（表格排版）

使用 HTML 表格展示多欄內容，搭配 Emoji 圖示：

```markdown
<table>
<tr>
<td width="50%">

### 🔰 基礎篇

- 📌 HTML 基礎
- 📌 CSS 入門
- 📌 JavaScript 初階

</td>
<td width="50%">

### 🚀 進階篇

- ⚡ 框架應用
- ⚡ 效能優化
- ⚡ 部署上線

</td>
</tr>
</table>
```

**優點：**
- 兩欄排版更清晰
- 易於掃讀
- 視覺上更平衡

### 4. 工具/資源連結

使用置中表格展示工具資源：

```markdown
| 工具 | 說明 | 連結 |
|:---:|:---|:---:|
| 📝 **工具名** | 簡短說明 | [前往官網 →](網址) |
| 🔧 **工具二** | 功能介紹 | [開始使用 →](網址) |
```

**格式說明：**
- 第一欄：`:---:` 置中對齊（emoji + 工具名）
- 第二欄：`:---` 左對齊（說明文字）
- 第三欄：`:---:` 置中對齊（連結按鈕）

### 5. 快速選擇指南

使用 code block 繪製文字流程圖，幫助用戶快速選擇：

```markdown
\`\`\`
你的主要需求是什麼？
│
├─► 需求 A ──────► 工具 A
│
├─► 需求 B ──────► 工具 B
│
└─► 需求 C ──────► 工具 C
\`\`\`
```

### 6. 作者資訊區塊

在 README 中適當位置添加作者資訊，使用社群按鈕徽章：

```markdown
## 👨‍🏫 關於作者

<div align="center">

### 曾慶良 主任（阿亮老師）

**📌 現任職務**
- 新興科技推廣中心主任
- 教育部學科中心研究教師

**📞 聯絡方式**

[![Facebook](https://img.shields.io/badge/Facebook-名稱-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](網址)
[![YouTube](https://img.shields.io/badge/YouTube-頻道名-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](網址)

</div>
```

**社群按鈕顏色：**
- Facebook: `1877F2`
- YouTube: `FF0000`
- Instagram: `E1306C`
- GitHub: `333333`
- Email: `EA4335`

### 7. 授權聲明

使用 code block 框起來，視覺突出：

```markdown
## 📜 授權聲明

\`\`\`
© 2026 阿亮老師 版權所有

本專案僅供「阿亮老師課程學員」學習使用。

⚠️ 禁止事項：
- ❌ 禁止修改本專案內容
- ❌ 禁止轉傳或散布
- ❌ 禁止商業使用
\`\`\`
```

### 8. 底部區塊（頁尾）

```markdown
---

<div align="center">

## 🌟 喜歡這個專案嗎？

如果這個工具對您有幫助，請給我們一個 ⭐ Star！

<br>

**Made with ❤️ by 阿亮老師**

<br>

[⬆️ 回到頂部](#專案標題)

---

© 2026 阿亮老師 版權所有

</div>
```

## 常用 Emoji 對照表

| 用途 | Emoji | 用途 | Emoji |
|-----|-------|-----|-------|
| 專案/簡報 | 📊 📈 📋 | 工具/設定 | 🔧 🛠️ ⚙️ |
| 基礎/入門 | 🔰 📌 | 設計/美術 | 🎨 ✨ 💎 |
| 進階/火箭 | 🚀 ⚡ | 警告/注意 | ⚠️ 🚫 ❌ |
| 作者/人物 | 👨‍🏫 👤 | 連結/指向 | 🔗 👉 → |
| 完成/確認 | ✅ ⭐ | 文檔/說明 | 📚 📖 📝 |

## 常用顏色代碼

| 用途 | 代碼 | 用途 | 代碼 |
|-----|------|-----|------|
| GitHub/藍 | `2088FF` | 成功/綠 | `28A745` |
| 授權/紅 | `FF4444` | 警告/橙 | `FD7E14` |
| Google | `4285F4` | Facebook | `1877F2` |
| YouTube | `FF0000` | Twitter | `1DA1F2` |

## 完整 README 結構

一份完整的 README 通常包含：

```
1. 頂部區塊（置中）
   ├─ 標題 + Emoji
   ├─ 副標題
   └─ Badge 徽章

2. 目錄或快速導航

3. 主要內容
   ├─ 簡介
   ├─ 功能介紹
   ├─ 課程/內容（可用表格）
   └─ 工具資源

4. 技術棧/需求

5. 安裝指南

6. 使用說明

7. 作者資訊

8. 授權聲明

9. 頁尾（置中）
```

## 美化技巧

### ✅ 應該做

- 善用 `<div align="center">` 置中重要區塊
- 使用分隔線 `---` 區分各區塊
- 適度使用 emoji，不要過量
- 表格使用 `:---:` 置中對齊，`:---` 左對齊
- 讓重要連結清晰可點
- 保持整體風格一致

### ❌ 不應該做

- 不要讓整個 README 都置中
- 不要濫用 emoji（每行都加會很亂）
- 不要使用過多不相關的顏色
- 不要讓連結失效或指向錯誤的地址
- 不要忘記測試所有連結

## 快速美化流程

1. **確定主題** - 決定 README 的風格（專業/創意/教育）
2. **設計頂部** - 添加標題、副標題、badge
3. **組織內容** - 用表格或分欄展示功能
4. **添加資源** - 連結到工具、文檔、外部資源
5. **加入作者** - 添加作者資訊和社群連結
6. **授權聲明** - 明確標註授權條款
7. **測試驗證** - 在 GitHub 上預覽，確認所有連結可用

## 參考資源

- **Badge 產生器**：[shields.io](https://shields.io)
- **Emoji 查詢**：[emoji-cheat-sheet.com](https://www.webfx.com/tools/emoji-cheat-sheet/)
- **Markdown 指南**：[markdownguide.org](https://www.markdownguide.org/)
- **GitHub Pages 指南**：[docs.github.com/pages](https://docs.github.com/en/pages)
