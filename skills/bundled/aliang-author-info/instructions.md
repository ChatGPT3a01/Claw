# 阿亮老師作者資訊模板 Skill

這個 skill 用於在 GitHub 專案的 README.md 中自動套用阿亮老師的作者資訊、授權聲明和社群連結。

## 使用方式

當用戶說「套用作者資訊」、「加入作者模板」或「/aliang-author-info」時，執行此 skill。

## 作者資訊

### 基本資訊
- **姓名**：曾慶良 主任（阿亮老師）
- **作者照片路徑**：`D:\提示詞模板\作者資訊.png`（需複製到專案目錄）

### 現任職務
- 📌 新興科技推廣中心主任
- 📌 教育部學科中心研究教師
- 📌 臺北市資訊教育輔導員

### 獲獎紀錄
- 🏆 2025年 SETEAM教學專業講師認證
- 🏆 2024年 獲教育部人工智慧講師認證
- 🏆 2022、2023年 指導學生XR專題競賽獲特優
- 🏆 2022年 獲VR教材開發教師組特優
- 🏆 2019年 獲百大資訊人才獎
- 🏆 2018、2019年 蟬聯親子天下創新100教師
- 🏆 2018年 臺北市特殊優良教師
- 🏆 2017年 教育部行動學習優等

## 社群連結

- **Facebook 個人頁面**：https://www.facebook.com/?locale=zh_TW
- **YouTube 頻道**：https://www.youtube.com/@Liang-yt02
- **3A科技研究社（Facebook 社團）**：https://www.facebook.com/groups/2754139931432955
- **Email**：3a01chatgpt@gmail.com

## 授權聲明

```
© 2026 阿亮老師 版權所有

本專案僅供「阿亮老師課程學員」學習使用。

⚠️ 禁止事項：
- ❌ 禁止修改本專案內容
- ❌ 禁止轉傳或散布
- ❌ 禁止商業使用
- ❌ 禁止未經授權之任何形式使用

如有任何授權需求，請聯繫作者。
```

## README.md 模板格式

當用戶要求套用作者資訊時，在 README.md 中加入以下區塊：

### 1. 作者資訊區塊（美化版）

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

### 2. 授權聲明區塊

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

### 3. 頁尾區塊

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

## 執行步驟

當用戶調用此 skill 時：

1. **檢查是否需要複製作者照片**
   - 如果專案目錄中沒有 `作者資訊.png`，從 `D:\提示詞模板\作者資訊.png` 複製過來

2. **讀取現有 README.md**
   - 檢查是否已有作者資訊區塊
   - 如果已存在，詢問是否要更新

3. **插入作者資訊**
   - 在 README.md 中適當位置（通常在技術說明之後、致謝之前）插入作者資訊區塊
   - 插入授權聲明區塊
   - 在最後加入美化的頁尾區塊

4. **確認並提交**
   - 顯示預覽給用戶
   - 詢問是否需要 git commit
   - 如果需要，執行 `git add README.md 作者資訊.png && git commit -m "新增作者資訊和授權聲明"`

## 美化技巧

- 使用 `<div align="center">` 讓內容居中
- 使用表格排版讓資訊結構清晰
- 使用 shields.io 徽章按鈕讓社群連結更美觀
- 使用 emoji 讓內容更生動
- 適當使用 `<br>` 調整間距

## 注意事項

- 確保作者照片檔案不超過 GitHub 的檔案大小限制（建議 < 5MB）
- 社群連結應該使用最新的網址
- 年份（© 2026）應該根據當前年份自動調整
- 如果是私人專案，可以考慮簡化授權聲明
