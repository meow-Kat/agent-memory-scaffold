# agent-memory-scaffold

> A tool-neutral Agent Skill that sets up — or audits — a systematic memory & workflow structure for AI-coding projects.

[![skills.sh](https://skills.sh/b/meow-Kat/agent-memory-scaffold)](https://skills.sh/meow-Kat/agent-memory-scaffold)

AI coding agents forget everything between sessions. Without a structured place to keep plans, decisions, and project knowledge — plus a disciplined loop for using it — you re-explain context every time, decisions get lost, and sub-agents have no shared handoff channel.

`agent-memory-scaffold` fixes that in one pass. On entering a project it detects whether the structure is missing or already there, then either **scaffolds** the missing pieces from templates or runs a **read-only audit** of what exists. It never overwrites your files, never starts dev work on its own, and works on any agent supporting the Agent Skills standard.

Two work-loop capabilities it wires into every scaffold stand out:

- **Difficulty-driven model tiering** — the orchestrator self-judges each task's difficulty and picks the model per-dispatch (on Claude Code: coder heavy → opus / standard → sonnet / light → haiku; tester one tier below; verifier fixed opus). No asking, with an optional per-project cap.
- **Wave-based parallel execution** — independent tasks (disjoint files, no shared deps) run as concurrent coder/tester lanes, capped at 4 per wave; one integration test then a single verifier wraps up the wave. Degrades losslessly to sequential where parallel dispatch isn't available.

## Install

```bash
npx skills add meow-Kat/agent-memory-scaffold       # current agent
npx skills add meow-Kat/agent-memory-scaffold -a claude-code   # a specific agent
npx skills add meow-Kat/agent-memory-scaffold -g    # globally, every project
```

## Two modes

The skill picks the mode during Detect — you don't.

**Scaffold** (missing) — creates only the missing items from templates, reports which fields you must fill, and flags which mechanisms (autoload / hooks) depend on your tool. Existing files are never touched. All six mandatory files (`architecture.md`, `conventions.md`, `decisions.md`, `flow.md`, `glossary.md`, and the project rules file) are always created — skipping at scaffold is path-dependent and the file then stays missing forever. The rules file is wired to read `docs/` so the memory actually gets consulted.

**Audit** (structure exists) — a read-only review that changes nothing. It grades each item **Has / Partial / Missing** per layer, gives a one-line fix, and surfaces the **top-3 highest-ROI gaps**. Checks cover: the six mandatory files present and populated; the hot tier (tasks/progress) maintained and matching the working tree; commit / source-write guards enforced by a real mechanism (not prose) and not over-blocking; the rules file lean (~80–120 lines, split targets on Claude Code include project-level `.claude/rules/`) with no redundant overrides; sub-agents actually using `docs/`; `detect-env.py` reachable; work-loop steering surviving compaction; roles operable (the tester really runs the documented test command); **model tiering** and **parallel/wave execution** present and operable; and (optional) a **session-start hot-tier injection** hook. Mechanisms a tool can't support are marked unsupported, not Missing.

Both modes **stop** afterward — they never roll on into a dev task.

## Precheck

The skill first confirms the work-loop roles exist as dispatchable sub-agents — **coder**, **tester**, **verifier** (the planner is always the main agent). It checks global/user scope first; if the roles live there they count as present. If they're missing everywhere it stops and asks you to set them up; if the tool has no sub-agent mechanism, the loop degrades to the main agent doing every step.

## What it scaffolds

```
docs/
├── plans/           # proposal drafts — one file per requirement (draft → approved/rejected)
├── tasks.md         # approved execution list (rolling)
├── progress.md      # done log + cross-session handoff
├── architecture.md  # stable: env fingerprint + structure (mandatory)
├── conventions.md   # stable: forward-binding rules / gotchas, autoloaded (mandatory stub)
├── flow.md          # stable: flows / cross-module deps (mandatory stub)
├── glossary.md      # stable: domain terms (mandatory stub)
└── decisions.md     # history: ADR log (mandatory stub)
```

Plus the project's main rules file (`CLAUDE.md` / `AGENTS.md`), in **Lean** mode (autoload + overrides, when a global rules file already supplies the work loop) or **Portable** mode (embeds `references/template-b.md` in full — roles, work loop, model tiering, wave execution, memory tiers, autoload, guards). Both wrap content in `agents-md-sync` region markers so `/agents-md-sync` stays idempotent.

For `architecture.md`, a bundled **`detect-env.py`** reads your manifests, version pins, and env vars (`pyproject.toml` / `package.json` / `Cargo.toml` / `go.mod` / `Gemfile`, `.python-version` / `.nvmrc`, `$CONDA_DEFAULT_ENV` …) to fill the Environment section deterministically — no LLM re-parsing each session. Whatever it can't detect, the skill asks for in one consolidated round: no blanks, no guesses.

Memory is tiered: **Stable** (architecture / conventions / flow / glossary — read before any task, rarely written), **Hot** (tasks / progress — read on session start), and **History** (decisions/ADRs + proposals under `plans/`).

## The work loop

A two-phase loop keeps planning and execution separate:

1. **Propose** — a new requirement becomes a draft in `docs/plans/`, then stops for discussion.
2. **Gate** — your approval is required; rejected proposals are marked.
3. **Execute** — split into `docs/tasks.md`, then coder → tester → verifier → all green → commit → update progress.
4. **On failure** — back to the coder. Retry caps: coder ↔ tester max 3 rounds (same failure twice → stop early); verifier runs once; 5 edits on one file → escalate.

On Claude Code the orchestrator self-judges difficulty and picks the model per-dispatch (model tiering, above), and may group independent tasks into **waves** run in parallel — concurrent coder/tester lanes (cap 4), then one integration test, then a single verifier per wave. Overlapping/dependent tasks stay sequential; parallelism degrades losslessly to sequential where unsupported.

## Deterministic guards

Discipline is enforced by your tool's real mechanism (hook / sandbox / tool-allowlist), not prose: the **coder can't commit** (a `PreToolUse(Bash)` hook blocks `git commit`/`push`; the orchestrator commits after green); the **tester writes tests only** (keeps edit/write for authoring tests and container wrappers, but commits/installs blocked — per-path where the tool supports it, else honest prose backstopped by the verifier); the **verifier is strictly read-only** (Edit/Write removed + a mutating-command hook). On Claude Code these live in per-agent frontmatter `hooks:`; on Codex via `sandbox_mode = "read-only"`; on Antigravity via the `agent.json` `toolNames` allowlist. Where a guard genuinely can't be enforced (e.g. the orchestrator holds all tools), the skill says so rather than pretending.

## Skill structure

```
agent-memory-scaffold/
├── SKILL.md                    # core: precheck, steps, audit criteria, conventions
├── detect-env.py               # bundled deterministic env-fingerprint script
├── references/
│   ├── mandatory-files.md      # per-file specs + templates for the six mandatories
│   └── template-b.md           # work-loop snippet to embed in Portable mode
├── prompt.md                   # workshop prompt: audit your GLOBAL setup (standalone)
├── prompt-scaffold.md          # workshop prompt: create the three role agents (standalone)
├── tests/                      # unittest fixtures for detect-env.py (stdlib only)
├── CHANGELOG.md                # dated change log (newest first)
├── README.md
└── LICENSE
```

The agent loads `SKILL.md` on invocation and reads `references/*` on demand, keeping the always-loaded surface small. The two `prompt*.md` files are standalone — you paste them into a tool yourself; the skill never loads them.

## Conventions

- **Tool-neutral** — *main rules file*, *import*, *hook*, *sub-agent* map onto your agent's mechanisms; unsupported ones fall back to the closest substitute, called out.
- **Never overwrites** — only missing pieces are added; Audit writes nothing.
- **English filenames + content**, except `docs/plans/*.md` bodies (the project's working language, for human review).
- **Repo-relative** — output goes to the current repo's `docs/`, never a scratch dir; if you're not in a repo, the skill asks where.

## Compatibility

Works with any agent supporting the [Agent Skills standard](https://agentskills.io) — Claude Code, Cursor, Codex, Antigravity, Gemini CLI, GitHub Copilot, OpenCode, and more. It uses only core `name` / `description` frontmatter, so it degrades gracefully. Hook-based guards require a tool with hook support; elsewhere they fall back to advisory rules.

## License

Released under the MIT License.
