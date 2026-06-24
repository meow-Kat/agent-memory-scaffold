# Progress

## 2026-06-24 — Difficulty-driven model tiering for coder/tester (plan: dynamic-model-tiering-by-difficulty)

Outcome: the scaffolded work loop now bakes in dynamic model selection — the orchestrator
self-judges each Phase 2 task's difficulty and picks the Claude Code model per-dispatch, no
asking the user. Mapping: coder heavy→opus / standard→sonnet / light→haiku; tester one tier
below coder (heavy/security → match coder); verifier FIXED opus (read-only final gate stays
strongest). Escalation bump tied to the existing retry caps (retry / same-failure-twice →
+1 tier, cap opus). Switch mechanism = orchestrator passes `model` on dispatch, sub-agent
frontmatter `model:` as fallback. Scope was deliberately Claude-Code-only per request: a
single honest "non-Claude → advisory" line, NO per-tool agy/Codex table.

6 docs files edited (template-b.md as single source; mandatory-files.md architecture.md gets
an optional `Model tiers` override field defaulting to `auto`; SKILL.md audit item k;
README work-loop + Checks-include; prompt.md audit check; prompt-scaffold.md role default
`model:` + per-dispatch override note). ADR-0002 prepended to decisions.md. Zero code changes
— detect-env.py / tests untouched (9 unittests still green).

Two-phase loop: coder on opus (user-directed), tester waived (pure-docs, no automated tests
to run), verifier (opus, read-only) → verdict pass. The `Model tiers` field is an OPTIONAL
override (cost cap / pin / account limit only); default auto means full self-judging.

## 2026-06-11 — README sync + detect-env hardening (plan: readme-sync-and-detect-env-hardening)

Outcome: closed the drift + hardening gaps found in the 2026-06-11 review. README
audit checklist caught up with SKILL.md items h/i/j (was 7 of 10) and the structure
diagram now explains prompt.md / prompt-scaffold.md as standalone workshop prompts
the skill never loads. detect-env.py: python-version regex line-anchored (regression:
`ipython = "^8.0"` parsed as the version), tool detection word-bounded ("blackjack"
no longer registers black), E741 names fixed. Added tests/test_detect_env.py — 9
stdlib-unittest fixture tests (no pytest dependency), all green; ruff clean. Added
.gitignore and docs/decisions.md with ADR-0001 (tester role model, promoted from the
antigravity plan's trade-off section). docs/ itself is now tracked in git.

Deliberately NOT done (review conclusions): no CI / pytest / ruff config (prose
skill — traditional gates don't apply); no architecture/flow/glossary/conventions
stubs (six-mandatory rule targets projects with a dev loop, not this skill repo);
prompt*.md not moved into a subfolder (install-layout decision deferred).

Executed directly by the main agent (user-approved verbally, role agents waived).

## 2026-06-10 — Antigravity coverage + tester role change (plan: antigravity-coverage-and-tester-write)

Outcome: skill now covers three tools (Claude Code / Codex / Antigravity) and the role
model changed from "tester read-only" to "tester writes TEST files + runs container
wrappers; verifier strictly read-only". 6 files edited (SKILL.md, README.md, prompt.md,
prompt-scaffold.md, references/template-b.md, references/mandatory-files.md); docs-only,
no code. Edited directly by the main agent (doc edits depending on session-local agy
binary analysis; role agents not dispatched). Verified via grep sweep: no stale
"tester read-only" wording; agy mechanisms present in all 6 files.

Key agy facts baked into the docs (from binary-strings analysis of agy 1.0.7):
- Rules file: AGENTS.md (global + workspace customization roots; shared with Codex —
  region markers don't scope reading, only sync).
- Per-agent guard: `toolNames` allowlist in `~/.gemini/antigravity-cli/agents/<name>/agent.json`.
- No user-facing hook config → coder no-commit is advisory on agy.
- No @import; no UserPromptSubmit equivalent (audit item h → unsupported, not Missing).
- Skills path: `~/.gemini/antigravity-cli/skills/<name>/SKILL.md`.

Follow-up sync (same day, user-requested): external configs updated to match —
- ~/.claude/CLAUDE.md roles line: tester = test-file writer, verifier = read-only.
- ~/.claude/agents/tester.md: Edit/Write restored; guards = block-mutating-bash.py +
  new ~/.claude/hooks/block-non-test-writes.py (PreToolUse Edit|Write|NotebookEdit,
  generic test-path patterns, fail closed; smoke-tested: blocks src/, allows
  tests/ dirs, test_*.py, *.test.ts, *Test.php, conftest.py).
- agy verifier/agent.json: write tools removed from toolNames (guard now real).
- agy tester/agent.json: write tools kept; description + prompt now say "test files
  only, never source; advisory — backstopped by verifier".

Still unconfirmed (harmless): whether agy workspace `.agents/` accepts agent
definitions (only workflows confirmed); whether agy settings.json permissions
support deny rules.
