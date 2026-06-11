---
status: approved        # 口頭核准(2026-06-11「都幫我做 不需要使用 agents」);主 agent 直接執行,不派 role agents
created: 2026-06-11
---

# README 同步 + detect-env.py 強化

## 需求 / 目標

審查發現的缺口一次修完:

1. **README 稽核清單落後 SKILL.md** — SKILL.md 的 audit 已是 a–j 十項,README「Checks include」只列 7 項,缺 h(compaction steering)、i(roles operable)、j(hot tier ↔ working tree)。guards 那條也沒提 over-block 概念。
2. **README 結構圖漏檔** — `prompt.md` / `prompt-scaffold.md` 已 commit 在 repo 根目錄但 README 沒解釋(workshop prompts,skill 本體不載入)。
3. **detect-env.py regex 誤判** — `(?:python|requires-python)\s*=` 無邊界,`ipython = "^8.0"` 會被誤認成 Python 版本;blob 的 substring 偵測(`"black" in blob`)同類問題。
4. **detect-env.py 零測試** — 它是 skill 裡唯一會執行的程式、定位是「detection 唯一真相來源」,壞掉即退化成 LLM 亂猜。補 stdlib `unittest` fixture 測試(不引入 pytest 相依)。
5. **repo 無 .gitignore** — 公開 repo,別人 clone 後沒有全域 ignore 保護。
6. **ADR 留檔** — tester 角色模型的取捨目前只在 plan 檔裡,promote 成 `docs/decisions.md` ADR-0001。

## 範圍(含明確不做的事)

**做**:README.md、detect-env.py、新增 tests/test_detect_env.py、新增 .gitignore、新增 docs/decisions.md、docs/tasks.md / progress.md 收尾。

**不做**:
- 不搬 prompt.md / prompt-scaffold.md 到子資料夾(改安裝佈局是另一個決策),只在 README 說明。
- 不建 CI、不引入 pytest/ruff 設定 — prose skill 不適用傳統 CI gate(前輪討論結論)。
- 不補 architecture.md / flow.md / glossary.md / conventions.md — 六 mandatory 是給有開發迴圈的目標專案,本 repo 不硬套。
- 不動 SKILL.md / references/ / prompt 檔內容。

## 影響的檔案 / 模組

README.md、detect-env.py、tests/(新)、.gitignore(新)、docs/decisions.md(新)、docs/tasks.md、docs/progress.md。

## 做法概述

1. README:「Checks include」補三項(h/i/j)+ guards 條補 over-block;結構圖加兩個 prompt 檔並註明「skill 不載入」。
2. detect-env.py:版本 regex 改行首錨定 `^\s*(?:requires-python|python)\s*=`;blob 偵測改 `\b` 邊界。
3. tests:subprocess 跑 script、JSON 驗證(空 repo / pyproject / ipython 回歸 / poetry / node / go);清除 CONDA/VIRTUAL_ENV 環境變數確保確定性。
4. decisions.md:用 mandatory-files.md 自家模板 + ADR-0001(tester 角色模型,內容自 plan 取捨段濃縮,英文)。

## 測試計畫

`python3 -m unittest discover tests` 全綠;`ruff check detect-env.py` 乾淨;README 渲染目視確認。

## 風險 / 未決問題

- 行首錨定 regex 假設 pyproject 的 `python =` 鍵在行首(含縮排)— TOML 慣例如此,風險低。
- tests/ 會隨 `npx skills add` 一起被安裝進 skill 資料夾 — 無害,接受。
