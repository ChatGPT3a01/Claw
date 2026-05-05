# Cross-tool portability

這份文件整理「同一個 skill 想在多個 host / agent 工具中重用」時的最低設計原則。重點不是追求到處都能跑，而是避免為了每個平台複製一份不同版本的 skill。

## 1) 先判斷值不值得做成跨工具 skill

適合：
- 同一套 workflow、output contract、tool policy 需要在多個 host 重用
- repo / CLI / IDE / agent app 之間只差包裝層，不差核心流程
- 需要共用同一組 tool contract、approval 邊界與測試矩陣

不適合：
- 主要價值綁死某一個平台獨有 API、hook 或 UI
- 每個 host 的輸入、步驟、驗收產物都明顯不同
- 其實只是想把同一主題的多個任務硬包成一個 skill

## 2) 預設架構：skill pack × tool gateway × host adapter

跨工具 skill 預設拆成三層：

1. `skill pack`
- `SKILL.md` + `references/` + `scripts/`
- 這裡放 decision boundary、workflow、output contract、tool policy、examples
- 目標是 host-agnostic，作為單一真實來源

2. `tool gateway`
- 統一承接 MCP、function calling、REST / OpenAPI 或其他外部能力
- 放 auth、timeout、retry、idempotency、approval 邊界與審計需求
- 不要把這些邏輯散落到每個 host 各自的 prompt

3. `host adapter`
- 各平台自己的 plugin / manifest / marketplace / config
- 只做薄包裝，不複製核心 skill 內容
- 必須明寫哪些 host 為 primary、哪些只是 best-effort support

預設順序：
1. 先把 `skill pack` 寫好
2. 再定義 `tool gateway` 契約
3. 最後才做 host wrappers

## 3) 工具契約怎麼選

預設優先順序：
- 先用保守 JSON Schema 定義輸入輸出
- 需要跨 host 共用工具時，優先考慮 MCP
- 需要企業治理、商務 API 或 Microsoft 365 類整合時，再補 OpenAPI

最低要求：
- function / tool 名稱可讀，不要用 `run_task`、`execute` 這種過度泛化命名
- 參數描述要具體，enum 與 required 欄位要寫清楚
- 錯誤分類、timeout、retry、approval 規則要一起設計
- active tool set 要盡量小，避免 host 之間因工具太多而選錯

## 4) 狀態、授權與 approval 要分層設計

不要把 skill folder 當資料庫。

必做：
- 快取、登入狀態、安裝產物、索引與其他可變資料寫到 workspace 或平台指定 data path
- 授權方式、token 來源、callback / login 流程在公開 surface 上講一致
- 對讀取型、寫入型、外部副作用型工具分級
- 刪除、發布、付款、寄信、寫正式環境等高風險動作必須有 approval gate

不要做：
- 在 wrapper 內藏一套額外的副作用規則，和 `SKILL.md` 不同步
- 把 timeout / retry 寫成每個 host 各自一套自然語言說法
- 讓終端使用者隨意掛上未知 skill / MCP server 後直接執行高風險動作

## 5) 支援矩陣要在設計期就寫清楚

至少列出：
- Primary hosts：正式支援與回歸測試的平台
- Secondary hosts：可以安裝，但只做 smoke test
- Unsupported hosts：目前明確不保證

每個 host 至少回答：
- skill pack 是否原樣重用
- 需要哪些 wrapper / manifest / config
- 工具 transport 是什麼
- auth / approval / persistence 怎麼做
- 哪些能力因平台限制被降級或停用

## 6) 測試矩陣

跨工具 skill 最少要測：
- `host × workflow`：同一個 use case 在不同 host 是否仍走對流程
- `host × routing`：同一 description / negative triggers 是否仍能正確觸發
- `host × non-functional`：auth、timeout、retry、approval、state path 是否一致

建議保留 artifacts：
- benchmark / grading 結果
- tool call 或 event trace
- 產物檔案與 timing
- host-specific regression gates

## 7) 發布與維護原則

- 用同一個核心 skill folder，外加多個薄 wrapper
- README、registry、marketplace、homepage、license、支援 host、權限與持久化敘事要一致
- 若某平台需要特化，先確認是 wrapper 特化還是代表 skill 已經失去 portability
- 當維護成本大於增益時，要直接縮回單平台 skill，而不是硬維持「名義上的跨工具」

## 8) 常見反模式

- 為每個平台複製一份不同的 `SKILL.md`
- 沒先定義 support matrix，直到發布前才開始補 wrapper
- tool schema、approval 邊界與公開文件彼此矛盾
- 把快取或登入狀態寫回 skill folder
- 把 MCP / API 超時與重試邏輯寫死在 prompt，而不是 gateway / tool 層
