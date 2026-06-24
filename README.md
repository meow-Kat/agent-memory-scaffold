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

**Scaffold** (pieces are missing) — creates only the missing items from templates, reports which fields you must fill, and flags which mechanisms (autoload / hooks) depend on your specific tool and need confirming. Existing files are never touched. All six mandatory files (`architecture.md`, `conventions.md`, `decisions.md`, `flow.md`, `glossary.md`, and the project rules file) are always created — no conditional skip, because skipping at scaffold is path-dependent and the file stays missing forever. The rules file is wired to read docs/ (autoload + a "read docs/ before any task" instruction) so the scaffolded memory actually gets consulted.

**Audit** (structure already exists) — a read-only review that changes nothing. Grading against the target structure, it marks each item **Has / Partial / Missing** per layer, gives a one-line fix for each, and surfaces the **top-3 highest-ROI gaps**. Checks include:

- Are the six mandatory files present and properly populated? (architecture.md Environment section filled with real values; conventions.md stub + autoloaded; decisions.md stub; flow.md stub; glossary.md stub; project rules file with `agents-md-sync` region markers + work loop linked or embedded + docs/ autoloaded/read-instructed)
- Is the hot tier maintained? (tasks.md / progress.md actively updated; progress.md is an outcome summary, not a duplicate of tasks.md checkmarks)
- Are commit / source-write restrictions enforced by a real mechanism (hook / sandbox / tool-allowlist) rather than prose — and not over-blocking? (the tester must still be able to write test files and run the documented test command, container wrapper included; verified by running it, not by reading the config)
- Is the main rules file lean (~80–120 lines)?
- Are sub-agents really using `docs/` as shared memory, or flying blind?
- Any project-level rule that just duplicates a global one?
- Is `detect-env.py` reachable from the skill folder?
- Does work-loop steering survive compaction? (a UserPromptSubmit-equivalent hook re-injects the two-phase routing every prompt; tools without such a mechanism are marked unsupported, not Missing)
- Are the roles operable, not just present? (the tester is dispatched to actually run the project's documented test/lint command — presence of the agent ≠ ability to do its job)
- Does the hot tier match the working tree? (tasks.md / progress.md cross-checked against `git status` / `git diff`; drift makes sub-agents redo or conflict with in-flight work)
- Is model tiering present and operable? (the work loop defines self-judged difficulty + coder/tester → opus/sonnet/haiku + verifier fixed opus, with the Claude Code dispatch `model` override; non-Claude tools are marked unsupported, not Missing)

In both modes it **stops** afterward and waits for you — it never rolls on into a dev task.

## Precheck

Before anything else, the skill confirms the work-loop roles exist as dispatchable sub-agents in your tool: **coder**, **tester**, **verifier**. (The planner is always the main agent / orchestrator — never a sub-agent.) It checks the global / user agent scope first — if these roles already live there, they're treated as present and you're not asked to recreate them per-project. Only if they're genuinely missing everywhere does the skill stop and ask you to set them up first. If your tool has no sub-agent mechanism at all, it says so, and the loop degrades to the main agent doing every step itself.

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

Plus the project's main rules file (`CLAUDE.md` / `AGENTS.md`) in one of two modes:

- **Lean** — autoload + project-specific overrides only; assumes the global rules file already supplies the work loop. The skill picks Lean automatically when a global rules file with the work loop is detected.
- **Portable** — embeds `references/template-b.md` in full (roles, work loop, memory tiers, autoload, deterministic guards) so the project is self-contained.

Both modes wrap content in `agents-md-sync` region markers (`<!-- harness:shared:start -->` …) from day one so future `/agents-md-sync` runs are idempotent.

For `architecture.md` specifically, a bundled **`detect-env.py`** reads your project's manifests (`pyproject.toml` / `package.json` / `Cargo.toml` / `go.mod` / `Gemfile`), version pins (`.python-version` / `.nvmrc` / `.tool-versions`), and env vars (`$CONDA_DEFAULT_ENV` / `$VIRTUAL_ENV`) to fill the Environment section deterministically — no LLM re-parsing each session. Whatever the script can't detect (run command, build / CI command, etc.) the skill asks for in one consolidated round: no blanks, no guesses.

Memory is organized in tiers:

- **Stable** (read-only background) — architecture, conventions, flow, glossary. Read before any task; updated only on a real structural/flow change, a new term, or a new recurring rule. `conventions.md` holds forward-binding rules / gotchas promoted from `decisions.md` or user feedback (one-offs stay in decisions).
- **Hot** (per-task) — tasks and progress. Read on session start to resume in-flight work; they don't autoload.
- **History** — decisions / ADRs (stub mandatory; entries appended on demand) plus proposals under `plans/`.

## The work loop

The template wires up a two-phase loop so planning and execution stay separated:

1. **Propose** — a new requirement becomes a draft in `docs/plans/`, then stops for discussion.
2. **Gate** — it needs your approval; rejected proposals are marked as such.
3. **Execute** — split into `docs/tasks.md`, then coder → tester → verifier → all green → commit → update progress.
4. **On failure** — back to the coder with the error. Retry caps: coder ↔ tester max 3 rounds (same failure twice → stop early); verifier runs once; 5 edits on one file → escalate.

On Claude Code the orchestrator self-judges each task's difficulty and dynamically picks the model per-dispatch — coder heavy → opus, standard → sonnet, light → haiku; tester one tier below (matching coder on heavy/security-sensitive work); the verifier is fixed on opus. No asking — grading and model choice are self-judged, with an optional `architecture.md` `Model tiers` cap. On non-Claude tools this degrades to the tool's default / advisory.

## Deterministic guards

Discipline that matters is enforced by your tool's real mechanism (hook / sandbox / tool-allowlist), not by hoping the agent behaves:

- The **coder can't commit** — a `PreToolUse(Bash)` hook blocks `git commit` / `git push`; the orchestrator commits after green.
- The **tester writes tests only** — it keeps edit/write so it can author tests and run container wrappers (e.g. `docker run --rm …`), but commits and package installs are blocked. Where the tool supports per-path guards, writes are restricted to the test dirs; elsewhere "tests only" is honest prose, backstopped by the verifier.
- The **verifier is strictly read-only** — Edit/Write removed, plus a hook blocking mutating commands (commits, `rm`, file redirects, package installs).
- On Claude Code these live in the sub-agent's frontmatter `hooks:`, scoped to that agent only; on Codex the verifier uses `sandbox_mode = "read-only"`; on Antigravity (agy) the per-agent guard is the `toolNames` allowlist in `agent.json` — a "read-only" line in the prompt while write tools stay listed is a fake guard.

Where a guard genuinely can't be enforced — e.g. "the main agent never writes source," since the orchestrator holds all tools — the skill says so honestly rather than pretending. If your tool has no hook support, restrictions are flagged as advisory only.

## Skill structure

```
agent-memory-scaffold/
├── SKILL.md                    # core: precheck, steps, audit criteria, conventions, mandatory-file pointers
├── detect-env.py               # bundled deterministic env-fingerprint script
├── references/
│   ├── mandatory-files.md      # per-file specs + templates for the six mandatories
│   └── template-b.md           # work-loop snippet to embed in Portable mode
├── prompt.md                   # workshop prompt: audit your GLOBAL agent setup (standalone, not loaded by the skill)
├── prompt-scaffold.md          # workshop prompt: create the three global role agents (standalone, not loaded by the skill)
├── tests/                      # unittest fixtures for detect-env.py (stdlib only)
├── README.md
└── LICENSE
```

The agent loads `SKILL.md` on invocation and reads `references/*` on demand when actually creating files, keeping the always-loaded surface small. The two `prompt*.md` files are standalone workshop prompts you paste into a tool yourself — one audits your global setup against this skill's target, the other scaffolds the coder / tester / verifier role agents at global scope; the skill never loads them.

## Conventions

- **Tool-neutral.** Concepts like *main rules file*, *import*, *hook*, and *sub-agent* are mapped onto your agent's actual mechanisms; if something isn't supported, the closest substitute is used and called out.
- **Never overwrites.** Only missing pieces are added; Audit mode writes nothing at all.
- **English filenames; English content by default, working language only for plan drafts.** All scaffolded files (project rules file, architecture.md, conventions.md, flow.md, glossary.md, decisions.md, tasks.md, progress.md) are concise English so sub-agents can parse them. The single exception is `docs/plans/*.md` body, which is written in the project's working language (e.g. 繁體中文) for human review.
- **Repo-relative.** All output goes to the current repo's `docs/`, never a session scratch directory. If you're not in a repo, the skill asks where to write.

## Compatibility

Works with any agent that supports the [Agent Skills standard](https://agentskills.io) — Claude Code, Cursor, Codex, Antigravity, Gemini CLI, GitHub Copilot, OpenCode, and more. The skill uses only the core `name` / `description` frontmatter, so it degrades gracefully on agents with fewer features. Hook-based guards require a tool that supports hooks (e.g. Claude Code); elsewhere they fall back to advisory rules.

## License

Released under the MIT License.
