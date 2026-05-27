---
name: agent-memory-scaffold
description: Use when entering a project to set up or check its systematic memory/management structure (docs/ memory layers, main-rules-file work loop, two-phase workflow). If pieces are missing, scaffolds them from templates. If the structure already exists, runs a read-only AUDIT — grades each item Has/Partial/Missing per layer (project/docs) and reports the highest-ROI gaps. Never overwrites existing files; never starts dev work.
---

# Project memory scaffold

Set up — or audit — the systematic memory/management structure for an AI-coding project. Tool-neutral: map "main rules file" / "import" / "hook" / "sub-agent" onto your tool's actual mechanisms; if a mechanism is unsupported, use the closest substitute and say so.

Two modes, decided in Detect:
- **Scaffold** — structure is missing → create only the missing pieces from templates.
- **Audit** — structure exists → read-only review, grade gaps, recommend. Make no changes.

## Precheck — work-loop roles
The work loop dispatches coder/tester/verifier. Confirm they exist as dispatchable sub-agents in your tool. Planner is ALWAYS the main agent (orchestrator), never a sub-agent — do not look for a planner agent.
- If coder/tester/verifier are missing → tell the user to set those roles up first (their global/user agent scope) and STOP; scaffolding docs without the roles leaves the loop unrunnable.
- If the tool has no sub-agent mechanism → say so; the loop degrades to the main agent performing all steps itself.

## When to use
On entering a project. Look for: docs/ memory layers (architecture / flow / glossary / tasks / progress / decisions), a main rules file (CLAUDE.md / AGENTS.md) carrying the work loop + memory mechanism, and docs/memory.md. Missing → scaffold. Present → audit.

## Steps
1. Detect: check each item in "Target structure" → mark Has / Partial / Missing (tag layer: project / docs).
2. Branch:
   - Mostly Missing → SCAFFOLD: create only the missing items from the templates. NEVER overwrite an existing file.
   - Exists / maintained → AUDIT (read-only, make NO changes), checking:
     a. main rules file contains the work loop AND points to the English docs/ filenames
     b. all docs/ files present, English filenames, and actually maintained (is progress.md updated on commit?)
     c. commit / source-write restrictions enforced by a real guard (hook), not just prose
     d. main rules file is lean (~80–120 lines) — if over, flag which detail to split into docs/
     e. docs/ genuinely used as shared memory, or are sub-agents flying blind?
     f. any redundant project-level role/rule override duplicating global (delete unless the LOGIC, not just data, differs)
3. Report:
   - SCAFFOLD → what you created + which `<fill-in>` spots the user must complete + which mechanisms (autoload / hook) depend on the tool and need confirming.
   - AUDIT → Has/Partial/Missing table (with layer tag) + a one-line fix each + the top-3 highest-ROI gaps.
4. STOP: in either mode, do not proceed into any dev task — wait for the user.

## Conventions (apply to all output)
- Filenames: English. File CONTENT: The scaffold's own spec/template text may stay English.
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
└── memory.md        # full spec of this memory mechanism — also the single source of "what good looks like" the AUDIT mode grades against
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
Filenames English; file content in the project's working language; paths under repo's docs/ (never scratch). If the tool's built-in behavior violates this, fix via hook or setting.
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
- docs/ files: English filenames, content in the project's working language, written to repo's docs/ (never scratch).

## Autoload (needs tool import support; else inline these summaries here)
@docs/glossary.md
@docs/architecture.md

## Deterministic guards (enforce via your tool's hook mechanism, NOT prose)
- coder must not commit: a PreToolUse(Bash) hook blocks `git commit` / `git push` (the orchestrator commits after green).
- tester/verifier read-only: remove Edit/Write + a PreToolUse(Bash) hook blocks mutating commands (git commit|add|push, rm, file redirects, package installs).
- Claude Code: put these in the sub-agent's frontmatter `hooks:` (scoped to that agent only).
- No hook support → state explicitly that the restriction is advisory only.
- NOTE: "main agent never writes source" stays a prose discipline — the orchestrator holds all tools, so it can't be cleanly hook-enforced. Say so honestly.
```

## TEMPLATE C — stable-tier file header (start of each)
```markdown
# (architecture / flow / glossary — pick one)
> Stable tier, read-only background. Update only on real structural/flow change or new term.

<fill in project content>
```
