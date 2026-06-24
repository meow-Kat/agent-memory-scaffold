# Decisions
> Append-only log. Newest entry first. One entry per major trade-off (architecture, framework, protocol, library, …).
> Status flow: proposed → accepted → (later) superseded by ADR-NNNN | deprecated.

<!-- ADR template — copy, fill, prepend:

## ADR-NNNN: <title>
**Date**: <YYYY-MM-DD>
**Status**: proposed | accepted

### Context
### Decision
### Consequences
### Alternatives considered
-->

## Entries
<!-- newest first -->

## ADR-0002: Difficulty-driven model tiering for coder/tester (Claude Code), verifier fixed opus
**Date**: 2026-06-24
**Status**: accepted

### Context
Running every role on one fixed model wastes capability on trivial edits or
under-powers hard tasks. We want a cost/capability balance per task without
asking the user each time. Scope this round is Claude Code only (opus / sonnet
/ haiku); agy / Codex per-dispatch switching is out of scope.

### Decision
The orchestrator self-judges each task's difficulty at dispatch time (no
asking) and picks the model per role: coder heavy→opus / standard→sonnet /
light→haiku; tester one tier below coder (opus→sonnet, sonnet→haiku,
haiku→haiku), matching coder on heavy/security-sensitive tasks; verifier FIXED
opus, not tiered. Escalation bump ties to the existing retry caps (retry or
same failure twice → bump one tier, cap opus). Switch mechanism is the Claude
Code dispatch `model` param, with the sub-agent frontmatter `model:` as
fallback. `architecture.md` Environment gains an optional `Model tiers`
override (default `auto` = self-judge), used only to cap cost / pin / honor an
account limit — not detect-env-detected, not asked.

### Consequences
Pure-docs change (no detect-env / test code touched). The mechanism is
Claude-Code-specific; non-Claude tools get a one-line advisory fallback
(degrade to the tool's default). `references/template-b.md` Model tiering
subsection is the single source; SKILL audit item k, README, and both workshop
prompts follow it.

### Alternatives considered
- Ask the user the model per task — rejected: model selection should be
  self-judged, not a per-task interruption.
- Tool-neutral per-tool tier table (agy / Codex mechanisms) — rejected:
  out of scope this round; only a one-line non-Claude advisory is kept.

## ADR-0001: Tester writes test files; verifier is the only read-only role
**Date**: 2026-06-10
**Status**: accepted

### Context
The original role model defined the tester as read-only (run checks, report).
In practice the tester must author/edit test files and launch container
wrappers (`docker run --rm …`); read-only forced test authoring onto the coder
and over-broad guards blocked legitimate test runs.

### Decision
coder = the only SOURCE-code writer (no commit/push). tester = writes/edits
TEST files only + runs tests/lint/build incl. container wrappers (no commit,
no installs). verifier = strictly read-only, runs once, returns a verdict.

### Consequences
"Tests only" is enforceable per-path only where the tool supports it (Claude
Code per-agent PreToolUse(Edit|Write) path check); on Codex and Antigravity it
stays honest prose, backstopped by the read-only verifier and the hot-tier ↔
working-tree audit check. Guard specs across all skill docs follow
`references/template-b.md` as the single source.

### Alternatives considered
- Keep tester read-only, add a fourth test-writer role — rejected: extra
  dispatch complexity; writing and running tests is one iteration loop.
- Coder writes tests, tester only runs them — rejected: that was the original
  model and conflicts with the actual workflow.
