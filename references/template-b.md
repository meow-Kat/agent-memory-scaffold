# TEMPLATE B — main rules file snippet

Paste this into the project's CLAUDE.md / AGENTS.md when using **Portable mode**. If the file already carries `agents-md-sync` region markers (`<!-- harness:shared:start -->` …), paste **inside** the shared region; otherwise suggest running `/agents-md-sync` first so this block isn't clobbered on the next sync.

```markdown
## Roles
- Main agent = orchestrator + planner: decomposes, writes plan/tasks, dispatches — never writes code itself.
- Workers (sub-agents, NOT skills): coder (the only one that writes SOURCE code), tester (writes/edits TEST files + runs tests/lint/build incl. container wrappers; never touches source), verifier (strictly read-only, diff-vs-plan + final checks).
- Sub-agents stateless: anything to reuse goes into docs/.

## Work loop (two-phase)
1. Propose: new requirement → docs/plans/<name>.md (draft) → STOP, discuss.
2. Gate: needs approval; if rejected, mark rejected.
3. Execute: split into docs/tasks.md → coder → tester → verifier → all green → commit → update progress.md/tasks.md → next.
   - Close-out stable-tier upkeep (main agent): structural/flow change → architecture.md / flow.md; major trade-off → prepend ADR to decisions.md; **recurring or generalizable lesson, or a user correction → promote a one-line rule into conventions.md (link `→ ADR-NNNN`), dedup/rewrite as the code evolves**. One-offs stay in decisions.md only — don't inflate conventions.
4. On failure: return to coder with the error, else stop and report. Retry caps: coder↔tester max 3 rounds (same failure twice → stop early); verifier runs once; 5 edits on one file → escalate.

## Memory tiers (docs/; English filenames; content English by default, working language only for plans/*; repo docs/ never scratch)
- Stable (read-only bg, rarely written): architecture.md / conventions.md / flow.md / glossary.md — read before any task; update only on structural/flow change, new term, or new recurring rule. conventions.md = forward-binding rules / gotchas promoted from decisions.md or user feedback (one-offs stay in decisions.md).
- Hot (per task): tasks.md (plan) / progress.md (after completion). On session start, READ both manually before acting — they don't autoload.
- History: decisions.md (ADR — file always present as a stub; entries appended on demand). Proposal: plans/<name>.md (draft→approved/rejected) — read on session start to check in-flight status before starting new work.
- Sub-agents are stateless; docs/ is the only shared handoff channel — anything downstream needs must be written there.

## Autoload (needs tool import support — Claude Code `@` imports; Codex / Antigravity have none → inline these summaries here)
@docs/glossary.md
@docs/architecture.md
@docs/conventions.md
- docs/ does NOT autoload by default. Autoload only lean summaries + short files (it pays tokens every session); never autoload architecture detail, decisions, or tasks/progress.

## Deterministic guards (enforce via your tool's mechanism — hook / sandbox / tool-allowlist — NOT prose)
- coder must not commit: a PreToolUse(Bash) hook blocks `git commit` / `git push` (the orchestrator commits after green).
- tester writes TEST FILES ONLY: keep Edit/Write (it authors tests and runs container wrappers like `docker run --rm …`), but block commit/push + package installs. "Tests only" is enforceable only where per-path guards exist (see per-tool notes); elsewhere it stays prose, backstopped by the read-only verifier.
- verifier strictly read-only: remove Edit/Write + a PreToolUse(Bash) hook blocks mutating commands (git commit|add|push, rm, file redirects, package installs).
- Claude Code: put guards in the sub-agent's frontmatter `hooks:` (scoped to that agent only). Tester's "tests only" CAN be enforced here: a PreToolUse(Edit|Write) hook that path-checks against the repo's test dirs (take them from architecture.md).
- Codex: verifier via the agent's own `.codex/agents/<name>.toml` field `sandbox_mode = "read-only"` (cleaner than a hook — no guard needed). Tester needs a writable sandbox; block commit/push via the global `[hooks]` PreToolUse **command** hook in `config.toml` / `hooks.json` — no per-path write restriction exists, so "tests only" stays prose. GOTCHA: Codex runs **command** hooks only — `prompt` and `agent` hook handlers are parsed but silently skipped, so a guard written as a prompt hook does nothing. Codex hooks are global + matcher-scoped, not per-agent like Claude's frontmatter.
- Antigravity (agy): the per-agent guard is the `toolNames` allowlist in the agent spec (global agents: `~/.gemini/antigravity-cli/agents/<name>/agent.json`). Verifier: REMOVE `write_to_file` / `replace_file_content` / `multi_replace_file_content` from `toolNames`. Tester: keep them (it writes tests); "tests only" stays prose. GOTCHA: a "read-only" line in the agent's system prompt while the write tools remain in `toolNames` is a fake guard. agy has no user-facing hook config, so command-level guards (coder's no-commit) are advisory there — say so.
- No hook / sandbox / allowlist support → state explicitly that the restriction is advisory only.
- NOTE: "main agent never writes source" stays a prose discipline — the orchestrator holds all tools, so it can't be cleanly hook-enforced.
```
