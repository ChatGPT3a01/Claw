---
name: aliang-author-info
description: 阿亮老師（曾慶良主任）的作者資訊、職務、獲獎紀錄、聯絡方式、社群連結、授權聲明和專案簽名模板。用於在 GitHub 專案的 README.md 中自動套用阿亮老師的完整資訊。使用時機：(1) 創建或編輯 GitHub 專案 README，(2) 需要加入阿亮老師的作者資訊、(3) 需要套用授權聲明和版權聲明，(4) 要求「套用作者資訊」、「加入作者模板」、「加入聯絡方式」、「加入社群連結」、「加入授權聲明」。關鍵詞：作者資訊、作者、連結、聯絡、聯絡方式、社群、授權、版權、簽名、README。
---

# 阿亮老師作者資訊模板

在 GitHub 專案中快速套用阿亮老師的專業作者資訊、職務、獲獎紀錄和授權聲明。

## 概述

這個 skill 提供完整的作者資訊模板系統，包括：

- **作者資訊區塊** - 包含照片、職務、獲獎紀錄
- **授權聲明** - 專業的版權和使用限制聲明
- **社群連結** - 美化的 badge 按鈕連結
- **頁尾簽名** - 專案結尾的致謝和返回頂部按鈕

## 作者基本資訊

### 👨‍🏫 曾慶良 主任（阿亮老師）

**📌 現任職務**
- 新興科技推廣中心主任
- 教育部學科中心研究教師
- 臺北市資訊教育輔導員

**🏆 獲獎紀錄**
- 2025年 SETEAM教學專業講師認證
- 2024年 教育部人工智慧講師認證
- 2022、2023年 指導學生XR專題競賽特優
- 2022年 VR教材開發教師組特優
- 2019年 百大資訊人才獎
- 2018、2019年 親子天下創新100教師
- 2018年 臺北市特殊優良教師
- 2017年 教育部行動學習優等

**📞 聯絡方式**
- **YouTube**：https://www.youtube.com/@Liang-yt02
- **Facebook 社團**：https://www.facebook.com/groups/2754139931432955
- **Email**：3a01chatgpt@gmail.com

## 使用方法

### 1. 當用戶要求套用作者資訊時

執行此工作流程：

```
使用者: "在 README 中套用作者資訊"
    ↓
觸發此 skill
    ↓
自動在 README 中加入作者資訊、授權聲明和頁尾
```

### 2. 自動執行步驟

**步驟 1：檢查作者照片**
- 檢查專案目錄中是否有 `作者資訊.png`
- 如果沒有，從 `D:\提示詞模板\作者資訊.png` 複製

**步驟 2：讀取 README.md**
- 檢查是否已有作者資訊區塊
- 如果已存在，詢問是否要更新

**步驟 3：插入三個區塊**

#### A. 作者資訊區塊（美化版）

在 README 的技術說明之後、致謝之前插入：

```markdown
## 👨‍🏫 關於作者

<div align="center">

### 曾慶良 主任（阿亮老師）

<img src="作者資訊.png" width="600" alt="作者資訊">

<br>

<table>
<tr>
<td width="50%">

**📌 現任職務**

🎓 新興科技推廣中心主任<br>
🎓 教育部學科中心研究教師<br>
🎓 臺北市資訊教育輔導員

</td>
<td width="50%">

**🏆 獲獎紀錄**

🥇 2025年 SETEAM教學專業講師認證<br>
🥇 2024年 教育部人工智慧講師認證<br>
🥇 2022、2023年 指導學生XR專題競賽特優<br>
🥇 2022年 VR教材開發教師組特優<br>
🥇 2019年 百大資訊人才獎<br>
🥇 2018、2019年 親子天下創新100教師<br>
🥇 2018年 臺北市特殊優良教師<br>
🥇 2017年 教育部行動學習優等

</td>
</tr>
</table>

<br>

### 📞 聯絡方式

[![YouTube](https://img.shields.io/badge/YouTube-@Liang--yt02-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/@Liang-yt02)
[![Facebook](https://img.shields.io/badge/Facebook-3A科技研究社-blue?style=for-the-badge&logo=facebook)](https://www.facebook.com/groups/2754139931432955)
[![Email](https://img.shields.io/badge/Email-3a01chatgpt@gmail.com-green?style=for-the-badge&logo=gmail)](mailto:3a01chatgpt@gmail.com)

</div>
```

#### B. 授權聲明區塊

在作者資訊之後插入：

```markdown
## 📜 授權聲明

**© 2026 阿亮老師 版權所有**

本專案僅供「阿亮老師課程學員」學習使用。

### ⚠️ 禁止事項

- ❌ 禁止修改本專案內容
- ❌ 禁止轉傳或散布
- ❌ 禁止商業使用
- ❌ 禁止未經授權之任何形式使用

如有任何授權需求，請聯繫作者。
```

#### C. 頁尾簽名區塊

在 README 最後加入：

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

### 3. 確認並提交

- 顯示更新預覽給用戶
- 詢問是否需要提交到 git
- 如果是，執行：
  ```bash
  git add README.md 作者資訊.png
  git commit -m "新增作者資訊和授權聲明"
  ```

## 美化技巧

- 使用 `<div align="center">` 讓內容居中
- 使用表格排版讓資訊結構清晰
- 使用 [shields.io](https://shields.io) 徽章讓社群連結更美觀
- 使用 emoji 讓內容生動有趣
- 適當使用 `<br>` 調整間距

## 注意事項

- ✅ 作者照片應不超過 5MB（GitHub 限制）
- ✅ 社群連結保持最新網址
- ✅ 年份應根據當前年份自動調整
- ✅ 私人專案可簡化授權聲明
- ✅ 確保 README 中有「專案標題」anchor 供頁尾返回連結使用
