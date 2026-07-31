# Mandatory file specs

Per-file specs and templates for the six mandatory files agent-memory-scaffold creates during SCAFFOLD. Read the relevant section before creating the corresponding file.

## architecture.md — mandatory

Always create `docs/architecture.md` during scaffold. It is the env fingerprint coder / tester / verifier need before they can run.

### Detect (deterministic — call the bundled script)
`detect-env.py` ships in this skill's own folder — resolve the path from wherever the skill is installed, don't hardcode a tool-specific prefix (Claude Code: `~/.claude/skills/agent-memory-scaffold/`; Codex: `~/.codex/skills/agent-memory-scaffold/`; Antigravity (agy): `~/.gemini/antigravity-cli/skills/agent-memory-scaffold/`; project-scoped installs live under `.claude/skills/` or `.codex/skills/`).
```bash
python3 <skill-dir>/detect-env.py [<repo-root>]
```
Reads `pyproject.toml` / `requirements.txt` / `setup.py` / `environment.yml` / `package.json` (+ lockfile) / `go.mod` / `Cargo.toml` / `Gemfile`, plus version pins (`.python-version`, `.nvmrc`, `.tool-versions`, `.ruby-version`) and env vars (`$CONDA_DEFAULT_ENV`, `$VIRTUAL_ENV`). Emits JSON:
```json
{ "root": "...", "languages": [{"name", "version", "package_manager", "test_framework", "lint_format"}], "env_manager": "...", "asks": [...] }
```
This script is the ONLY source of truth for detection — do not re-parse manifests in the LLM, it drifts session to session.

### Then ask once for what the script couldn't detect
Use the `asks[]` array from the JSON verbatim as the consolidated question set. No blanks. No guesses.

### Test framework field — must be a runnable command
Record the **exact command the tester can paste and run**, including the container wrapper if the host runtime can't run it natively (e.g. `docker run --rm … vendor/bin/phpunit`). A bare framework name ("phpunit", "pytest") is insufficient — the tester will improvise and drift, and a containerized run may trip an over-broad write-guard. If host ≠ runtime, capture the wrapper here so the loop stays runnable.

### Model tiers field — optional override, default auto
Default `auto` = the orchestrator self-judges opus/sonnet per task difficulty (Claude Code; see `references/template-b.md` Model tiering). Fill this only to cap cost, pin, or honor an account limit (e.g. "heavy also only sonnet", or an effort cap/pin like "coder xhigh" / "verifier high"). It is NOT detected by `detect-env.py` and is NOT asked — leave it `auto` unless the user has a reason to override.

### Frontend / UI field — declares browser-verification eligibility
`none` = no frontend; screens/UI never enter the loop and are never browser-verified. Otherwise, one line: how to launch the UI for browser testing — start command + URL + a mock/clean-DB note (seeded data, test account, etc.). NOT detected by `detect-env.py` (launch semantics aren't inferable from manifests) — it folds into the same consolidated ask round as the other `asks[]` items, not a separate question.

### Structure section
- Plan exists (`docs/plans/*.md` listing affected files / modules) → infer from it.
- Greenfield (no plan) → write `TBD — filled by Phase 2 (execute) after the first task`.

### Template (paste verbatim)
```markdown
# Architecture
> Stable tier, read-only background. Update only on real structural change.

## Environment
- Language / version:
- Env manager (conda / venv / pyenv / nvm / system):
- Package manager:
- Test framework (or "none"):    # full runnable command incl. container wrapper, not just the framework name
- Lint / Format (or "none"):
- Run / start command:
- Build / CI command (or "none"):
- Model tiers (or "auto"):    # OPTIONAL override; auto = orchestrator self-judges opus/sonnet per difficulty (Claude Code); may also cap/pin effort (e.g. "coder xhigh")
- Frontend / UI (or "none"):    # launch cmd + URL + mock/clean-DB note for browser verification; NOT detected by detect-env.py — filled in the consolidated ask round

## Structure


## External dependencies
- Services / APIs:
- Required env vars:
- Other:
```

## Project rules file (CLAUDE.md / AGENTS.md) — mandatory

Create the main rules file during scaffold — `CLAUDE.md` for Claude Code, `AGENTS.md` for Codex AND Antigravity (agy reads `AGENTS.md` at both its global and workspace customization roots), both (region-marker shared) for cross-tool. Sub-agents read this before acting; without it they fly blind.

### Mode
- Global rules file exists with the work loop → **Lean**: only autoload + project overrides; assume global supplies work loop / roles / tiers.
- Otherwise → **Portable**: embed the content of `references/template-b.md` in full.

### Wrap in `agents-md-sync` region markers
`<!-- harness:shared:start -->` … `<!-- harness:shared:end -->` for tool-neutral content; empty `harness:claude:*` and `harness:codex:*` regions below. Keeps `/agents-md-sync` idempotent from day one. NOTE: regions only control what `/agents-md-sync` copies — they do NOT scope what a tool reads. Codex and Antigravity both read the whole `AGENTS.md`, so tool-specific differences (e.g. guard mechanisms) belong as per-tool bullets ("Codex: …", "agy: …") inside the shared region, not in separate regions.

### Lean template (paste verbatim — drop the title; the directory is the identity)
```markdown
<!-- harness:shared:start -->
## Autoload
@docs/architecture.md
@docs/conventions.md
<!-- optional: @docs/glossary.md if jargon exists -->

Claude Code alternative: project-level `.claude/rules/` with `paths:` frontmatter can replace or complement the `@` lines above for path-scoped, conditional loading — see `references/template-b.md` Autoload for the mechanics.

## Refer to
- Work loop, roles, memory tiers, guards: see global CLAUDE.md / AGENTS.md.
- **Before any task, READ docs/ memory** — stable tier (architecture / conventions / flow / glossary) + hot tier (tasks.md / progress.md on session start) + check plans/ for in-flight work. docs/ is the only shared handoff channel; sub-agents fly blind without it.
- Project-specific overrides go below — keep this file lean (~80 lines).
<!-- harness:shared:end -->

<!-- harness:claude:start -->
<!-- Claude Code-specific notes; delete if unused -->
<!-- harness:claude:end -->

<!-- harness:codex:start -->
<!-- Codex-specific notes; delete if unused -->
<!-- harness:codex:end -->
```

### Portable template
Wrap the content of `references/template-b.md` inside `<!-- harness:shared:start -->` / `<!-- harness:shared:end -->`. Add empty `harness:claude:*` and `harness:codex:*` regions below.

### Existing-file handling (never overwrite)
- Has region markers + shared region empty → write content into shared region.
- Has region markers + shared region non-empty → AUDIT-report only; do not modify.
- No region markers → propose `/agents-md-sync` first; do NOT auto-add markers without consent.

## decisions.md — mandatory (stub)

History tier — stub mandatory even with zero entries; there's no "no history" state. Phase 2 (execute) prepends ADR entries as they arise.

### Template (paste verbatim)
```markdown
# Decisions
> Append-only log. Newest entry first. One entry per major trade-off (architecture, framework, protocol, library, …).
> Status flow: proposed → accepted → (later) superseded by ADR-NNNN | deprecated.

<!-- ADR template — copy, fill, prepend:

## ADR-NNNN: <title>
**Date**: <YYYY-MM-DD>
**Status**: proposed | accepted

### Context
### Decision
### Consequences
### Alternatives considered
-->

## Entries
<!-- newest first -->
```

## flow.md — mandatory (stub)

Stable tier — stub mandatory even with no flows yet. Skipping at scaffold leaves it permanently missing; the threshold to "go back and create later" never gets crossed. Greenfield → use the template with `TBD — filled by Phase 2 as flows materialize` under "Main flows"; leave "Cross-module dependencies" empty.

### Template (paste verbatim)
```markdown
# Flow
> Stable tier, read-only background. Update only on real flow / cross-module change.

## Main flows
<one entry per top-level user-visible behavior; trigger → steps → outcome>

### <flow name>
- Trigger:
- Steps:
  1.
  2.
- Outcome:

## Cross-module dependencies
<one-directional arrows; flag any cycles>

- `<module A>` → `<module B>` (purpose)
```

## glossary.md — mandatory (stub)

Stable tier — stub mandatory even with zero terms. Skipping at scaffold leaves it permanently missing; the threshold to "go back and create later" never gets crossed. Greenfield → use the template with `TBD — filled as domain terms appear in code or docs` under "## Terms".

### Template (paste verbatim)
```markdown
# Glossary
> Stable tier, read-only background. Add a term only when it appears in code or docs.

## Terms

### <Term>
<one-sentence definition in project context>
<optional: acronym expansion / external reference>
```

## conventions.md — mandatory (stub)

Stable tier, **autoloaded** — distilled, forward-binding rules / gotchas / exception-cases the AI must follow on every task. Distinct from `decisions.md` (one-off decisions + full context, backward-looking): a convention is the rule **promoted from a recurring or generalizable decision**, deduplicated and rewritten as the code evolves. Not every ADR becomes a convention — only the ones that should steer FUTURE work; one-offs stay in `decisions.md`. Stub mandatory even with zero rules (path-dependent: skipped → permanently missing). Autoloaded, so keep it scannable — promote only rules with real recurrence.

Each entry: an imperative do/don't + a one-line why (+ optional `→ ADR-NNNN` link to the decision that established it).

### Template (paste verbatim)
```markdown
# Conventions
> Stable tier, autoloaded. Forward-binding rules / gotchas the AI must follow on every task.
> Each rule: imperative do/don't + one-line why (+ optional → ADR-NNNN).
> Promote here only recurring / generalizable lessons; one-offs stay in decisions.md.

## Rules
TBD — filled as recurring rules emerge (promoted from decisions.md or user feedback)

<!-- example shape:
### Security — XSS / DOM-XSS
Fix at the source (server-side escape / server-render), NOT client-side sanitizers or
JS DOM-building. Snyk taint analysis flags `.html()`/`.append()`/`innerHTML` as sinks
regardless of `.text()` safety, so dynamic fixes only relocate the finding. → ADR-NNNN
-->
```
