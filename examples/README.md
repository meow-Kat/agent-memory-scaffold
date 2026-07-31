# Examples — work-loop role agents (Claude Code format)

Dated snapshots (2026-07-31) of working agent definitions that implement this skill's
work loop. Canonical live copies evolve at the user's `~/.claude/agents/`; these files
are reference implementations, not the source of truth. `prompt-scaffold.md` at the repo
root creates the three roles from scratch on any tool — these show the Claude Code result.

- `agents/coder.md` — the only source writer; no commit; effort inherits.
- `agents/tester.md` — test files only + runs checks; `effort: low`; guarded by both hooks.
- `agents/verifier.md` — strictly read-only final gate; `effort: medium`; reads the tester's
  report instead of re-running checks.
- `agents/browser-tester.md` — browser-verification role for the UI gate; launch info comes
  from the target repo's `docs/architecture.md` `Frontend / UI` field, never hardcoded.
- `hooks/block-mutating-bash.py`, `hooks/block-non-test-writes.py` — the PreToolUse guards
  the tester/verifier frontmatter references as `$HOME/.claude/hooks/<name>.py`. Install to
  `~/.claude/hooks/` (or adjust the frontmatter paths) or the guards silently won't run.
