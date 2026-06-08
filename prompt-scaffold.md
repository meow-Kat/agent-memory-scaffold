Auto-detect (scan, don't ask): which AI coding tool you're in (+version) and its conventions for (a) global/user config, (b) defining reusable sub-agent roles (file location + format + how to set per-agent tool permissions). Web-search the tool's docs only for facts you genuinely don't know; if you ARE the tool and already know the mechanism, state it and skip the search. Work at GLOBAL/user scope only (not any repo).

First, state this tool's AGENT vs SKILL distinction (cite a doc link), then confirm you will build the roles as AGENTS (independent executor, own context window, own tool permissions, dispatchable, returns a result) — NOT skills (a skill has no context isolation and can't be dispatched as a role = wrong category).

GOAL — CREATE (scaffold), not just audit. Create these THREE reusable, project-agnostic role agents at GLOBAL scope, in this tool's native agent format & location:
- coder   — the ONLY role that writes code.
- tester  — runs tests/lint/build; READ-ONLY.
- verifier — checks the diff against the plan + re-runs checks; READ-ONLY.
(Planning is the main/orchestrator agent's job — do NOT create a planner agent.)

RULES for creation —
1. IDEMPOTENT — never overwrite. For each agent: if a global definition already exists, leave it untouched and report "exists (skipped)". Only create the missing ones. If one exists but is MISCATEGORIZED (built as a skill, not an agent), do NOT delete it silently — report it + give the conversion, and create the correct agent alongside only if names won't collide.
2. LEAST PRIVILEGE (enforce in the agent definition, not prose):
   - coder: may edit/write files; must NOT commit/push (the orchestrator commits) — block `git commit` / `git push` via the tool's hook/guard mechanism.
   - tester & verifier: READ-ONLY — remove Edit/Write capability AND block mutating shell commands (git commit|add|push, rm, file redirects `>`/`>>`, package installs). On tools with a per-agent sandbox field (e.g. Codex `.codex/agents/<name>.toml` → `sandbox_mode = "read-only"`) use it — cleaner than a hook. On tools with per-agent frontmatter hooks (e.g. Claude Code) scope the guard to that agent. State the GOTCHA where relevant (e.g. Codex runs COMMAND hooks only; prompt/agent hooks are parsed but silently skipped).
3. EACH agent's instructions MUST state: stateless role → before acting, READ the project's main rules file + `docs/` (stable tier: architecture / conventions / flow / glossary; hot tier: tasks.md / progress.md; plans/ for in-flight work). docs/ is the only handoff channel — without reading it the agent flies blind. Keep each agent's instructions lean and role-scoped (coder writes; tester only runs checks and reports verbatim output; verifier only confirms diff-vs-plan + green, fixes nothing, returns a verdict).
4. If this tool has NO agent/sub-agent mechanism and skills are the closest thing, STOP and say so explicitly — give the best workaround, but do NOT pretend a skill is an agent or fake the creation.
5. Do NOT touch any repo, do NOT scaffold docs/ files, do NOT start dev work. Only create the three global role agents.

BEFORE WRITING, if the global write target is outside the current sandbox/approval scope, say what you need (e.g. permission to write `~/.codex/agents/` or `~/.claude/agents/`) and stop rather than failing silently.

OUTPUT in 繁體中文: detected tool + agent format/location (with doc link) → per role: created | exists (skipped) | miscategorized→converted, with the exact file path written → how least-privilege was enforced for each (sandbox field / removed tools / hook, name the mechanism) → confirmation each agent is told to read docs/ first → anything that needs your permission or couldn't be done + why. Keep each line short.
