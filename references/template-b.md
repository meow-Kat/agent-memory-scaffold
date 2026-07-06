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
   - **Wave-based parallel (optional optimization)**: the orchestrator MAY group tasks.md tasks into **waves** and run a wave's tasks concurrently. Group by the plan's "影響的檔案 / 模組" (affected files): tasks in one wave MUST have **disjoint file sets and no inter-task dependency** — core invariant: **no two coders in a wave write the same file**. Independence uncertain → keep them sequential (err strict). Within a wave the orchestrator dispatches each task's coder concurrently (Claude Code: multiple Agent/Task calls in one turn), then the testers concurrently — each lane is still coder→tester with the normal model tiering and **per-lane** retry caps. Cap: **max 4 lanes/wave**; more tasks → split into multiple sequential waves. After all lanes in a wave are individually green, run ONE **integration test** — the full test/lint/build over the merged working tree — to catch cross-task interaction (a tester run over the whole diff). Once integration is stable/green, ONE **verifier per wave** reviews all the wave's task diffs vs their plan(s) at once and returns a single verdict — but the report MUST call out each task separately (don't blur multiple tasks into one verdict). Commit once **per wave** after the verifier passes (not per-lane). Parallel is an optimization; the wave grouping + integration test + single verifier structure is tool-neutral, and tools without parallel sub-agent dispatch run the wave's lanes **sequentially** — same structure, same outcome, just slower (lossless fallback).
4. On failure: return to coder with the error, else stop and report. Retry caps: coder↔tester max 3 rounds (same failure twice → stop early); verifier runs once; 5 edits on one file → escalate.
   - **Parallel failure handling**: a lane's tester failure → that lane loops back to its OWN coder (retry caps counted **per-lane**: coder↔tester max 3 rounds, same failure twice → stop that lane). Integration-test failure → identify the offending lane(s), loop back to that coder (counts toward its lane cap). A blocked lane → orchestrator reports partial completion + the blocked lane; other green lanes' work is preserved (no auto-rollback).

## Model tiering (difficulty-driven dispatch — Claude Code)
- Orchestrator self-grades each task's difficulty at dispatch time (no asking the user; grading AND model choice are self-judged), then picks the coder/tester model per-dispatch. Signals: change size/scope, new module vs localized edit, algorithmic/concurrency/security sensitivity, ambiguity, blast radius, whether a prior attempt failed.
- Rubric → model: light (localized edit, low blast radius, unambiguous) → haiku; standard (typical feature, contained scope) → sonnet; heavy (new module, algorithm/concurrency/security-sensitive, high blast radius, or prior attempt failed) → opus.
- Per role:
  - coder: heavy → opus, standard → sonnet, light → haiku (model aligns to difficulty).
  - tester: default one tier below coder (opus→sonnet, sonnet→haiku, haiku→haiku); for heavy or security-sensitive tasks → match coder.
  - verifier: FIXED opus, not tiered — the read-only final gate always uses the strongest model.
- Escalation bump (ties to the Work loop retry caps above): on a coder↔tester retry or the same failure twice, bump the model one tier (cap at opus).
- Switch mechanism (Claude Code): the orchestrator passes the `model` param (opus/sonnet/haiku) when dispatching via the Agent/Task tool; the sub-agent frontmatter `model:` is the default/fallback when no param is passed.
- Optional override: `architecture.md` Environment `Model tiers` (default `auto` = self-judge) can cap/pin per project (e.g. "heavy also only sonnet"); honor it over the rubric.
- Parallel lanes (wave execution): each lane's coder/tester self-judges its own model as usual — wave grouping doesn't change per-lane model selection.
- Non-Claude tools: this subsection does not apply — model selection degrades to the tool's default / advisory.

## Memory tiers (docs/; English filenames; content English by default, working language only for plans/*; repo docs/ never scratch)
- Stable (read-only bg, rarely written): architecture.md / conventions.md / flow.md / glossary.md — read before any task; update only on structural/flow change, new term, or new recurring rule. conventions.md = forward-binding rules / gotchas promoted from decisions.md or user feedback (one-offs stay in decisions.md).
- Hot (per task): tasks.md (plan) / progress.md (after completion). On session start, READ both manually before acting — they don't autoload. Optional upgrade on Claude Code: a `SessionStart` hook can inject tasks.md/progress.md/plans status into context deterministically; other tools have no equivalent, so the manual read stays advisory there.
- History: decisions.md (ADR — file always present as a stub; entries appended on demand). Proposal: plans/<name>.md (draft→approved/rejected) — read on session start to check in-flight status before starting new work.
- Sub-agents are stateless; docs/ is the only shared handoff channel — anything downstream needs must be written there.

## Autoload (needs tool import support — Claude Code `@` imports; Codex / Antigravity have none → inline these summaries here)
@docs/glossary.md
@docs/architecture.md
@docs/conventions.md
- docs/ does NOT autoload by default. Autoload only lean summaries + short files (it pays tokens every session); never autoload architecture detail, decisions, or tasks/progress.
- Claude Code alternative/complement: `.claude/rules/` — a markdown rule file with NO frontmatter loads every session, same as CLAUDE.md content; a rule file WITH a `paths:` frontmatter glob list loads only when Claude reads a matching file (conditional, no token cost until triggered). Use PROJECT-level `.claude/rules/` for `paths:` rules — user-level (`~/.claude/rules/`) path-scoped rules have been reported silently ignored (GH issue #21858, unverified). `@` imports above stay the default for lean summaries; rules complement, not replace, them. Codex / Antigravity have no equivalent → unsupported-by-tool.

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
