# Tasks

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
