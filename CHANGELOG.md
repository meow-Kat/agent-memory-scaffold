# Changelog

Notable changes to `agent-memory-scaffold`. The skill is not formally versioned —
entries are dated (newest first). Format loosely follows
[Keep a Changelog](https://keepachangelog.com/).

## 2026-06-24

### Added
- **Difficulty-driven model tiering** for the work loop (Claude Code): the orchestrator
  self-judges each task's difficulty and picks the model per-dispatch — coder heavy → opus /
  standard → sonnet / light → haiku; tester one tier below coder (match coder on
  heavy/security); verifier fixed opus. Escalation bump on retry; optional `architecture.md`
  `Model tiers` cap. Non-Claude tools degrade to advisory. (ADR-0002)
- **Wave-based parallel execution**: independent tasks (disjoint file sets, no inter-task
  dependency) run as concurrent coder/tester lanes, capped at 4 per wave; one integration test
  over the merged tree, then a single verifier closes out the wave. Sequential is the lossless
  fallback for overlapping/dependent tasks or tools without parallel dispatch. (ADR-0003)
- Audit items **k** (model tiering present & operable) and **l** (parallel/wave execution safe).

### Changed
- Stopped tracking `docs/` in git — the project's working memory (plans/tasks/progress/
  decisions) is kept local and removed from the remote's current tree.
- README: intro now highlights model tiering and wave execution; Portable-mode summary and
  workshop audit prompt (`prompt.md`) updated to match.

## 2026-06-11

### Changed
- README audit checklist synced with `SKILL.md` (compaction-steering, roles-operable, and
  hot-tier↔working-tree consistency checks) + a guards over-block note; structure diagram now
  explains `prompt.md` / `prompt-scaffold.md` as standalone workshop prompts.

### Fixed
- `detect-env.py`: line-anchored the Python-version regex (no longer reads `ipython = "^8.0"`
  as the version) and word-bounded tool detection (`blackjack` no longer registers `black`).

### Added
- `tests/test_detect_env.py` — 9 stdlib `unittest` fixtures (no pytest dependency).
- `.gitignore`; `docs/decisions.md` with ADR-0001 (tester role model).

## 2026-06-10

### Added
- Antigravity (agy) coverage across the skill; Codex mechanism mappings; standalone workshop
  prompts (`prompt.md` audit, `prompt-scaffold.md` create-roles).

### Changed
- Tester role: now writes/edits TEST files and runs container wrappers (e.g. `docker run --rm`);
  the verifier is the single strictly read-only role. (ADR-0001)
