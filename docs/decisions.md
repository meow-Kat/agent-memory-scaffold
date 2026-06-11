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
