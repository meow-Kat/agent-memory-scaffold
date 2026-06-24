---
status: approved        # approved 2026-06-24; Q1 cap=4, Q2 include prompt.md; EXECUTE: coder on opus, no tester (pure-docs), verifier read-only
created: 2026-06-24
---

# Wave-based 平行執行:獨立 task 併發 coder/tester,整合測試後單一 verifier 收尾

## 需求 / 目標

讓 scaffold 出來的 work loop(及 global harness Phase 2)支援**任務級平行**:

- 主 agent 把 `tasks.md` 的 task 分成 **wave**;同一 wave 內的 task **檔案不重疊、無相依**。
- 一個 wave 內,各 task 的 **coder→tester 平行併發**(Claude Code 一輪多個 Agent dispatch)。
- 全 wave 的 lane 各自 green 後,做一次 **整合測試**(對合併後的工作樹跑完整 test/lint/build),抓跨 task 互動。
- 整合測試穩定(全綠)後,**單一 verifier 一口氣收尾**整個 wave(一次 diff-vs-plan + 終檢,出一個 verdict)。
- 有重疊/相依的 task **退回循序**(現有 coder→tester→verifier 流程)——平行是最佳化,不是強制。

核心不變式:**同一 wave 內不得有兩個 coder 寫到同一檔案**(否則衝突);拿不準獨立性 → 循序。

## 範圍(含明確不做的事)

**核心設計(本次定調)**

- **Wave 編排是 tool-neutral 的**(分組 + 整合測試 + 單一 verifier);只有「同 wave 內 lane 併發 dispatch」這一步需要工具支援平行 sub-agent。
- **併發機制(Claude Code)**:主 agent 在同一輪發多個 `Agent(coder)`(及之後多個 `Agent(tester)`)即平行。
- **誠實 fallback**:工具無平行 sub-agent dispatch → 同 wave 的 lane **循序跑**;wave 分組 + 整合測試 + 單一 verifier 結構照舊,結果等價,只是較慢(不丟正確性)。
- **Model tiering 照舊**:每個 lane 的 coder/tester 仍依難度自判 model(沿用既有規則);verifier 固定 opus。
- **失敗處理(平行版)**:lane 內 tester 失敗 → 該 lane 回自己的 coder(retry caps **per-lane** 計);某 lane blocked → 該 wave 的 verifier 卡住,主 agent 回報「部分完成 + blocked lane」,其餘 lane 已 green 的成果保留。整合測試失敗 → 定位出問題的 lane 回該 coder(計入該 lane cap)。verifier 每 wave 跑一次。
- **並發上限**:上限 **4 lane/wave**(可調)以控 blast radius 與 context;超過 → 拆多個 wave 循序。
- **commit 時機**:每個 wave 經 verifier pass 後 commit 一次(不 per-lane commit,保持歷史連貫)。

**做**(repo,純文件):

1. `references/template-b.md` —(single source)`## Work loop (two-phase)` 段擴充 wave 平行執行:
   - 新增「Execute 可分 wave」:主 agent 依 plan/tasks 的「影響檔案」把獨立 task 分組;wave 內 lane 併發。
   - 整合測試步驟 + 單一 verifier per wave + 「重疊/相依 → 循序」fallback + 並發上限 + per-lane retry caps + per-wave commit。
   - `## Model tiering` 補一行:平行 lane 各自照常自判 model。
2. `SKILL.md` — audit 新增一項(暫定 **l. Parallel/wave execution safe**):work loop 是否定義 wave 分組(獨立性 gating:同 wave 不共享檔案)、整合測試先於 verifier、單一 verifier per wave;工具無平行 dispatch → 記 **unsupported-by-tool**(降級循序),非 Missing。
3. `README.md` — 「The work loop」段補 wave 平行執行說明;audit「Checks include」加對應一項。
4. `docs/decisions.md` — 新增 **ADR-0003**(wave 平行編排決策)。
5. `prompt.md`(global workshop 稽核 prompt)— TARGET / CHECK 加一條 wave-execution 稽核項:global 是否定義 wave 分組(獨立性 gating)、整合測試先於 verifier、單一 verifier per wave、重疊/相依退循序;非平行工具標 unsupported(降級循序)。措辭對齊 template-b。

**做**(global,repo 改完後):

6. `~/.claude/CLAUDE.md` — Phase 2 第 4 點 `Per task` 擴充為 **`Per wave`**:獨立 task 分 wave 併發 coder/tester、整合測試、單一 verifier 收尾、重疊/相依退循序、並發上限 4;`### Retry caps` 註明 per-lane 計。

**不做**:

- 不改 `prompt-scaffold.md`(建立角色 prompt)—— 平行是編排層,不改 agent 定義;只動稽核 prompt(prompt.md)。
- 不動 `~/.claude/agents/*`(角色定義不變;平行是編排層,不改 agent 本身)。
- 不碰 `detect-env.py` / `tests/`(與本需求無關)。
- 不做 task 間自動相依分析工具/演算法 —— 獨立性由主 agent 依 plan 的「影響檔案」判斷(prose discipline),不寫偵測程式。
- 不做跨 wave 的自動 rollback / 部分 commit 回退 —— blocked lane 以回報處理,不自動還原其他 lane。

## 影響的檔案 / 模組

repo:`references/template-b.md`、`SKILL.md`、`README.md`、`prompt.md`、`docs/decisions.md`(+ 收尾 `tasks.md` / `progress.md`)。
global:`~/.claude/CLAUDE.md`。共 6 檔(repo 5 + global 1),純文件,**零程式碼改動**。

## 做法概述

1. 先定稿 `template-b.md` 的 Work loop wave 擴充(single source),確立分組規則、整合測試、單一 verifier、fallback、上限、per-lane caps、per-wave commit。
2. `SKILL.md` audit 加項 l;`README.md` 同步兩處;`prompt.md` 加 wave 稽核項;`decisions.md` 加 ADR-0003。
3. grep 掃尾確認 repo 內措辭一致(wave / lane / 整合測試 / 單一 verifier / 循序 fallback / 上限 4)。
4. repo 收尾(tasks.md 勾選、progress.md)後,**再**把規則同步進 `~/.claude/CLAUDE.md` Phase 2,措辭與 template-b 對齊。
5. 回歸保險:`python3 -m unittest discover tests` 仍全綠(確認沒誤動 detect-env)。

## 取捨與替代方案

- **平行 = 最佳化、循序 = fallback**:wave 結構保證正確性,併發只是加速;工具不支援就循序,結果等價 —— 比「平行專屬、不支援就壞掉」誠實且穩。
- **整合測試放哪/誰跑**:選「全 lane green 後,一次 tester run 跑完整套件於合併樹」—— per-lane 測試只證自己的改動,跨 task 互動要靠整合那一跑抓。替代:不做整合測試,直接 verifier —— 否決,verifier 是 read-only 不跑迭代修復,跨 task 互動該在 tester 階段收斂。
- **verifier per wave vs per lane**:選 per wave(你的「一口氣收尾」)—— 省重複終檢;代價:單一 verdict 涵蓋多 task,verifier 報告需逐 task 標明,不能混為一談(會在 template 寫明)。
- **獨立性判斷**:靠 plan 的「影響檔案 / 模組」欄(本來就有)+ 主 agent 判斷,不寫偵測程式 —— prose discipline;拿不準就循序,從嚴。
- **並發上限**:上限 4 lane/wave(你定),避免一輪太多 lane 撐爆 context / 難回報;可依專案調。

## 測試計畫

純文件,無程式碼改動 → 無自動測試新增。驗收:

1. grep:repo 內 wave/lane/整合測試/單一 verifier/循序 fallback 措辭一致,無與既有循序流程矛盾。
2. template-b 為 single source,SKILL/README 不得出現衝突敘述;global CLAUDE.md 與 template-b 規則一致。
3. 既有 sequential 流程仍可讀(平行是疊加,非取代)——確認「重疊/相依 → 循序」明確保留。
4. README 渲染目視確認 work loop + audit 清單兩處到位。
5. (回歸保險)`python3 -m unittest discover tests` 全綠。

## 風險 / 未決問題

- Q1 已定:並發上限 **4 lane/wave**(可調)。
- Q2 已定:`prompt.md` **要做** wave-execution 稽核項(與 model-tiering 對等)。
- skill 本體 tool-neutral,本擴充的「併發」是 Claude Code 能力 —— 已用「不支援 → 循序 fallback、結果等價」誠實標註(比 model-tiering 那條更乾淨,因為循序不丟正確性)。
- global CLAUDE.md 與 `/agy-dispatch`:agy 路徑本次不碰;若 agy 也想平行另開需求。
- 平行 lane 共享檔案的偵測純靠 prose discipline,有誤判風險 —— 以「拿不準就循序、從嚴」緩解,並在 template 明寫不變式。
