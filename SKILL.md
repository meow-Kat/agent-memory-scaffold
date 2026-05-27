---
name: agent-memory-scaffold
description: Use when entering a project to set up or check its systematic memory/management structure (docs/ memory layers, main-rules-file work loop, two-phase workflow). Missing pieces → scaffold from templates. Already exists → read-only AUDIT, grading each item Has/Partial/Missing per layer (project/docs) and reporting the highest-ROI gaps. Never overwrites existing files; never starts dev work.
---

# Project memory scaffold

Set up — or audit — the systematic memory/management structure for an AI-coding project. Tool-neutral: map "main rules file" / "import" / "hook" / "sub-agent" onto your tool's actual mechanisms; if a mechanism is unsupported, use the closest substitute and say so. Two modes, chosen in Detect: **scaffold** when pieces are missing, **audit** (read-only) when the structure already exists.

## Precheck — work-loop roles
The work loop dispatches coder/tester/verifier. Confirm they exist as dispatchable sub-agents in your tool. Planner is ALWAYS the main agent (orchestrator), never a sub-agent — do not look for a planner agent.
- coder/tester/verifier missing → tell the user to set those roles up first (their global/user agent scope) and STOP; scaffolding docs without the roles leaves the loop unrunnable.
- No sub-agent mechanism in the tool → say so; the loop degrades to the main agent doing all steps itself.

## Steps
1. Detect: for each item in "Target structure" (docs/ layers + the main rules file carrying the work loop & memory mechanism) → mark Has / Partial / Missing (tag layer: project / docs).
2. Branch:
   - Mostly Missing → SCAFFOLD: create only the missing items from the templates. NEVER overwrite an existing file.
   - Exists / maintained → AUDIT (read-only, make NO changes), grading against "Target structure":
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

## Conventions
- Filenames English; file CONTENT in the project's working language (e.g. 繁體中文). The scaffold's own template/spec text may stay English.
- Write all output to the current repo's docs/ (repo-relative), NEVER a session/scratch dir. Not a repo → ask the user where.
- All tier / autoload / read-write mechanics live in TEMPLATE B — the single source. Don't restate them elsewhere.

## Target structure (also the AUDIT baseline)
```
docs/
├── plans/           # proposal drafts, one file per requirement, status: draft→approved/rejected
├── tasks.md         # approved execution list (rolling)
├── progress.md      # done log + cross-session handoff
├── architecture.md  # stable: structure; update only when structure changes
├── flow.md          # stable: flows / cross-module deps (skip if flow is trivial)
├── glossary.md      # stable: domain terms (skip if no jargon)
└── decisions.md     # history: ADR
```
Main rules file (CLAUDE.md / AGENTS.md) must contain: roles, two-phase work loop, memory summary, autoload hookup (see TEMPLATE B).

---

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

## Memory tiers (docs/; English filenames, content in working language; repo docs/ never scratch)
- Stable (read-only bg, rarely written): architecture.md / flow.md / glossary.md — read before any task; update only on structural/flow change or new term.
- Hot (per task): tasks.md (plan) / progress.md (after completion).
- History (on demand): decisions.md (ADR). Proposal: plans/<name>.md (draft→approved/rejected).
- Sub-agents are stateless; docs/ is the only shared handoff channel — anything downstream needs must be written there.

## Autoload (needs tool import support; else inline these summaries here)
@docs/glossary.md
@docs/architecture.md
- docs/ does NOT autoload by default. Autoload only lean summaries + short files (it pays tokens every session); never autoload architecture detail, decisions, or tasks/progress.

## Deterministic guards (enforce via your tool's hook mechanism, NOT prose)
- coder must not commit: a PreToolUse(Bash) hook blocks `git commit` / `git push` (the orchestrator commits after green).
- tester/verifier read-only: remove Edit/Write + a PreToolUse(Bash) hook blocks mutating commands (git commit|add|push, rm, file redirects, package installs).
- Claude Code: put these in the sub-agent's frontmatter `hooks:` (scoped to that agent only).
- No hook support → state explicitly that the restriction is advisory only.
- NOTE: "main agent never writes source" stays a prose discipline — the orchestrator holds all tools, so it can't be cleanly hook-enforced.
```

## TEMPLATE C — stable-tier file header (optional; prepend to each stable file)
```markdown
# (architecture / flow / glossary — pick one)
> Stable tier, read-only background. Update only on real structural/flow change or new term.

<fill in project content>
```
