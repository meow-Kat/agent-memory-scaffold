# Tasks

Plan: docs/plans/parallel-wave-execution.md (approved 2026-06-24) — coder on opus, no tester; Q1 cap=4, Q2 include prompt.md

- [x] template-b.md: extend "## Work loop (two-phase)" with wave-based parallel execution (wave grouping by disjoint files/no-deps, parallel coder→tester lanes, integration test, single verifier per wave, sequential fallback for overlap/deps, cap 4 lanes/wave, per-lane retry caps, per-wave commit) + Model tiering one-liner (lanes self-judge as usual)
- [x] SKILL.md: audit item l (parallel/wave execution safe — independence gating, integration test before verifier, single verifier per wave; non-parallel tool → unsupported-by-tool, degrade sequential)
- [x] README.md: work-loop wave paragraph + "Checks include" item l
- [x] prompt.md: wave-execution audit item (TARGET/CHECK), aligned with template-b
- [x] docs/decisions.md: ADR-0003 (wave-based parallel orchestration)
- [x] global: ~/.claude/CLAUDE.md Phase 2 item 4 "Per task" → "Per wave" parallel orchestration + Retry caps per-lane note (done AFTER repo, by orchestrator)
- [x] Close out: grep consistency sweep + `python3 -m unittest discover tests` regression (unchanged) + progress.md (orchestrator)

---

Plan: docs/plans/dynamic-model-tiering-by-difficulty.md (approved 2026-06-24) — coder on opus, no tester

- [x] template-b.md: add "Model tiering (difficulty-driven dispatch — Claude Code)" subsection (rubric + opus/sonnet/haiku mapping, coder/tester/verifier-fixed-opus + escalation bump + dispatch `model` mechanism + one-line non-Claude advisory fallback)
- [x] mandatory-files.md: architecture.md template Environment section — add `Model tiers` optional override field (default auto)
- [x] SKILL.md: audit item k (model tiering present & operable) + scaffold-branch note that Model tiers is optional override
- [x] README.md: work-loop line on dynamic model tiering + "Checks include" item
- [x] prompt.md: add model-tiering audit check item (TARGET/CHECK), aligned with template-b
- [x] prompt-scaffold.md: role default `model:` (coder=opus/tester=sonnet/verifier=opus fallback) + per-dispatch override note
- [x] Close out: grep consistency sweep across 6 files + `python3 -m unittest discover tests` regression (unchanged) + ADR-0002 (progress.md by orchestrator)

---

Plan: docs/plans/readme-sync-and-detect-env-hardening.md (approved 2026-06-11)

- [x] Commit docs/ workflow memory (stale "not committed" note dropped first)
- [x] README: audit checklist +3 items (compaction steering / roles operable / hot-tier consistency) + guards over-block note
- [x] README: structure diagram + explanation for prompt.md / prompt-scaffold.md / tests/
- [x] detect-env.py: line-anchor python version regex (ipython false-positive) + word-boundary tool detection + E741 cleanup
- [x] tests/test_detect_env.py: 9 stdlib-unittest fixture tests (incl. ipython + blackjack regressions)
- [x] .gitignore (DS_Store / ruff_cache / pycache)
- [x] docs/decisions.md: ADR-0001 tester role model (promoted from antigravity plan)
- [x] Close out: progress.md + commit

---

Plan: docs/plans/antigravity-coverage-and-tester-write.md (approved 2026-06-10)

- [x] template-b.md: roles line (tester = test-writer) + Deterministic guards rewrite with per-tool mapping incl. Antigravity
- [x] mandatory-files.md: skill install path + AGENTS.md serves Codex & Antigravity + region-marker note
- [x] prompt.md: least-privilege target + check #4 split (tester test-only-write / verifier read-only) + agy mechanism examples
- [x] prompt-scaffold.md: role definitions + least-privilege rules + agy toolNames mechanism + gotchas
- [x] SKILL.md: precheck agy agents path + audit item c rewording + item h unsupported-vs-missing note
- [x] README.md: guards section new role model + audit bullet wording
- [x] Sweep: grep for stale "tester … read-only" wording across repo (1 hit fixed in mandatory-files.md)
- [x] Close out: progress.md
