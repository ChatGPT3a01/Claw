# Quality checklist

這份 checklist 用來記錄 skill-creator-advanced 目前是否符合 `skill-creator-advanced` 的 readiness gate 規範。
本次 audit 以 `quick_validate.py`、`format_check.py`、`audit_skill_references.py`、`audit_unreferenced_files.py` 與 `SKILL.md` 結構掃描為基礎，並保留 skill 專屬檢核項。

## Final gate
- Audit date: 2026-03-30
- Compliance level: 高
- Overall status: PASS
- Automated checks:
  - [x] `quick_validate.py` passed
  - [x] `format_check.py` passed
  - [x] `audit_openclaw_frontmatter.py` passed
  - [x] `audit_skill_references.py` passed
  - [x] `audit_unreferenced_files.py` passed
- Key observations:
  - 新增 `references/skill-structure-patterns.md`，把 `Tool Wrapper`、`Generator`、`Reviewer`、`Inversion`、`Pipeline` 收斂成明確的 SKILL.md 結構選型框架。
  - 主 `SKILL.md` 現在要求先區分 `archetype` 與 `primary structure pattern`，避免還沒決定內容骨架就直接堆細節。
  - 新增跨工具可攜設計參考文件，並把 host matrix / tool gateway / thin wrapper 原則納入主流程與初始化骨架。
  - `audit_skill_references.py` 現在會同時掃 `SKILL.md` 與 `references/*.md`。
  - 新增 `audit_unreferenced_files.py`，可檢查 `scripts/`、`references/`、`assets/` 中未被文件參考的 orphan files。
  - 自動檢查全數通過。
- Structural gaps to keep improving:
  - 無明顯結構缺口。

## Format checks
- [x] skill folder 名稱符合 kebab-case
- [x] `SKILL.md` 存在且通過基本 frontmatter 驗證
- [x] `format_check.py` 為 0 errors / 0 warnings
- [x] `SKILL.md` 內提到的本地 `scripts/`、`references/`、`assets/` 路徑都存在
- [x] `scripts/`、`references/`、`assets/` 內沒有未解釋的未引用檔案
- [x] `references/quality_checklist.md` 已存在且已依本次 audit 更新
- [x] `SKILL.md` 中沒有待清理的 `TODO` / `[TODO]`

## Requirement and policy checks
- [x] `SKILL.md` 有明確 workflow / instructions
- [x] 有獨立 `role` 區塊或等價角色定義
- [x] 有獨立 decision boundary 區塊或等價使用邊界
- [x] 有明確 output contract / output shape 要求
- [x] 有明確 default follow-through policy / ask-first 邊界
- [x] 有工具或路由使用規則
- [x] 有 worked examples / examples 支撐輸出品質

## Common error checks
- [x] 沒有失效的本地引用路徑
- [x] 沒有未解釋的 orphan files 留在 `scripts/`、`references/`、`assets/`
- [x] frontmatter / 命名 / description 沒有被 validator 擋下
- [x] 結構與文字格式沒有被 linter 擋下
- [x] readiness gate 所期待的關鍵區塊已完整具備
- [x] checklist 已與新版 readiness gate 結構對齊

## Skill-specific checks
## Skill Readiness Checklist

在建立、改版、review 或發佈 skill 前，必須更新這份 checklist。
它不是附錄，而是目前這個 skill 是否達到可用狀態的單一檢核面板。

### 使用方式

1. 先跑格式與結構檢查，再回填結果。
2. 每個區塊至少寫出 `PASS`、`FAIL` 或 `BLOCKED`，不要只打勾不留證據。
3. 若有阻擋問題，先停止發佈或打包，再修正。

### 最終結論

- 檢查日期：
- 檢查版本：
- Overall status: `PASS` / `FAIL` / `BLOCKED`
- Blocking issues:
  - [ ] 無
  - [ ] 有，請列出：
- Evidence / commands run:
  - [ ] `python scripts/format_check.py <path/to/skill>`
  - [ ] `python scripts/quick_validate.py <path/to/skill>`
  - [ ] `python scripts/audit_openclaw_frontmatter.py`
  - [ ] `python scripts/audit_skill_references.py <path/to/skill>`
  - [ ] `python scripts/audit_unreferenced_files.py <path/to/skill>`

### 格式確認 (Format checks)

- [ ] skill folder 名稱符合 kebab-case
- [ ] `SKILL.md` 存在且為 UTF-8
- [ ] YAML frontmatter 結構正確，且包含 `name`、`description`
- [ ] frontmatter 沒有非法字元或保留欄位問題
- [ ] `references/quality_checklist.md` 已存在且已依本次修改更新
- [ ] `SKILL.md` 內提到的本地 `scripts/`、`references/`、`assets/` 路徑都存在
- [ ] `scripts/`、`references/`、`assets/` 沒有未解釋的未引用檔案
- [ ] 沒有把 `README.md` 放進 skill folder

### 要求與規範確認 (Requirement and policy checks)

- [ ] skill 只負責一個主要工作，邊界與 handoff 清楚
- [ ] description 有寫何時用、何時不用、成功輸出長什麼樣
- [ ] workflow 每一步都有 input / action / output / validation
- [ ] output contract 明確，不靠臨場自由發揮
- [ ] default follow-through policy 有寫清楚哪些可直接做、哪些必須先問
- [ ] 若 skill 依賴 tool / MCP / function calling，schema 與使用規則已檢查
- [ ] 若有 eval / benchmark，要確認 ROI 與 regression gates 合理

### 常見錯誤確認 (Common error checks)

- [ ] 沒有 release-blocking 的 `[TODO]` 或 placeholder 留在對外可見內容
- [ ] 沒有互相矛盾的規則散落在 `SKILL.md`、`references/`、`scripts/`
- [ ] 沒有把已失效或未使用的檔案留在 `scripts/`、`references/`、`assets/` 卻無合理保留理由
- [ ] 沒有把單次事故心得寫成無條件通用規則
- [ ] 沒有用過寬 description 去硬搶鄰近 skill 的 query
- [ ] 沒有把高風險副作用動作誤標成可直接執行
- [ ] 沒有擅自修改與本次問題無關的區域
