# 台灣學術論文來源完整指南

## 一、核心來源：NDLTD 臺灣博碩士論文知識加值系統

### 基本資訊
- **網址**：https://ndltd.ncl.edu.tw/
- **管理單位**：國家圖書館
- **涵蓋範圍**：1956 年至今，全台灣所有大學碩博士論文
- **總量**：約 150 萬+ 篇

### 存取方式

#### 方式 A：開放資料 CSV（推薦，零認證）
- **來源**：https://data.gov.tw/dataset/14024
- **URL 格式**：`https://ndltd.ncl.edu.tw/opendata/{民國年}ndltd.csv`
- **年份範圍**：民國 102-112 年（2013-2023）
- **欄位**：論文名稱、外文名稱、學校、系所、學年度、學位、作者、指導教授、永久連結
- **限制**：不含摘要、關鍵字

#### 方式 B：Handle System API
- **用途**：解析論文永久連結
- **API**：`GET https://hdl.handle.net/api/handles/11296/{short_code}`
- **Handle prefix**：11296（所有 NDLTD 論文共用）
- **解析鏈**：`hdl.handle.net/11296/xxx` → `ndltd.ncl.edu.tw/r/xxx` → 論文詳情頁

#### 方式 C：Web 搜尋（最完整，但有 CAPTCHA）
- **搜尋頁**：`https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/login?o=dwebmge`
- **搜尋欄位**：

| 代碼 | 欄位 | 說明 |
|------|------|------|
| `ti` | 論文名稱 | 中英文標題 |
| `au` | 研究生 | 作者姓名 |
| `ad` | 指導教授 | 指導教授姓名 |
| `say` | 口試委員 | 口試委員姓名 |
| `kw` | 關鍵字 | 論文關鍵字 |
| `ab` | 摘要 | 中英文摘要 |
| `rf` | 參考文獻 | 引用文獻 |
| `ALLFIELD` | 全欄位 | 搜尋所有欄位 |
| `id` | 系統編號 | 如 110NTHU5650010 |

- **論文系統 ID 格式**：`{民國年}{學校代碼}{系所代碼}{序號}`
- **注意**：有圖形 CAPTCHA，單一 Session 約 500 次查詢後被限制

### NDLTD 搜尋技巧
1. 使用精確匹配：`ti="深度學習"` 比 `ti=深度學習` 更準確
2. 組合搜尋：`kw="自然語言處理" AND ad="某教授"`
3. 年份限制：在進階搜尋中設定畢業學年度範圍
4. 全文下載：部分論文提供全文 PDF（依作者授權）

---

## 二、各大學機構典藏（OAI-PMH）

### 支援的大學端點

| 學校 | OAI-PMH 端點 | 系統 | 備註 |
|------|-------------|------|------|
| 臺灣大學 | `https://tdr.lib.ntu.edu.tw/oai/request` | DSpace | 最大，含全校論文 |
| 清華大學 | `https://etd.lib.nthu.edu.tw/oai/request` | DSpace | |
| 成功大學 | `https://etds.lib.ncku.edu.tw/oai/request` | DSpace | |
| 陽明交通大學 | `https://etd.lib.nycu.edu.tw/oai/request` | DSpace | 2021 合併後 |
| 政治大學 | `https://thesis.lib.nccu.edu.tw/oai/request` | DSpace | |
| 中央大學 | `https://ir.lib.ncu.edu.tw/oai/request` | DSpace | |
| 中山大學 | `https://etd.lib.nsysu.edu.tw/oai/request` | DSpace | |
| 臺灣師範大學 | `https://etds.lib.ntnu.edu.tw/oai/request` | DSpace | |

### OAI-PMH 常用查詢

```
# 列出所有可用的元資料格式
?verb=ListMetadataFormats

# 列出所有集合（Collection）
?verb=ListSets

# 列出記錄（Dublin Core 格式）
?verb=ListRecords&metadataPrefix=oai_dc

# 依日期範圍列出記錄
?verb=ListRecords&metadataPrefix=oai_dc&from=2024-01-01&until=2024-12-31

# 取得單筆記錄
?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:tdr.lib.ntu.edu.tw:123456789/12345
```

### Dublin Core 欄位對照

| DC 欄位 | 說明 | 對應 |
|---------|------|------|
| `dc:title` | 標題（可能多值：中文+英文） | title / title_en |
| `dc:creator` | 建立者（可能多值：作者+指導教授） | author / advisor |
| `dc:subject` | 主題/關鍵字 | keywords |
| `dc:description` | 描述/摘要 | abstract |
| `dc:date` | 日期 | year_ce |
| `dc:identifier` | 識別碼（URL/Handle/DOI） | url |
| `dc:type` | 類型（Thesis/Dissertation） | degree |
| `dc:language` | 語言 | — |

---

## 三、其他來源

### Crossref API
- **用途**：搜尋有 DOI 的台灣論文
- **台灣大學 DOI prefix**：`10.6342`
- **API**：`https://api.crossref.org/works?query={keyword}&filter=type:dissertation`
- **限制**：覆蓋率有限，許多 NDLTD 論文使用 Handle 而非 DOI

### Airiti Library（華藝線上圖書館）
- **網址**：https://www.airitilibrary.com/
- **說明**：台灣最大的中文學術全文資料庫，200 萬+ 篇
- **限制**：需付費訂閱，無公開 API
- **替代**：透過學校圖書館 VPN 存取

### GRB 政府研究資訊系統
- **網址**：https://www.grb.gov.tw/
- **說明**：科技部（現國科會）補助研究計畫成果
- **用途**：搜尋研究計畫而非學位論文
- **限制**：需手動查詢，無公開 API

### TCI-HSS（台灣人文及社會科學引文索引）
- **網址**：https://tci.ncl.edu.tw/
- **說明**：台灣人文社會科學期刊引文索引
- **限制**：無公開 API，網頁查詢

### NBINet（全國圖書書目資訊網）
- **開放資料**：https://data.gov.tw/dataset/7502
- **說明**：全國圖書館聯合目錄，含部分學位論文
- **格式**：MARC21 / XML

---

## 四、民國年/西元年對照表

| 民國年 | 西元年 | | 民國年 | 西元年 |
|--------|--------|-|--------|--------|
| 100 | 2011 | | 108 | 2019 |
| 101 | 2012 | | 109 | 2020 |
| 102 | 2013 | | 110 | 2021 |
| 103 | 2014 | | 111 | 2022 |
| 104 | 2015 | | 112 | 2023 |
| 105 | 2016 | | 113 | 2024 |
| 106 | 2017 | | 114 | 2025 |
| 107 | 2018 | | 115 | 2026 |

**公式**：西元年 = 民國年 + 1911

---

## 五、搜尋策略建議

### 中文關鍵字選擇
1. 使用學術術語而非口語（如「深度學習」而非「AI 學習」）
2. 嘗試不同同義詞（如「自然語言處理」/「自然語言理解」/「NLP」）
3. 繁體/簡體都試（NDLTD 以繁體為主，但部分論文含簡體內容）

### 多來源交叉比對
```
關鍵字："教育科技"
├── NDLTD 開放資料：搜尋標題
├── NDLTD Web：搜尋標題+摘要+關鍵字
├── 台大 OAI-PMH：搜尋 dc:subject
├── Crossref：搜尋 "educational technology" + Taiwan
└── 合併去重 → 依年份排序 → 輸出報告
```

### 學校代碼速查（常用）
| 代碼 | 學校 | 代碼 | 學校 |
|------|------|------|------|
| NTU | 臺灣大學 | NTHU | 清華大學 |
| NCKU | 成功大學 | NYCU | 陽明交通大學 |
| NCCU | 政治大學 | NCU | 中央大學 |
| NSYSU | 中山大學 | NTNU | 臺灣師範大學 |
| NTUST | 臺灣科技大學 | NTUT | 臺北科技大學 |
