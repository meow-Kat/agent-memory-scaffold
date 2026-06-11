# Progress

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
