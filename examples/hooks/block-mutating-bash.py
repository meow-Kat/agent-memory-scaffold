#!/usr/bin/env python3
"""PreToolUse(Bash): enforce read-only Bash for the tester / verifier subagents.

Referenced only from the tester.md and verifier.md frontmatter, so it runs
exclusively while those agents are active. Reads the proposed command from
stdin JSON and exits 2 with stderr if it mutates files, the repo, the
environment, or installs packages. Read / test / inspection commands pass.

Design: fail closed. These two roles are read-only by contract; if a legit
command is blocked, report it and let the main agent or human run it.
"""

import json
import re
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

cmd = data.get("tool_input", {}).get("command", "")
if not cmd:
    sys.exit(0)

MUTATING = [
    # match rm only in command position (start, after ; & | ( ) or a quote) so
    # flags like `docker run --rm ...` are not mistaken for a file delete
    (r"""(?:^|[\s;&|()'"`])rm\b""", "rm (delete files)"),
    (r"\brmdir\b", "rmdir"),
    (r"\bmv\b", "mv (move/rename)"),
    (r"\bcp\b", "cp (can overwrite)"),
    (r"\btouch\b", "touch (create/alter files)"),
    (r"\bmkdir\b", "mkdir"),
    (r"\btruncate\b", "truncate"),
    (r"\btee\b", "tee (writes files)"),
    (r"\bdd\b", "dd"),
    (r"\bchmod\b", "chmod"),
    (r"\bchown\b", "chown"),
    (r"\bln\b", "ln (create links)"),
    (r"\bsed\b[^|]*\s-i", "sed -i (in-place edit)"),
    (r"\bperl\b[^|]*\s-i", "perl -i (in-place edit)"),
    (r"\bfind\b[^|]*-delete", "find -delete"),
    (r"\bfind\b[^|]*-exec", "find -exec"),
    # output redirection to a real file (allow /dev/null and fd dup like 2>&1)
    (r"(^|\s)\d*>>?\s*(?!/dev/null|&)\S", "output redirection to a file"),
    # mutating git subcommands (git diff/status/log/show/blame/rev-parse stay allowed)
    (
        r"\bgit\s+(commit|add|push|reset|checkout|switch|restore|rebase|merge|stash|"
        r"clean|rm|mv|apply|cherry-pick|revert|tag|am|pull|fetch|init|clone|remote)\b",
        "mutating git subcommand",
    ),
    (r"\bgit\s+branch\s+-[dD]\b", "git branch delete"),
    # package / environment mutations (conda run is intentionally NOT matched)
    (r"\b(pip|pip3)\s+(install|uninstall)\b", "pip install/uninstall"),
    (
        r"\b(npm|pnpm|yarn)\s+(install|i|add|remove|ci|update|upgrade)\b",
        "node package mutation",
    ),
    (r"\bpoetry\s+(add|remove|install|update)\b", "poetry mutation"),
    (r"\bconda\s+(install|remove|create|update|env)\b", "conda env mutation"),
    (
        r"\b(brew|apt|apt-get|yum|dnf|pacman)\s+(install|remove|upgrade|update)\b",
        "system package mutation",
    ),
    (r"\bcargo\s+(add|install|remove)\b", "cargo mutation"),
    (r"\bgo\s+(install|get)\b", "go module mutation"),
]

for pattern, label in MUTATING:
    if re.search(pattern, cmd):
        print(
            f"[harness-hook] BLOCKED: {label} — this agent is read-only.\n"
            f"  Command: {cmd}\n"
            f"  Report this instead of running it; the coder (or the user) makes changes.",
            file=sys.stderr,
        )
        sys.exit(2)

sys.exit(0)
