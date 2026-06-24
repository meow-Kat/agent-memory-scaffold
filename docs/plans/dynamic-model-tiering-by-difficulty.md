---
status: approved        # approved 2026-06-24; EXECUTE: coder on opus, no tester (pure-docs), verifier read-only consistency check
created: 2026-06-24
---

# Scaffold 內建「依任務難易度動態調整 coder / tester model」(Claude Code only)

## 需求 / 目標

讓這個 skill scaffold 出來的 work loop(以及 audit 標準)本身就帶一條紀律:
**主 agent(orchestrator)在 Phase 2 dispatch 每個 task 前,自評該 task 難易度,
再依難度動態指定 coder / tester 要用的 model**(難 → opus,中 → sonnet,易 → haiku)。
**verifier 不分級,固定 opus**(read-only 終檢用最強 model 把關)。

### 兩層拆清楚(本次定調)

- **第一層 難度判斷(grading)** = 主 agent **自評**,不問人。
- **第二層 tier → 實際 model** = 本次重點;**只針對 Claude Code**,直接判斷該用 **opus / sonnet / haiku**,
  由主 agent 自判,不問人。**agy / Codex / 其他工具本次不理會。**

非目標:不在這個 repo 自己跑分級(本 repo 是純文件 skill,沒有 coder/tester dispatch);
只是把「自判難度 → 選 Claude Code model」的規則寫進 scaffold 產物、global workshop prompts 與 audit 清單。

## 範圍(含明確不做的事)

**做**(全部純文件,零程式碼改動):

1. `references/template-b.md` — work loop 段新增子節 **「Model tiering(difficulty-driven dispatch — Claude Code)」**:
   - 分級主體 = 主 agent;時機 = Phase 2 每個 task dispatch 前;**grading 與 model 選擇皆 orchestrator 自判,不問人**。
   - 三級難度 rubric + 具體訊號(改動範圍、是否新模組、演算法/併發/安全敏感度、模糊度、blast radius、前次是否失敗)。
   - tier → model **直接對照(Claude Code)**:
     - coder:heavy → opus、standard → sonnet、light → haiku(對齊難度)。
     - tester:預設低 coder 一級(coder=opus→sonnet、sonnet→haiku、haiku→haiku);heavy / 安全敏感則對齊 coder。
     - verifier:**固定 opus**(不分級)。
   - **切換機制(Claude Code)**:主 agent 用 Agent/Task tool dispatch 時帶 `model` 參數(opus/sonnet/haiku);
     sub-agent frontmatter `model:` 為預設/fallback。
   - **escalation bump**:接上既有 retry caps —— coder↔tester 重試或同錯兩次時,model 升一級(上限 opus)。
   - 一行誠實 fallback:**非 Claude Code 的工具本子節不覆蓋**,model 選擇退化為該工具預設 / advisory(不展開)。
2. `references/mandatory-files.md` — `architecture.md` 模板 Environment 段新增 **`Model tiers`** **選填 override 欄**
   (預設 `auto` = orchestrator 自判 opus/sonnet/haiku;此欄僅供成本 cap / 帳號限制 / 指定 pin 時覆寫,
   如「heavy 也只准 sonnet」;非 detect-env 偵測、不主動問)。
3. `SKILL.md` —
   - Scaffold 分支:註明 `Model tiers` 由 template 帶,屬**選填 override(預設 auto,不問)**。
   - Audit 分支:新增一項(暫定 **k. Model tiering present & operable**):work loop 是否定義難度自判 +
     coder/tester → opus/sonnet/haiku 對照 + verifier 固定 opus;Claude Code 用 dispatch `model` override(真實機制);
     非 Claude Code → 記 **unsupported-by-tool,非 Missing**(沿用項 h 處理法)。
4. `README.md` — 「The work loop」段補一句動態 model tiering(自判,非詢問);audit「Checks include」清單加對應一項。
5. **`prompt.md`(global workshop — 稽核 prompt)** — TARGET / CHECK 加一條 model-tiering 稽核項:global 設定是否讓 orchestrator
   依難度自判 coder/tester 的 model(Claude Code dispatch `model` override / frontmatter `model:`)、verifier 固定 opus;
   表述對齊 template-b,非 Claude Code 標 unsupported。
6. **`prompt-scaffold.md`(global workshop — 建立角色 prompt)** — 建立 coder/tester/verifier 時:
   每個 agent 設**預設 `model:`**(coder=opus、tester=sonnet、verifier=opus 作為 fallback),
   並註明 **orchestrator 在 dispatch 時依難度 per-task 覆寫 coder/tester**(verifier 固定 opus 不覆寫);
   一行 fallback:非 Claude Code 的工具依其格式設預設、per-dispatch 覆寫能力 advisory。

**不做**:

- **不理會 agy / Codex / 其他工具的 per-dispatch 切換機制** —— 本次只判斷 Claude Code model;
  文件只留一行「非 Claude Code 退化為 advisory」帶過,不寫 per-tool 對照表。
- **不動 `detect-env.py` / `tests/`** —— model tier 不進 `asks[]`、不主動問(模型自判)。
- 不動 global 的 `~/.claude/CLAUDE.md`、`~/.claude/agents/*`、`agy-dispatch` skill(環境層,本 repo 改完另提醒)。
- 不加 quota gating / Pool fallback(agy 帳號特定)。

## 影響的檔案 / 模組

`references/template-b.md`、`references/mandatory-files.md`、`SKILL.md`、`README.md`、
`prompt.md`、`prompt-scaffold.md` —— 共 6 檔,純文件,**零程式碼改動**(detect-env.py / tests 不碰)。

## 做法概述

1. 先定稿 `template-b.md` 新子節(single source:tier/model/機制都住這),確立 rubric、opus/sonnet/haiku 對照、verifier 固定 opus、escalation bump、Claude Code dispatch `model` 機制 + 一行非-Claude fallback。
2. `mandatory-files.md` 的 architecture.md 模板加 `Model tiers` 選填 override 欄,措辭與 template-b 對齊。
3. `SKILL.md` audit 加項 k + scaffold 註記;`README.md` 同步兩處。
4. `prompt.md` 加稽核項、`prompt-scaffold.md` 加角色預設 `model:` + per-dispatch 覆寫說明,措辭對齊 template-b。
5. 收尾掃尾:grep 全 repo 確認 model 措辭一致、無矛盾;更新 docs/tasks.md、progress.md、必要時 decisions.md 補一條 ADR(可 promote 的流程決策)。

## 取捨與替代方案

- **只做 Claude Code**:依你指示,只判斷 opus/sonnet/haiku,不做 tool-neutral per-tool 表 —— 大幅簡化,符合你實際使用環境。
  代價:skill 本體 tool-neutral,本子節對非 Claude 工具只有一行 advisory fallback;日後要補 agy/Codex 再開需求。
- **verifier 固定 opus**(你定):read-only 終檢是正確性最後一道關,用最強 model 不分級 —— 不省這裡的成本。
- **tier 對照住哪**:選 `architecture.md`(env fingerprint 自然延伸,可 per-project 覆寫)。
  替代:住 rules file work loop —— 否決,model 選擇是環境資料、且每 session 自動載入浪費 token。
- **tester 預設低一級 vs 對齊 coder**:選「預設低一級,heavy/安全敏感對齊」—— 寫測試較機械可省成本;留 escalation bump 與安全例外。
- **prompt-scaffold 預設 model**:coder=opus / tester=sonnet / verifier=opus 作 frontmatter fallback;真正的 per-task 選擇靠 orchestrator dispatch 覆寫 —— frontmatter 只是「沒覆寫時的安全預設」。

## 測試計畫

純文件,無程式碼改動 → 無自動測試新增。驗收:

1. grep 全 repo:opus/sonnet/haiku 對照、verifier 固定 opus、dispatch `model` 機制敘述一致、無「coder/tester 固定單一 model」殘留矛盾。
2. 6 檔交叉一致:rubric 與機制以 template-b 為準,其餘 5 檔(含兩 prompt)不得衝突。
3. README 渲染目視確認 work loop 與 audit 清單兩處到位。
4. (回歸保險)`python3 -m unittest discover tests` 仍全綠 —— 確認沒誤動 detect-env。

## 風險 / 未決問題

- skill 本體 tool-neutral,本子節 Claude-Code-specific(prompts 同)—— 已用「非 Claude Code → advisory fallback」一行誠實標註,不假裝覆蓋全工具。
- 與 global `agy-dispatch` 的關係:本次完全不碰 agy 路徑;兩者各自獨立。
- `prompt-scaffold.md` 設角色預設 `model:` 後,與你現有 global `~/.claude/agents/*` 既有定義可能不一致 —— 本 repo 改的是 workshop prompt 文字(供未來重建用),不動現有 agents;若要回灌另提醒。
