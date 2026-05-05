---
name: google-drive
description: >
  Google Drive 雲端硬碟完整操作技能（基於 rclone）。
  當使用者要求上傳檔案到 Google Drive、從雲端下載、
  列出雲端資料夾、同步本地與雲端、分享連結、
  搜尋雲端檔案、建立/刪除/移動雲端資料夾時，使用此技能。
  支援：上傳、下載、修改雲端檔案、讀取內容、列出、搜尋、同步、分享、建立資料夾、刪除、移動/重新命名。
  關鍵詞：Google Drive、雲端硬碟、rclone、上傳、下載、修改、編輯、讀取、同步、gdrive。
---

# Google Drive 雲端硬碟操作（rclone）

透過 rclone 操作 Google Drive，不需要自己建立 Google Cloud 專案或申請 OAuth 憑證。

## 原理

rclone 內建 Google OAuth 客戶端，首次使用時開啟瀏覽器讓使用者登入 Google 帳號授權，之後 token 自動儲存，不需重複認證。

---

## 前置檢查（每次使用前必做）

### 1. 確認 rclone 可用

```bash
# 檢查 rclone 是否已安裝
RCLONE=""
if command -v rclone &>/dev/null; then
  RCLONE="rclone"
elif [ -f "/tmp/rclone_extracted/rclone-v1.73.2-windows-amd64/rclone.exe" ]; then
  RCLONE="/tmp/rclone_extracted/rclone-v1.73.2-windows-amd64/rclone.exe"
fi

if [ -z "$RCLONE" ]; then
  echo "rclone 未安裝，正在下載..."
  curl -L -o /tmp/rclone.zip "https://downloads.rclone.org/rclone-current-windows-amd64.zip"
  unzip -o /tmp/rclone.zip -d /tmp/rclone_extracted
  RCLONE=$(find /tmp/rclone_extracted -name "rclone.exe" | head -1)
fi

$RCLONE version | head -1
```

### 2. 確認 Google Drive 已認證

```bash
# 檢查是否已有 gdrive 設定
$RCLONE listremotes 2>/dev/null | grep -q "gdrive:" && echo "已認證" || echo "需要認證"
```

### 3. 首次認證（僅需一次）

如果尚未認證，執行以下流程：

```bash
# Step 1: 取得 token（會開啟瀏覽器）
$RCLONE authorize "drive"
# 使用者在瀏覽器登入 Google 帳號並授權
# rclone 會輸出一段 JSON token

# Step 2: 用取得的 token 建立設定（將 <TOKEN_JSON> 替換為上一步的輸出）
$RCLONE config create gdrive drive token '<TOKEN_JSON>' config_refresh_token false config_change_team_drive false --non-interactive
```

驗證設定：
```bash
$RCLONE about gdrive: 2>&1 | head -5
```

---

## 操作指令

以下所有指令中的 `$RCLONE` 指 rclone 執行檔路徑。
遠端名稱統一使用 `gdrive:`。

### 列出檔案與資料夾

```bash
# 列出根目錄的資料夾
$RCLONE lsd gdrive:

# 列出指定資料夾內容（檔案＋子資料夾）
$RCLONE ls "gdrive:資料夾名稱/"

# 列出資料夾（僅子資料夾）
$RCLONE lsd "gdrive:資料夾名稱/"

# 透過資料夾 ID 列出（適用於分享連結中的 ID）
$RCLONE lsd gdrive: --drive-root-folder-id "FOLDER_ID"

# 列出所有檔案（遞迴）
$RCLONE ls "gdrive:資料夾名稱/" --max-depth 2

# 只列出特定類型
$RCLONE ls "gdrive:資料夾名稱/" --include "*.docx"
```

### 上傳

```bash
# 上傳單一檔案到根目錄
$RCLONE copy "/local/path/file.docx" "gdrive:目標資料夾/" --progress

# 上傳整個資料夾（保留結構）
$RCLONE copy "/local/path/整個資料夾/" "gdrive:目標資料夾/" --progress

# 上傳到指定資料夾 ID（從分享連結取得）
$RCLONE copy "/local/path/" gdrive: --drive-root-folder-id "FOLDER_ID" --progress

# 批次上傳（多執行緒加速）
$RCLONE copy "/local/path/" "gdrive:目標/" --progress --transfers 8 --checkers 16

# 上傳並排除特定檔案
$RCLONE copy "/local/path/" "gdrive:目標/" --exclude "*.md" --exclude "node_modules/**" --progress
```

### 下載

```bash
# 下載單一檔案
$RCLONE copy "gdrive:資料夾/檔案.docx" "/local/path/" --progress

# 下載整個資料夾
$RCLONE copy "gdrive:雲端資料夾/" "/local/download/" --progress

# 從資料夾 ID 下載
$RCLONE copy gdrive: "/local/download/" --drive-root-folder-id "FOLDER_ID" --progress

# 下載特定類型
$RCLONE copy "gdrive:資料夾/" "/local/" --include "*.pdf" --progress
```

### 同步（雙向/單向）

```bash
# 單向同步：本地 → 雲端（雲端會與本地完全一致，多餘檔案會被刪除）
$RCLONE sync "/local/path/" "gdrive:目標/" --progress

# 單向同步：雲端 → 本地
$RCLONE sync "gdrive:資料夾/" "/local/path/" --progress

# 安全同步（先預覽不執行）
$RCLONE sync "/local/path/" "gdrive:目標/" --dry-run

# 雙向同步（bisync，實驗性功能）
$RCLONE bisync "/local/path/" "gdrive:目標/" --resync
```

**注意**：`sync` 會刪除目標端多餘的檔案！不確定時先用 `--dry-run` 預覽。
如果只想「新增不刪除」，使用 `copy` 而非 `sync`。

### 建立資料夾

```bash
# 建立資料夾
$RCLONE mkdir "gdrive:新資料夾名稱"

# 建立巢狀資料夾
$RCLONE mkdir "gdrive:父資料夾/子資料夾/孫資料夾"
```

### 移動與重新命名

```bash
# 移動檔案
$RCLONE moveto "gdrive:舊路徑/file.docx" "gdrive:新路徑/file.docx"

# 重新命名（同資料夾內移動）
$RCLONE moveto "gdrive:資料夾/舊名稱.docx" "gdrive:資料夾/新名稱.docx"

# 移動整個資料夾
$RCLONE move "gdrive:舊資料夾/" "gdrive:新位置/新名稱/" --progress
```

### 刪除

```bash
# 刪除單一檔案
$RCLONE deletefile "gdrive:路徑/檔案.docx"

# 刪除資料夾內所有檔案（保留資料夾結構）
$RCLONE delete "gdrive:資料夾/" --progress

# 完全刪除資料夾（含結構）
$RCLONE purge "gdrive:資料夾/"

# 安全刪除（先預覽）
$RCLONE delete "gdrive:資料夾/" --dry-run
```

### 搜尋

```bash
# 搜尋檔名包含關鍵字的檔案
$RCLONE ls gdrive: --include "*關鍵字*"

# 搜尋特定類型
$RCLONE ls gdrive: --include "*.pdf" --max-depth 3

# 搜尋特定資料夾下
$RCLONE ls "gdrive:專案/" --include "*報告*"
```

### 取得檔案資訊

```bash
# 查看雲端容量
$RCLONE about gdrive:

# 查看檔案大小統計
$RCLONE size "gdrive:資料夾/"

# 查看檔案詳細資訊（含修改時間）
$RCLONE lsl "gdrive:資料夾/"
```

### 讀取雲端檔案內容

rclone 可以直接將雲端檔案串流到本地工具，不需先下載整個檔案。

```bash
# 直接讀取文字檔內容（cat 雲端檔案）
$RCLONE cat "gdrive:路徑/README.md"

# 讀取前 100 行
$RCLONE cat "gdrive:路徑/大檔案.txt" | head -100

# 讀取 Google Docs 為純文字
$RCLONE cat "gdrive:文件/會議紀錄" --drive-export-formats txt

# 讀取 Google Docs 為 Markdown（如支援）
$RCLONE cat "gdrive:文件/筆記" --drive-export-formats docx > /tmp/temp.docx
# 再用 pandoc 轉為可讀格式
pandoc /tmp/temp.docx -t markdown

# 讀取 CSV/JSON 等結構化資料
$RCLONE cat "gdrive:資料/data.csv" | head -20

# 查看檔案的詳細 metadata（大小、修改時間、MIME 類型）
$RCLONE lsjson "gdrive:路徑/檔案.docx"

# 查看整個資料夾的檔案清單（JSON 格式，含完整資訊）
$RCLONE lsjson "gdrive:資料夾/" --recursive
```

### 修改雲端檔案

rclone 不支援直接編輯雲端檔案。標準流程是：**下載 → 本地修改 → 覆蓋回傳**。

#### 流程 A：修改單一檔案（覆蓋更新）

```bash
# Step 1: 下載到暫存目錄
$RCLONE copy "gdrive:專案/報告.docx" "/tmp/edit/" --progress

# Step 2: 用本地工具修改（Claude Code 可直接操作）
# 例如：用 Edit 工具修改文字檔、用 pandoc 修改 docx 等

# Step 3: 修改完成後覆蓋回傳（copyto = 精確覆蓋單一檔案）
$RCLONE copyto "/tmp/edit/報告.docx" "gdrive:專案/報告.docx" --progress
```

#### 流程 B：批次修改多個檔案

```bash
# Step 1: 下載整個資料夾
$RCLONE copy "gdrive:專案資料/" "/tmp/batch_edit/" --progress

# Step 2: 本地批次修改（sed、python、Node.js 等）

# Step 3: 只回傳有修改的檔案（--update 只傳比雲端新的）
$RCLONE copy "/tmp/batch_edit/" "gdrive:專案資料/" --update --progress

# 或完全同步（雲端與本地完全一致）
$RCLONE sync "/tmp/batch_edit/" "gdrive:專案資料/" --progress
```

#### 流程 C：修改 Google Docs / Sheets / Slides（原生格式）

```bash
# Google 原生格式不能直接編輯，需轉為 Office 格式處理

# Step 1: 下載為 Office 格式
$RCLONE copy "gdrive:文件/企劃書" "/tmp/edit/" --drive-export-formats docx --progress

# Step 2: 本地修改 .docx 檔案

# Step 3: 上傳回去（會建立新檔案，不會覆蓋原 Google Docs）
$RCLONE copy "/tmp/edit/" "gdrive:文件/" --progress
# 注意：上傳 .docx 會是獨立的 Office 檔案，不會變回 Google Docs

# 若需要轉回 Google Docs 格式：
$RCLONE copy "/tmp/edit/" "gdrive:文件/" --drive-import-formats docx --progress
```

#### 流程 D：替換檔案（新版本覆蓋舊版本）

```bash
# 用本地新版本直接覆蓋雲端舊版本
$RCLONE copyto "/local/v2/報告_最終版.docx" "gdrive:專案/報告.docx" --progress

# 覆蓋前先備份舊版本
$RCLONE copyto "gdrive:專案/報告.docx" "gdrive:專案/備份/報告_舊版.docx"
$RCLONE copyto "/local/v2/報告.docx" "gdrive:專案/報告.docx" --progress
```

#### 流程 E：修改檔案 metadata（名稱、位置）

```bash
# 重新命名檔案
$RCLONE moveto "gdrive:路徑/舊名稱.docx" "gdrive:路徑/新名稱.docx"

# 移動到其他資料夾（等同剪下貼上）
$RCLONE moveto "gdrive:舊資料夾/檔案.docx" "gdrive:新資料夾/檔案.docx"

# 重新命名資料夾
$RCLONE move "gdrive:舊資料夾名/" "gdrive:新資料夾名/" --progress
```

### 分享連結

```bash
# 取得檔案的分享連結
$RCLONE link "gdrive:路徑/檔案.docx"

# 取得資料夾的分享連結
$RCLONE link "gdrive:資料夾/"
```

---

## 從 Google Drive 連結取得資料夾 ID

當使用者提供 Google Drive 連結時，從 URL 擷取資料夾 ID：

| 連結格式 | ID 位置 |
|---------|--------|
| `https://drive.google.com/drive/folders/XXXXX` | `XXXXX` 就是 ID |
| `https://drive.google.com/drive/folders/XXXXX?usp=sharing` | `XXXXX` 就是 ID |
| `https://drive.google.com/file/d/XXXXX/view` | `XXXXX` 就是檔案 ID |

取得 ID 後用 `--drive-root-folder-id "XXXXX"` 操作該資料夾。

---

## 常用組合範例

### 範例 1：上傳專案到指定 Google Drive 資料夾

```bash
# 從連結取得 ID: https://drive.google.com/drive/folders/1abc123
FOLDER_ID="1abc123"

# 上傳（排除不需要的檔案）
$RCLONE copy "/local/project/" gdrive: \
  --drive-root-folder-id "$FOLDER_ID" \
  --exclude "node_modules/**" \
  --exclude ".git/**" \
  --exclude "*.tmp" \
  --progress --transfers 4
```

### 範例 2：定期備份到雲端

```bash
# 只上傳新增/修改的檔案（不刪除雲端多餘檔案）
$RCLONE copy "/local/backup/" "gdrive:備份/2026-03-09/" --progress --update
```

### 範例 3：下載雲端資料夾到本地

```bash
$RCLONE copy gdrive: "/tmp/download/" \
  --drive-root-folder-id "FOLDER_ID" \
  --progress
```

### 範例 4：修改雲端上的某個檔案再傳回去

```bash
# 完整流程：讀取 → 修改 → 回傳
RCLONE="/tmp/rclone_extracted/rclone-v1.73.2-windows-amd64/rclone.exe"

# 1. 下載
$RCLONE copy "gdrive:專案/config.json" "/tmp/edit/"

# 2. 修改（用 Claude Code 的 Edit 工具直接改 /tmp/edit/config.json）

# 3. 覆蓋回傳
$RCLONE copyto "/tmp/edit/config.json" "gdrive:專案/config.json"
echo "雲端檔案已更新"
```

### 範例 5：讀取雲端文字檔內容（不下載）

```bash
# 直接 cat 雲端檔案
$RCLONE cat "gdrive:筆記/TODO.md"

# 搜尋雲端 CSV 中的特定內容
$RCLONE cat "gdrive:資料/students.csv" | grep "王小明"
```

### 範例 6：批次更新雲端資料夾中的所有 Word 檔

```bash
# 下載所有 docx
$RCLONE copy "gdrive:書籍/" "/tmp/books/" --include "*.docx" --progress

# 本地批次處理（例如修改頁首、轉換格式等）

# 只回傳修改過的檔案
$RCLONE copy "/tmp/books/" "gdrive:書籍/" --update --include "*.docx" --progress
```

---

## 進階設定

### 多帳號支援

```bash
# 建立第二個 Google 帳號
$RCLONE authorize "drive"
# 用新 token 建立新的遠端名稱
$RCLONE config create gdrive2 drive token '<NEW_TOKEN>' config_refresh_token false config_change_team_drive false --non-interactive

# 跨帳號複製
$RCLONE copy "gdrive:來源/" "gdrive2:目標/" --progress
```

### 頻寬限制

```bash
# 限制上傳速度（避免佔滿頻寬）
$RCLONE copy "/local/" "gdrive:目標/" --bwlimit 1M --progress
```

### Google Docs 匯出格式

```bash
# 下載時將 Google Docs 轉為 docx
$RCLONE copy "gdrive:文件/" "/local/" --drive-export-formats docx,xlsx,pptx
```

---

## 注意事項

- **Token 有效期**：rclone 會自動使用 refresh_token 更新，通常不需重新認證
- **API 限制**：Google Drive API 有每日配額限制，大量操作時加 `--tpslimit 10` 限速
- **檔名限制**：Google Drive 不允許 `\ / : * ? " < > |` 等字元，rclone 會自動替換
- **大檔案**：>5GB 檔案會自動分段上傳
- **sync vs copy**：`sync` 會刪除目標多餘檔案，`copy` 只新增不刪除，不確定時用 `copy`
- **--dry-run**：任何危險操作前先加 `--dry-run` 預覽
- **設定檔位置**：Windows 為 `%APPDATA%\rclone\rclone.conf`

## 疑難排解

| 問題 | 解法 |
|------|------|
| `Failed to configure token` | 重新執行 `rclone authorize "drive"` |
| `quota exceeded` | 等待 24 小時或降低 `--tpslimit` |
| `file name not allowed` | 檔名含特殊字元，rclone 會自動處理 |
| `token expired` | rclone 通常自動更新，若失敗重新 `authorize` |
| 上傳很慢 | 增加 `--transfers 8 --checkers 16` |
| 要看中文資料夾 | 終端機需支援 UTF-8（Windows Terminal 預設支援） |
