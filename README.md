# agent-memory-scaffold

> A tool-neutral Agent Skill that sets up — or audits — a systematic memory & workflow structure for AI-coding projects.

[![skills.sh](https://skills.sh/b/meow-Kat/agent-memory-scaffold)](https://skills.sh/meow-Kat/agent-memory-scaffold)

AI coding agents forget everything between sessions. Without a structured place to keep plans, decisions, and project knowledge — plus a disciplined loop for using it — you re-explain context every time, decisions get lost, and sub-agents have no shared handoff channel.

`agent-memory-scaffold` fixes that in one pass. On entering a project it figures out whether the structure is missing or already there, then either **scaffolds** the missing pieces from templates or runs a **read-only audit** of what exists. It never overwrites your files, never starts dev work on its own, and works on any agent that supports the Agent Skills standard.

## Install

```bash
npx skills add meow-Kat/agent-memory-scaffold
```

```bash
# Install to a specific agent
npx skills add meow-Kat/agent-memory-scaffold -a claude-code

# Install globally (available in every project)
npx skills add meow-Kat/agent-memory-scaffold -g
```

## Two modes

The skill decides which mode to run during its Detect step — you don't pick.

**Scaffold** (structure is missing) — creates only the missing pieces from templates, reports which `<fill-in>` spots you need to complete, and flags which mechanisms (autoload / hooks) depend on your specific tool and need confirming. Existing files are never touched.

**Audit** (structure already exists) — a read-only review that changes nothing. It grades each item **Has / Partial / Missing** per layer, gives a one-line fix for each, and surfaces the **top-3 highest-ROI gaps**. The audit checks things like: does the main rules file actually carry the work loop and point to the real `docs/` filenames; is `progress.md` genuinely updated on commit; are commit/write restrictions enforced by a real guard rather than just prose; is the main rules file lean enough; and are sub-agents really using `docs/` as shared memory or flying blind.

In both modes it **stops** afterward and waits for you — it does not roll on into a dev task.

## Precheck

Before anything else, the skill confirms the work-loop roles exist as dispatchable sub-agents in your tool: **coder**, **tester**, **verifier**. (The planner is always the main agent / orchestrator — never a sub-agent.) If those roles are missing it tells you to set them up first and stops, since scaffolding the docs without runnable roles would leave the loop unrunnable. If your tool has no sub-agent mechanism at all, it says so, and the loop degrades to the main agent doing every step itself.

## What it scaffolds

```
docs/
├── plans/           # proposal drafts — one file per requirement (draft → approved/rejected)
├── tasks.md         # approved execution list (rolling)
├── progress.md      # done log + cross-session handoff
├── architecture.md  # stable: structure
├── flow.md          # stable: flows / cross-module deps
├── glossary.md      # stable: domain terms
├── decisions.md     # history: ADRs
└── memory.md        # full spec of the memory mechanism — also the yardstick Audit grades against
```

Plus a section in your main rules file (`CLAUDE.md` / `AGENTS.md`) defining roles, the two-phase work loop, a memory summary, and the autoload hookup.

Memory is organized in tiers:

- **Stable** (read-only background) — architecture, flow, glossary. Read before any task; updated only on a real structural change.
- **Hot** (per-task) — tasks and progress.
- **History** (on demand) — decisions / ADRs.

## The work loop

The templates wire up a two-phase loop so planning and execution stay separated:

1. **Propose** — a new requirement becomes a draft in `docs/plans/`, then stops for discussion.
2. **Gate** — it needs your approval; rejected proposals are marked as such.
3. **Execute** — split into `docs/tasks.md`, then coder → tester → verifier → all green → commit → update progress.
4. **On failure** — back to the coder with the error, max 3 retries, then stop and report.

## Deterministic guards

Discipline that matters is enforced by your tool's hook mechanism, not by hoping the agent behaves:

- The **coder can't commit** — a `PreToolUse(Bash)` hook blocks `git commit` / `git push`; the orchestrator commits after green.
- **Tester and verifier are read-only** — Edit/Write removed, plus a hook blocking mutating commands.
- On Claude Code these live in the sub-agent's frontmatter `hooks:`, scoped to that agent only.

Where a guard genuinely can't be enforced — e.g. "the main agent never writes source," since the orchestrator holds all tools — the skill says so honestly rather than pretending. If your tool has no hook support, restrictions are flagged as advisory only.

## Conventions

- **Tool-neutral.** Concepts like *main rules file*, *import*, *hook*, and *sub-agent* are mapped onto your agent's actual mechanisms; if something isn't supported, the closest substitute is used and called out.
- **Never overwrites.** Only missing pieces are added; Audit mode writes nothing at all.
- **English filenames.** File content stays in the project's working language.
- **Repo-relative.** All memory files go to the current repo's `docs/`, never a session scratch directory.

## Compatibility

Works with any agent that supports the [Agent Skills standard](https://agentskills.io) — Claude Code, Cursor, Codex, Antigravity, Gemini CLI, GitHub Copilot, OpenCode, and more. The skill uses only the core `name` / `description` frontmatter, so it degrades gracefully on agents with fewer features. Hook-based guards require a tool that supports hooks (e.g. Claude Code); elsewhere they fall back to advisory rules.

## License

Released under the MIT License.
