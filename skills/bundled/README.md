# Skills / Bundled — 精選教育技能

此目錄用於存放精選的教育技能副本（或 symlink）。

## 使用方式

LiangClaw 啟動時會自動掃描此目錄，載入所有含 `SKILL.md` 的子目錄。

## 新增技能

1. 將技能目錄複製到此處（或建立 symlink）
2. 確保技能目錄中有 `SKILL.md`
3. 選擇性加入 `manifest.json`（提供名稱、標籤等 metadata）
4. 重啟 LiangClaw 即可生效

## 技能目錄結構

```
skills/bundled/
├── lesson-plan-generator/
│   ├── SKILL.md
│   ├── manifest.json
│   ├── scripts/
│   └── references/
├── competency-assessment/
│   ├── SKILL.md
│   └── ...
└── README.md  (本檔案)
```

## 系統已載入技能來源

LiangClaw 同時掃描以下路徑：

1. `~/.claude/skills/` — Claude Code 全域技能（自動偵測）
2. `skills/bundled/` — 本目錄（專案內建技能）

兩個來源的技能都會被載入，不會重複。
