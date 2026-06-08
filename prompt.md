Auto-detect (scan, don't ask): which AI coding tool you're in (+version) and its conventions for (a) global/user config, (b) defining reusable sub-agent roles, (c) global commands/skills/guards. Web-search the tool's docs only for facts you genuinely don't know; if you ARE the tool being audited and already know the mechanism, state it directly and skip the search. Map my target onto THIS tool's mechanisms. Scan global config ONLY (not any repo). Say what you can't detect — don't assume. At global scope there is no repo and no docs/ — audit the RULES/definitions, not produced files. For anything that only manifests inside a repo (plan drafts in docs/plans/, docs/ upkeep), verify the GLOBAL RULE specifies it correctly and mark runtime behavior as "unverifiable until run in a repo".

First, clarify TWO distinct mechanisms for this tool (state both + cite a doc link):
- AGENT / sub-agent = an independent executor with its OWN context window, own tool permissions, dispatchable by the main agent, returns a result. Give its exact file location + format.
- SKILL = a reusable knowledge/procedure pack the current agent loads on demand; NOT an independent executor, no context isolation. Give its exact file location + format.

Audit my GLOBAL setup. Mark each: Has / Partial / Missing.

TARGET (express in this tool's own conventions) —
- 3 reusable, project-agnostic roles — coder, tester, verifier — built as AGENTS, NOT skills (a skill can't be dispatched as a role and has no context isolation = wrong category). Planning is the main/orchestrator agent's job, NOT a subagent. Each agent must read the project's docs/ + main rules file before acting (stateless roles → docs/ is the only handoff channel).
- Least privilege: coder writes code; tester & verifier read-only (Edit/Write removed + a mutating-Bash hook).
- Personal cross-project preferences, kept lean.
- TWO-PHASE workflow rule, written INLINE in the global rules file (no external skill required — procedures inlined so the LLM can't "forget to invoke"):
  • Phase 1 — PROPOSE: new requirement → PLAN draft at `<repo>/docs/plans/<name>.md`, one file per requirement, with a status header (draft → approved / rejected). Then STOP and discuss. Do NOT create tasks, do NOT touch architecture, do NOT start coding yet.
  • Gate — human approval required. If rejected: mark rejected, stop.
  • Phase 2 — EXECUTE (only after approved): decompose into `tasks.md`, update `architecture.md` / `flow.md` if structure actually changes, append ADR to `decisions.md` on major trade-offs, promote any recurring/generalizable lesson or user correction into `conventions.md` (one-line rule, link `→ ADR-NNNN`; one-offs stay in `decisions.md`), run coder → tester → verifier loop with retry caps inline (e.g. coder <-> tester max 3 rounds; verifier runs once; 5 same-file edits → escalate).
- Session-start resumption rule: on every new session, if `docs/plans/*.md`, `tasks.md`, or `progress.md` exist → READ them all before acting (they don't autoload). Otherwise the agent re-decomposes or conflicts with in-flight work.
- Six mandatory `docs/` files (no conditional skip — skipping is path-dependent → permanently missing): `docs/architecture.md` (env fingerprint + structure), `docs/conventions.md` (forward-binding rules / gotchas, autoloaded; promoted from recurring decisions or user feedback — one-offs stay in `decisions.md`), `docs/decisions.md` (ADR stub), `docs/flow.md` (flows + cross-module deps stub), `docs/glossary.md` (domain terms stub), project rules file (`CLAUDE.md` / `AGENTS.md`). Hot tier (`tasks.md`, `progress.md`) and `plans/*` materialize during Phase 2; `progress.md` must be outcome summary, NOT a duplicate of `tasks.md` checkmarks.
- Generated files go to the CURRENT repo's `docs/` (repo-relative path), NEVER the session/conversation scratch dir — when not in a repo, ask where to write.
- Language split: ONLY `docs/plans/*.md` body is in working language (e.g. 繁體中文) for human review. Everything else — project rules file, all stable-tier docs (architecture / conventions / flow / glossary), `decisions.md` (structure AND ADR entry text), `tasks.md`, `progress.md` — is concise English so sub-agents can parse them.
- Deterministic env fingerprint: language / version / env manager / package manager / test framework / lint detection MUST offload to a deterministic script or hook the workflow CALLS (e.g. `detect-env.py` beside the scaffold skill). LLM re-parsing manifests each session is forbidden — drift-prone.
- Global permissions, reusable commands, skills, guards — whatever this tool supports.

CHECK —
1. For each of coder / tester / verifier: AGENT or SKILL? Flag any built as a skill as MISCATEGORIZED, with exact conversion steps (file location, required frontmatter, how to set permissions).
2. Do all 3 agents exist at global scope?
3. Is each told to read `docs/` first?
4. Are tester/verifier read-only (Edit/Write removed + mutating-Bash hook)?
5. Are personal prefs lean (no rules the model already follows)?
6. TWO-PHASE workflow inlined in the global rules file with explicit STOP + approval gate + retry caps as concrete numbers (not "see /execute skill" or similar)? If procedures live in external skills the LLM has to choose to invoke, flag as drift-prone.
7. Plan-output: does the GLOBAL RULE require plan drafts at repo-relative `<repo>/docs/plans/` (NOT scratch), one per requirement, with a status header, in 繁體中文? And does this tool have a built-in "plan" behavior hardwired to a scratch/ephemeral path, a fixed language, or auto-execute (skipping the discussion gate) that prompts can't override? If yes, say so. If the PROPOSE gate can be enforced deterministically (hook/tool setting), recommend it; if it genuinely can't (e.g. "a new requirement" is not a detectable event), say so plainly and treat prose discipline in the global rules file as the honest mechanism — don't invent a hook that can't exist.
8. Resumption rule: is "on session start → read `docs/plans/`, `tasks.md`, `progress.md` before any action" explicitly in the global rules file?
9. Six-mandatory rule: does the global setup mandate all six `docs/` files (architecture / conventions / decisions / flow / glossary / project rules file) as no-skip-at-scaffold? Or do conditional-skip phrases like "skip if trivial" / "skip if no jargon" / "skip if no recurring rule" persist (which lead to permanent under-documentation)?
10. Language rule: is "ONLY `plans/*.md` is working language; everything else English" explicit, or does vague "file content in working language" persist?
11. Deterministic env detection: is there a script/hook the scaffold path actually CALLS (state its file path)? Confirm the scaffold skill REFERENCES the script (e.g. an explicit `python3 .../detect-env.py` line in SKILL.md), not just describes detection steps in prose. LLM-only manifest re-reading = drift-prone, flag.

If this tool genuinely has NO agent/sub-agent mechanism and skills are the closest thing, say so explicitly and give the best workaround — don't pretend a skill is an agent.

OUTPUT in 繁體中文: detected tool + agent-vs-skill mechanisms (with doc links) → each role's current category + fix for any miscategorized → two-phase workflow + resumption rule status → env-detection script status → six-mandatory + language-split status → other items status + one-line fix → top fixes → cite a link where you used web facts. Keep each item to one line; don't restate the rule text verbatim.
