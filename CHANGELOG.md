# Changelog

Notable changes to `agent-memory-scaffold`. The skill is not formally versioned —
entries are dated (newest first). Format loosely follows
[Keep a Changelog](https://keepachangelog.com/).

## 2026-07-31

### Added
- **Effort as the primary cost/latency control on Opus 5** (template-b Model tiering): frontmatter
  `effort` (`low|medium|high|xhigh|max`, model-dependent) now sits ahead of model switching as the
  first-line cost lever; per-role baselines — coder unset/inherit, tester `effort: low`, verifier
  `effort: medium` (bump to `high` if it starts missing issues). Dispatch has no `effort` param, so
  effort stays frontmatter-static; per-task dynamic control still runs through `model`. (ADR-0005)
- **Frontend/UI declaration + gate**: `architecture.md` gains a `Frontend / UI` field (`none`, or
  launch cmd + URL + mock/clean-DB note) — not detected by `detect-env.py`, folded into the
  consolidated ask round. When ≠ none, the work loop browser-verifies UI-touching tasks (via a
  browser-testing sub-agent) after tester green and before the verifier; tools without one →
  unsupported-by-tool, report states unverified-in-browser. Audited as new item **n**. (ADR-0006)
- **`examples/`**: dated snapshots of the four working role-agent definitions (coder, tester,
  verifier, browser-tester — Claude Code format, effort baselines included) plus the two
  PreToolUse guard scripts their frontmatter references. Reference output of `prompt-scaffold.md`;
  never loaded by the skill.

### Changed
- **Rubric Plan A**: haiku leaves the coder/tester model rubric — it doesn't support `effort` — so
  light tier now maps to sonnet alongside standard (`light/standard → sonnet`, `heavy → opus`);
  tester's one-tier-below floors at sonnet (opus→sonnet, sonnet→sonnet). Verifier stays fixed opus,
  now with `effort: medium`.
- `prompt-scaffold.md` verifier description: no longer unconditionally "re-runs checks" — reads the
  tester's/integration report first, re-running checks only if that report is missing or the diff
  changed after it (drops the redundant re-run the official Opus 5 guide calls out as
  over-verification).
- SKILL.md audit item k: extended with effort checks (baselines present on supported roles, absent
  on haiku/effort-unsupported paths; non-Claude tools → unsupported-by-tool, not Missing).
- README.md, prompt.md, `references/mandatory-files.md`: rubric/tiering mentions synced to Plan A +
  effort.
- Conciseness pass (template-b Model tiering + SKILL.md item k): dropped the dead standard/light
  distinction (both map to sonnet → "heavy → opus; everything else → sonnet"), the duplicate coder
  per-role line, the twice-stated verifier `effort: medium`, and explanatory asides — template-b is
  embedded per-project and read every session, so its wording is a recurring token cost.

## 2026-07-06

### Added
- **`.claude/rules/` mechanism** documented in the Autoload narrative (template-b): rule files
  without frontmatter load every session; `paths:`-frontmatter rules load conditionally when a
  matching file is touched — recommended at PROJECT level only (user-level path-scoped rules
  reported silently ignored, GH #21858, unverified). `@` imports stay the shown default;
  rules complement, not replace, them. (ADR-0004)
- **Optional session-start hot-tier injection**: on Claude Code a `SessionStart` hook can
  deterministically inject tasks.md/progress.md/plans status instead of the manual-read prose
  rule. Audited as new item **m** — an upgrade, not a baseline (absent → suggested, NOT Missing;
  non-Claude tools → unsupported-by-tool).

### Changed
- Audit item **d**: split targets for an over-long rules file now include project-level
  `.claude/rules/`; official ~200-line guidance noted as the outer bound (the skill's
  ~80–120-line target stays stricter).

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
  workshop audit prompt (`prompt.md`) updated to match; overall README condensed (142 → 105 lines).

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
