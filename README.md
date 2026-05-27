# agent-memory-scaffold

> A tool-neutral Agent Skill that bootstraps a systematic memory & workflow structure into projects that don't have one.

[![skills.sh](https://skills.sh/b/<your-username>/agent-memory-scaffold)](https://skills.sh/<your-username>/agent-memory-scaffold)

AI coding agents forget everything between sessions. Without a structured place to keep plans, decisions, and project knowledge — plus a disciplined loop for using it — you end up re-explaining context every time, decisions get lost, and sub-agents have no shared handoff channel.

`agent-memory-scaffold` sets that structure up **once**. It detects what's missing in the current project, creates only the missing pieces from templates, then stops and hands control back to you. It never overwrites existing files, and it works on any agent that supports the Agent Skills standard.

## Install

```bash
npx skills add meow-Kat/agent-memory-scaffold
```

```bash
# Install to a specific agent
npx skills add meow-Kat/agent-memory-scaffold -a gemini-cli

# Install globally (available in every project)
npx skills add meow-Kat/agent-memory-scaffold -g
```

## What it does

On entering a project, the skill triggers if **any** of these are missing:

- the `docs/` memory layers
- a memory mechanism / work loop in the main rules file (`CLAUDE.md` / `AGENTS.md`)
- the `docs/memory.md` spec

It then:

1. **Detects** — checks each part of the target structure, marking Exists / Missing.
2. **Fills gaps only** — creates what's missing from templates; never touches existing files.
3. **Reports** — lists what it created, the `<fill-in>` spots you need to complete, and any mechanism (autoload / hook) that depends on your specific tool.
4. **Stops** — it does not start any dev work; it waits for you.

## What it scaffolds

```
docs/
├── plans/           # proposal drafts — one file per requirement (draft → approved/rejected)
├── tasks.md         # approved execution list
├── progress.md      # done log + cross-session handoff
├── architecture.md  # stable: structure
├── flow.md          # stable: flows / cross-module deps
├── glossary.md      # stable: domain terms
├── decisions.md     # history: ADRs
└── memory.md        # full spec of the memory mechanism
```

Plus a section in your main rules file (`CLAUDE.md` / `AGENTS.md`) defining roles, a two-phase work loop, a memory summary, and the autoload hookup.

Memory is organized in tiers:

- **Stable** (read-only background) — architecture, flow, glossary. Read before any task; updated only on a real structural change.
- **Hot** (per-task) — tasks and progress.
- **History** (on demand) — decisions / ADRs.

## Conventions

- **Tool-neutral.** Concepts like *main rules file*, *import*, *hook*, and *sub-agent* are mapped onto your agent's actual mechanisms. If something isn't supported, the closest substitute is used and called out.
- **Never overwrites.** Only missing pieces are added to an existing project.
- **Output language.** Filenames stay English.
- **Repo-relative.** All memory files go to the current repo's `docs/`, never a session scratch directory.

## Compatibility

Works with any agent that supports the [Agent Skills standard](https://agentskills.io) — Claude Code, Codex, Gemini CLI, Cursor, GitHub Copilot, OpenCode, and more. The skill uses only the core `name` / `description` frontmatter, so it degrades gracefully on agents with fewer features.

## License

Released under the MIT License.
