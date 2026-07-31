#!/usr/bin/env python3
"""PreToolUse(Edit|Write|NotebookEdit): restrict the tester subagent's writes to test files.

Referenced only from tester.md frontmatter, so it runs exclusively while the
tester is active. The tester authors/edits tests; source code stays the
coder's. Reads the proposed target path from stdin JSON and exits 2 with
stderr unless the path looks like a test file or lives under a test directory.

Design: fail closed, generic patterns (no per-repo config). If a legit test
path is blocked, report it and let the main agent or human decide.
"""

import json
import re
import sys
from pathlib import PurePosixPath

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_input = data.get("tool_input", {})
path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
if not path:
    sys.exit(0)

p = PurePosixPath(path.replace("\\", "/"))
name = p.name.lower()
parts = [part.lower() for part in p.parts]

TEST_DIRS = {"test", "tests", "spec", "specs", "__tests__", "testing"}

TEST_FILE_PATTERNS = [
    r"^test_.*\.py$",  # pytest
    r".*_test\.py$",  # pytest alt
    r"^conftest\.py$",  # pytest fixtures/config
    r".*_test\.go$",  # go test
    r".*tests?\.php$",  # phpunit (FooTest.php / FooTests.php)
    r".*\.(test|spec)\.[a-z]+$",  # jest/vitest/mocha (foo.test.ts, foo.spec.js)
    r".*_spec\.rb$",  # rspec
    r".*test.*\.ipynb$",  # test notebooks
]

is_test = any(part in TEST_DIRS for part in parts[:-1]) or any(
    re.match(pat, name) for pat in TEST_FILE_PATTERNS
)

if not is_test:
    print(
        f"[harness-hook] BLOCKED: write outside test paths — the tester writes TEST files only.\n"
        f"  Path: {path}\n"
        f"  Source changes belong to the coder; report this instead of writing it.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
