---
name: agent-memory-scaffold
description: Use when starting in a project that lacks systematic memory/management structure — no docs/ memory layers, no main-rules-file mechanism, or no two-phase workflow. Detects what's missing and scaffolds it from template. Do NOT use if the structure already exists and is maintained.
---

# Project memory scaffold

Scaffold the systematic memory/management structure when a project lacks it. Tool-neutral: map "main rules file" / "import" / "hook" / "sub-agent" onto your tool's actual mechanisms; if unsupported, use the closest substitute and say so.

## When to trigger
On entering a project, if ANY of these are true:
- No docs/ memory layers (architecture / flow / glossary / tasks / progress / decisions)
- Main rules file (CLAUDE.md / AGENTS.md) has no memory mechanism or work loop
- No docs/memory.md spec

## Steps
1. Detect: check each item in "Target structure" below; mark Exists / Missing.
2. Fill gaps only: create missing items from the templates. NEVER overwrite existing files — add only what's missing.
3. Report: list what you created, which `<fill-in>` spots the user must complete, and which mechanisms (autoload / hook) depend on the tool and need confirming.
4. Don't start work: after scaffolding, STOP and wait for the user — do not proceed into any dev task.

## Conventions (apply to all output)
- Filenames English; Structural spec text may stay English.
- Write all memory files to the current repo's docs/ (repo-relative), NEVER the session/conversation scratch dir.
- docs/ does NOT autoload by default; it only takes effect via the main rules file's import or an inlined summary.
- Stable tier = read-only background, written only when structure/flow truly changes; tasks/progress = per-task writes; decisions = written only when needed.

## Target structure
```
docs/
├── plans/           # proposal drafts, one file per requirement, status: draft→approved/rejected
├── tasks.md         # approved execution list (rolling)
├── progress.md      # done log + cross-session handoff
├── architecture.md  # stable: structure; update only when structure changes
├── flow.md          # stable: flows / cross-module deps (skip if flow is trivial)
├── glossary.md      # stable: domain terms (skip if no jargon)
├── decisions.md     # history: ADR
└── memory.md        # full spec of this memory mechanism
```
Main rules file (CLAUDE.md / AGENTS.md) must contain: roles, two-phase work loop, memory summary, autoload hookup.

---

## TEMPLATE A — docs/memory.md
```markdown
# Memory spec
Agents must adjust read/write behavior per this spec after reading the main rules file.

## Tiers & cadence
- Stable (read-only bg, rarely written): architecture.md (structure), flow.md (flows), glossary.md (terms). Read before any task; update only on structural/flow change or new term.
- Hot (written per task): tasks.md (plan), progress.md (after completion).
- History (written on demand): decisions.md (ADR).
- Proposal (one file per requirement): plans/<name>.md, status draft→approved/rejected.

## Autoload
- Should autoload: architecture summary, glossary, flow (if cross-module deps exist).
- Should NOT: architecture detail, decisions, tasks/progress.
- How: if the tool supports import, import them in the main rules file; else inline the summary into the main rules file.
- Trade-off: autoload = guaranteed-read but pays tokens every session, so autoload only lean summaries + short files.

## Read/write timing
Happens via the work loop, not automatically: requirement → plan draft (STOP, discuss) → approve → split tasks → dispatch coder/tester/verifier (read bg before acting) → all green → commit → update progress.
Sub-agents are stateless; docs/ is the only shared handoff channel — anything downstream needs must be written to docs/.

## Hard rules
Filenames English; paths under repo's docs/ (never scratch). If the tool's built-in behavior violates this, fix via hook or setting.
```

## TEMPLATE B — main rules file snippet (paste into CLAUDE.md / AGENTS.md)
```markdown
## Roles
- Main agent = orchestrator + planner: decomposes, writes plan/tasks, dispatches — never writes code itself.
- Workers (sub-agents, NOT skills): coder (only one that writes code), tester (read-only, tests), verifier (read-only, lint/build + spec review).
- Sub-agents stateless: anything to reuse goes into docs/.

## Work loop (two-phase)
1. Propose: new requirement → docs/plans/<name>.md (draft) → STOP, discuss.
2. Gate: needs approval; if rejected, mark rejected.
3. Execute: split into docs/tasks.md → coder → tester → verifier → all green → commit → update progress.md/tasks.md → next.
4. On failure: return to coder with the error, max 3 retries, else stop and report.

## Memory (full spec in docs/memory.md)
- Read the stable tier as background before any task; write tasks.md/progress.md per task.
- docs/ files: English filenames, 繁中 content, written to repo's docs/ (never scratch).

## Autoload (needs tool import support; else inline these summaries here)
@docs/glossary.md
@docs/architecture.md

## Deterministic guards (hooks, if supported)
- Block coder from committing directly; block planning from executing before approval.
```

## TEMPLATE C — stable-tier file header (start of each)
```markdown
# (architecture / flow / glossary — pick one)
> Stable tier, read-only background. Update only on real structural/flow change or new term. Content in 繁體中文.

<fill in project content>
```
