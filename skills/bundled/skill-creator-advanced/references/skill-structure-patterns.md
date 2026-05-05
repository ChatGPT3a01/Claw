# Skill Structure Patterns

這份文件補的是「SKILL.md 內容結構該怎麼選」，不是 skill 在整個組合中的角色分類。

請先分清兩個維度：
- `archetype`：這個 skill 在 portfolio 裡扮演什麼角色，例如 `router`、`executor`、`ops`、`utility`
- `structure pattern`：這份 `SKILL.md` 應該用什麼內容骨架，才能讓模型穩定執行

兩者不是二選一，而是正交維度。

## 1) 先決定 pattern，再展開細節

如果你已經知道：
- 主要工作是什麼
- 使用者會怎麼觸發
- 成功輸出長什麼樣

下一步不是立刻堆更多規則，而是先判斷這個 skill 比較接近哪一種結構 pattern。

常用的五種：
- Tool Wrapper
- Generator
- Reviewer
- Inversion
- Pipeline

## 2) 快速選型

用這個順序判斷：

1. 如果主要價值是教模型遵守某個 library、framework、內部系統或治理規範，先看 `Tool Wrapper`
2. 如果主要價值是穩定產出固定格式文件、設定檔或範本化內容，先看 `Generator`
3. 如果主要價值是依 checklist / rubric / 標準去評估既有內容，先看 `Reviewer`
4. 如果沒有先蒐集關鍵上下文就不能安全開工，先看 `Inversion`
5. 如果流程有明確依賴順序、不能跳步、而且中間需要 gate，先看 `Pipeline`

若同時命中多項，先選 primary pattern，再把其他 pattern 當嵌入式子結構，而不是把五種寫成一團。

## 3) Pattern 1: Tool Wrapper

適合：
- 教模型使用特定 library、SDK、framework、內部平台或團隊規範
- 主要價值在「套用既有規則」，不是生成固定模板

典型目錄：
- `SKILL.md`
- `references/`

核心設計：
- `description` 直接寫技術名詞、常見工作動詞、典型檔案或元件名
- `SKILL.md` 只放何時載入、何時讀哪些規範、寫 code / review 時怎麼套用
- 細節規則放進 `references/`

最小骨架：

```md
<decision_boundary>
Use when:
- The user is building, reviewing, or debugging FastAPI code.
Do not use when:
- The task is generic Python with no FastAPI-specific conventions.
</decision_boundary>

<workflow>
Step 1: Load the framework conventions reference file.
Step 2: Apply the conventions to the user's code or question.
Step 3: Cite the violated rule when giving feedback.
</workflow>
```

常見失敗：
- `description` 太泛，像「協助 API 開發」
- 把整份技術文件塞進 `SKILL.md`
- 沒寫何時不用，結果搶到泛用 query

## 4) Pattern 2: Generator

適合：
- 主要任務是穩定產出固定結構的文件、設定檔、腳手架或表單結果
- 一致性比自由發揮更重要

典型目錄：
- `SKILL.md`
- `assets/`
- `references/`

核心設計：
- `assets/` 放模板
- `references/` 放 style guide、品質要求、欄位規則
- `SKILL.md` 負責：缺資料就補問、讀模板、填模板、檢查缺漏

最小骨架：

```md
<workflow>
Step 1: Load the style guide reference file.
Step 2: Load the output template file.
Step 3: Ask for missing required inputs.
Step 4: Fill every required section.
Step 5: Validate against the output contract before returning.
</workflow>
```

常見失敗：
- 只有 prose，沒有模板
- 模板有了，但沒寫缺資料時怎麼處理
- 想要固定格式，卻只寫「請條理清楚」

## 5) Pattern 3: Reviewer

適合：
- 要對既有 code、文件、內容、流程產物做審查
- 審查依據應該可以被 checklist / rubric 明文化

典型目錄：
- `SKILL.md`
- `references/`

核心設計：
- 把 `WHAT to check` 放進 checklist
- 把 `HOW to review` 放進 `SKILL.md`
- 明確定義 findings 格式、severity、定位方式、修正建議格式

最小骨架：

```md
<workflow>
Step 1: Load the review checklist file.
Step 2: Read the artifact and understand its purpose.
Step 3: Apply each checklist item.
Step 4: Return findings grouped by severity with rationale and suggested fixes.
</workflow>
```

Reviewer 的關鍵不是「叫模型 review」，而是把審查標準外部化。這樣 checklist 換掉時，整個審查行為也會跟著換。

常見失敗：
- checklist 跟 review protocol 混在一起
- 只有泛泛建議，沒有 severity 與完成定義
- 輸出只有批評，沒有定位、理由與可執行修正

## 6) Pattern 4: Inversion

適合：
- 缺少關鍵上下文時，直接產出會高機率瞎猜
- 需求蒐集、診斷訪談、規劃類任務要先問再做

典型目錄：
- `SKILL.md`
- 視需要搭配 `assets/`

核心設計：
- 由 skill 主動驅動對話，而不是等使用者自己補完整需求
- 把問題拆成 phase
- 寫清楚 gate：資訊未蒐集完前，不得開始設計、產出或執行

最小骨架：

```md
<workflow>
Phase 1: Ask problem and user-context questions.
Phase 2: Ask technical constraints and non-negotiables.
Phase 3: Only after all required answers are collected, produce the plan using the chosen plan template.
</workflow>
```

常見失敗：
- 只寫「先確認需求」，卻沒寫要問什麼
- 一邊問一邊先產生解法，等於 gate 失效
- 問題順序混亂，導致蒐集到的資訊無法直接餵給後續模板

## 7) Pattern 5: Pipeline

適合：
- 流程有順序依賴
- 某步漏掉會讓後面結果失真
- 中途需要 validator、人工確認或 stop condition

典型目錄：
- `SKILL.md`
- `references/`
- `assets/`
- 必要時 `scripts/`

核心設計：
- 每一步都要有 input / action / output / gate
- 清楚寫「何時不得進下一步」
- validator、checklist、template 與 scripts 各司其職

最小骨架：

```md
<workflow>
Step 1: Parse input and produce inventory.
Step 2: Generate or transform intermediate artifacts.
Step 3: Validate with checklist or script.
Step 4: Only if validation passes, assemble the final artifact.
</workflow>
```

常見失敗：
- 只有列步驟，沒有 gate
- 所有步驟塞成一段，模型容易跳步
- 明明是高風險寫入流程，卻沒 approval gate

## 8) Pattern 組合規則

常見組合：
- `Pipeline + Reviewer`
  用在最後一步需要 checklist 驗收的多階段流程
- `Generator + Inversion`
  先蒐集缺失資訊，再填入固定模板
- `Pipeline + Tool Wrapper`
  流程中某一步需要套用特定 framework / internal system 規範

組合原則：
- 先決定 primary pattern
- 其他 pattern 只作為子步驟或子區塊存在
- 不要讓一個 skill 同時看起來像五種不同產品

## 9) 與現有 repo 規則怎麼對齊

這份 pattern 文件不是要取代既有規則，而是幫你更快決定：
- `references/authoring-patterns.md`：怎麼把單一 skill 寫得可執行
- `references/workflows.md`：長流程怎麼拆
- `references/output-patterns.md`：格式與 few-shot 怎麼鎖
- `references/patterns-troubleshooting.md`：結構失效時怎麼診斷

簡單講：
- 先用這份文件選 pattern
- 再用其他參考文件把這個 pattern 寫紮實

## 10) 快速檢查表

- 我現在選的是哪一個 primary pattern
- 這個 pattern 為什麼比其他四個更像目前任務
- `SKILL.md` 是否真的長得像這個 pattern，而不是只在 metadata 寫名字
- 是否把 secondary patterns 壓在子步驟，而不是把整份 skill 寫散
- 是否已補上對應的 template / checklist / gate / references
