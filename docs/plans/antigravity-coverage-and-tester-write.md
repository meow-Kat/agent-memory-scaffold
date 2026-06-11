---
status: approved
created: 2026-06-10
---

# Antigravity 覆蓋 + tester 角色改為「可寫測試」

## 需求 / 目標

兩件事,一次改完(都落在同一批檔案):

1. **Antigravity (agy) 覆蓋**:skill 目前的機制對照只寫 Claude Code 和 Codex,補上 agy 的對應機制(已調查確認,見下表)。
2. **角色權限模型調整**:tester 實務上需要啟動 docker 跑測試、且需要**撰寫/編輯測試檔**,不能再定義為 read-only。新模型:
   - **coder**:唯一可寫**原始碼**的角色;禁 commit/push。
   - **tester**:可寫/編輯**測試檔**、可跑 docker 與測試指令;不得改原始碼;禁 commit/push、禁裝套件。
   - **verifier**:嚴格 read-only(維持不變)。

### agy 機制對照(調查結論,寫入文件用)

| 概念 | Antigravity (agy) 機制 |
|---|---|
| 主 rules file | `AGENTS.md`(global root + workspace root,與 Codex 共用檔案) |
| Sub-agents | global:`~/.gemini/antigravity-cli/agents/<name>/agent.json`;workspace:`.agents/`(workflows 已確認,agents 待實測) |
| 權限控制 | `agent.json` 的 `toolNames` 白名單(增刪 `write_to_file` / `replace_file_content` / `multi_replace_file_content`) |
| PreToolUse hook | 無 user-facing 設定 → coder 禁 commit 在 agy 上降級為 advisory(明寫,不發明不存在的 hook) |
| `@import` autoload | 無 → 同 Codex,inline 摘要 + "read docs/ first" prose |
| UserPromptSubmit 重注入 | 無 → audit 項 h 對 agy 記 unsupported,非 Missing |
| Skills 路徑 | `~/.gemini/antigravity-cli/skills/<name>/SKILL.md` |

## 範圍(含明確不做的事)

**做**(全部在本 repo):

- `references/template-b.md` — Roles 段:tester 從 "read-only, tests" 改為「寫測試 + 跑檢查,不碰原始碼」;Deterministic guards 段重寫三角色的 per-tool 對照(Claude / Codex / **新增 Antigravity**)。
- `references/mandatory-files.md` — skill 安裝路徑加 agy;rules file 段落註明 `AGENTS.md` 同時服務 Codex 與 Antigravity。
- `prompt.md`(workshop audit prompt)— 「tester & verifier read-only」相關敘述改為新模型;審查清單第 4 項拆成 tester(test-only write)與 verifier(read-only)兩問;補 agy 機制例子。
- `prompt-scaffold.md` — 角色權限定義改新模型;per-agent enforcement 例子清單加 agy `toolNames`;GOTCHA 加一條:agy 的 read-only 若只寫在 prompt、`toolNames` 沒刪 = 假 guard。
- `SKILL.md` — Precheck 補 agy 的 global agents 路徑例;audit 項 c 的措辭更新(guard 不得擋 tester 的測試檔寫入與 docker wrapper);項 h 加註「工具無此機制 → unsupported,非 Missing」。
- `README.md` — guards 段落同步新角色模型;相容性段落維持。

**不做**:

- 不動 `~/.claude/CLAUDE.md`(global)、`~/.claude/agents/` 的角色定義 — 那裡仍寫 tester read-only,改完本 repo 後另列待辦提醒你,屬於 agy/Claude 環境層,不在本 repo。
- 不動 `~/.gemini/antigravity-cli/agents/*/agent.json` — 但結論會附帶建議:verifier 的 `toolNames` 應刪三個寫入工具(目前是 prompt-only 假 guard);tester 在新模型下保留寫入工具反而是正確的,只需 prompt 註明「僅測試檔」。
- 不加 `harness:antigravity:*` region — agy 與 Codex 讀同一個 `AGENTS.md`,region 只防 sync 覆蓋不防讀取,工具特定差異以 per-tool 條列寫在 shared 區即可(template-b 既有作法)。
- 不改 detect-env.py、不新增任何 docs/ 模板檔。

## 影響的檔案 / 模組

`SKILL.md`、`references/template-b.md`、`references/mandatory-files.md`、`prompt.md`、`prompt-scaffold.md`、`README.md` — 共 6 檔,純文件修改,無程式碼。

## 做法概述

1. 先改 `template-b.md`(single source:tier/guard 機制都住這),定稿新角色模型與三工具對照。
2. 其餘 5 檔對照 template-b 的新措辭逐一同步,避免殘留「tester read-only」字樣(以 grep `tester.*read-only|read-only.*tester` 掃尾)。
3. 「tester 僅能寫測試檔」的 enforcement 誠實分級:
   - 可確定 enforce:禁 commit/push、禁裝套件(Claude hook / Codex command hook;agy advisory)。
   - 「只能碰測試檔」:Claude Code 可用 per-agent PreToolUse(Edit|Write) 路徑檢查 hook(需知道 repo 測試目錄,scaffold 時從 architecture.md 取);Codex 無 per-path sandbox → prose;agy → prose。文件明寫各自等級,不假裝。

## 取捨與替代方案

- **替代案 A:tester 維持 read-only,另設第四角色 test-writer** — 否決:增加 dispatch 複雜度,且實務上寫測試與跑測試是同一個迭代迴圈,拆開反而增加交接成本。
- **替代案 B:測試也由 coder 寫,tester 只跑** — 否決:正是目前模型,與你的實際工作流(tester 需編輯測試)衝突。
- **取捨**:tester 取得寫入權後,「不碰原始碼」在 Codex/agy 只剩 prose 約束 — 接受,因為 verifier 仍是 read-only 終檢,且 audit 項 j(hot tier ↔ working tree 一致性)會抓到越權改動。

## 測試計畫

純文件 repo,無自動測試。驗收方式:

1. grep 全 repo 無殘留舊措辭(`tester` + `read-only` 同句)。
2. 6 檔交叉一致:角色定義在 template-b 為準,其餘檔案不得出現矛盾敘述。
3. 三工具對照表完整:每個 guard 都標明 Claude / Codex / agy 的機制或「advisory」。

## 風險 / 未決問題

- workspace 層 `.agents/` 是否可放 agent 定義(目前僅確認 workflows)— 文件先寫「global 路徑已確認、workspace 待實測」,不影響本次。
- 你的 global `~/.claude/CLAUDE.md` 與 `~/.claude/agents/tester` 定義仍是 read-only,本 repo 改完後兩邊會暫時不一致 — 已列入「不做」並於結案時提醒。
- agy `settings.json` permissions 是否支援 deny 規則未確認 — 本次以 advisory 處理,若日後確認支援可升級 guard。
