---
name: agent-memory-scaffold
description: Use when entering a project to set up or check its systematic memory/management structure (docs/ memory layers, main-rules-file work loop, two-phase workflow). Missing pieces → scaffold from templates. Already exists → read-only AUDIT, grading each item Has/Partial/Missing per layer (project/docs) and reporting the highest-ROI gaps. Never overwrites existing files; never starts dev work.
---

# Project memory scaffold

> **Scope note:** "memory" here means the project's own `docs/` shared-handoff layers (architecture / tasks / progress / decisions …) — this is project docs/, **NOT** the `~/.claude/.../memory/` auto-memory system. They are different mechanisms; this skill never touches auto-memory.

Set up — or audit — the systematic memory/management structure for an AI-coding project. Tool-neutral: map "main rules file" / "import" / "hook" / "sub-agent" onto your tool's actual mechanisms; if a mechanism is unsupported, use the closest substitute and say so. Two modes, chosen in Detect: **scaffold** when pieces are missing, **audit** (read-only) when the structure already exists.

## Precheck — work-loop roles
The work loop dispatches coder/tester/verifier. Confirm they exist as dispatchable sub-agents in your tool. Planner is ALWAYS the main agent (orchestrator), never a sub-agent — do not look for a planner agent.
- Check the global/user agent scope FIRST — these roles are commonly defined there already; if so, treat them as present and do NOT ask the user to recreate them per-project.
- Genuinely missing everywhere (no global, no project) → tell the user to set those roles up first (their global/user agent scope) and STOP; scaffolding docs without the roles leaves the loop unrunnable.
- No sub-agent mechanism in the tool → say so; the loop degrades to the main agent doing all steps itself.

## Steps
1. Detect: for each item in "Target structure" (docs/ layers + the main rules file carrying the work loop & memory mechanism) → mark Has / Partial / Missing (tag layer: project / docs).
2. Branch:
   - Mostly Missing → SCAFFOLD: create only the missing items from the templates. NEVER overwrite an existing file. **All five mandatories must be created — no skip**: `docs/architecture.md`, `docs/decisions.md`, `docs/flow.md`, `docs/glossary.md`, AND the project rules file (`CLAUDE.md` / `AGENTS.md`). Skipping at scaffold is path-dependent — once skipped, the threshold to "go back and create later" is always too high, so the file stays missing forever. Greenfield → create with template + TBD placeholder; Phase 2 (execute) fills as content materializes. **See `references/mandatory-files.md` for per-file spec + template.**
   - Exists / maintained → AUDIT (read-only, make NO changes), grading against "Target structure":
     a. **Mandatory files present & properly populated**:
        - project rules file (CLAUDE.md / AGENTS.md): exists, has `agents-md-sync` region markers + work loop (linked or embedded)
        - `docs/architecture.md`: Environment section has no blank fields / `<fill>` placeholders; Structure not stuck at TBD if first task has shipped
        - `docs/decisions.md`: stub present (header + ADR template comment)
        - `docs/flow.md`: stub present (Main flows + Cross-module dependencies headers); Main flows not stuck at TBD if flows have materialized
        - `docs/glossary.md`: stub present (Terms header); Terms not stuck at TBD if domain terms have entered code or docs
     b. **Hot tier maintained**: tasks.md / progress.md actively updated; progress.md is outcome summary, NOT duplicate of tasks.md checkmarks
     c. **Guards real**: commit / source-write restrictions hook-enforced, not prose
     d. **Main rules file lean** (~80–120 lines); over → flag what to split into docs/
     e. **docs/ used as shared memory**, or sub-agents flying blind?
     f. **No redundant overrides**: project-level role/rule duplicating global (delete unless LOGIC, not just data, differs)
     g. **`detect-env.py` reachable** from the skill folder (if architecture.md was scaffolded by this skill)
     h. **Work-loop steering survives compaction**: a UserPromptSubmit-equivalent hook re-injects a one-line reminder every prompt to route code work through the two-phase loop + coder/tester/verifier — present, or the loop is silently forgotten in long sessions. Verify the hook exists; do NOT create it here (it lives in the tool's hook config, not docs/).
3. Report:
   - SCAFFOLD → what you created + which `<fill-in>` spots the user must complete + which mechanisms (autoload / hook) depend on the tool and need confirming.
   - AUDIT → Has/Partial/Missing table (with layer tag) + a one-line fix each + the top-3 highest-ROI gaps.
4. STOP: in either mode, do not proceed into any dev task — wait for the user.

## Conventions
- Filenames English. Content language:
  - **繁體中文 (working language) — `docs/plans/*.md` body ONLY**. Plans are human-review documents.
  - **English (concise) — everything else**: project rules file (CLAUDE.md / AGENTS.md), stable-tier docs (`architecture.md`, `flow.md`, `glossary.md`), `decisions.md` (structure AND ADR entry text), `tasks.md`, `progress.md`. Sub-agents read these on every task — ambiguous prose or mixed language costs comprehension.
- Write all output to the current repo's docs/ (repo-relative), NEVER a session/scratch dir. Not a repo → ask the user where.
- All tier / autoload / read-write mechanics live in `references/template-b.md` — the single source. Don't restate them elsewhere.

## Target structure (also the AUDIT baseline)
```
docs/
├── plans/           # proposal drafts, one file per requirement, status: draft→approved/rejected
├── tasks.md         # approved execution list (rolling)
├── progress.md      # done log + cross-session handoff
├── architecture.md  # stable: env fingerprint + structure (mandatory)
├── flow.md          # stable: flows / cross-module deps (mandatory stub)
├── glossary.md      # stable: domain terms (mandatory stub)
└── decisions.md     # history: ADR log (mandatory stub)
```
Main rules file (CLAUDE.md / AGENTS.md) must contain: roles, two-phase work loop, memory summary, autoload hookup. See `references/template-b.md` for the snippet to embed (Portable mode).

## Mandatory files (read spec before scaffolding)

All five mandatories must be scaffolded — never skipped (path-dependent: skipped → permanently missing). Per-file specs + templates live in `references/mandatory-files.md`; read the relevant section before creating the file.

| File | Purpose | Reference |
|---|---|---|
| `docs/architecture.md` | env fingerprint (calls `detect-env.py`) | `references/mandatory-files.md` |
| `docs/decisions.md` | ADR log stub | `references/mandatory-files.md` |
| `docs/flow.md` | flows + cross-module dependencies | `references/mandatory-files.md` |
| `docs/glossary.md` | domain terms | `references/mandatory-files.md` |
| project rules file (CLAUDE.md / AGENTS.md) | Lean or Portable mode | `references/mandatory-files.md` (Portable embeds `references/template-b.md`) |
