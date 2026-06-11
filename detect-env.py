#!/usr/bin/env python3
"""
detect-env.py — deterministic env fingerprint for agent-memory-scaffold.

Reads repo manifests + env vars; emits JSON on stdout. No prompts, no side effects.

Usage: python3 detect-env.py [<repo-root>]   # defaults to cwd
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def read(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def detect_python(root: Path) -> dict | None:
    pyproject = read(root / "pyproject.toml")
    requirements = read(root / "requirements.txt")
    setup_py = read(root / "setup.py")
    env_yml = read(root / "environment.yml")
    py_ver = read(root / ".python-version")
    tool_ver = read(root / ".tool-versions")

    if not any([pyproject, requirements, setup_py, env_yml, py_ver, tool_ver]):
        return None

    version = None
    if py_ver:
        version = py_ver.strip()
    elif tool_ver:
        m = re.search(r"^python\s+(\S+)", tool_ver, re.M)
        if m:
            version = m.group(1)
    elif pyproject:
        # line-anchored so dependency keys like `ipython = "^8.0"` don't match
        m = re.search(
            r'^\s*(?:requires-python|python)\s*=\s*"([^"]+)"', pyproject, re.M
        )
        if m:
            version = m.group(1)

    if env_yml:
        pkg = "conda + environment.yml"
    elif pyproject and "[tool.poetry]" in pyproject:
        pkg = "poetry"
    elif pyproject and ("[tool.uv]" in pyproject or (root / "uv.lock").exists()):
        pkg = "uv"
    elif pyproject:
        pkg = "pyproject (pip)"
    elif requirements:
        pkg = "pip + requirements.txt"
    elif setup_py:
        pkg = "setup.py"
    else:
        pkg = None

    blob = " ".join(s for s in (pyproject, requirements, setup_py) if s)

    def named(tool: str) -> bool:
        # word-boundary match so e.g. "black" doesn't hit "blackjack"
        return re.search(rf"\b{re.escape(tool)}\b", blob) is not None

    test_fw = next(
        (fw for fw in ("pytest", "unittest", "nose", "tox") if named(fw)), None
    )
    lints = [
        t for t in ("ruff", "black", "flake8", "pylint", "mypy", "isort") if named(t)
    ] or None

    manifests = [
        n
        for n, c in [
            ("pyproject.toml", pyproject),
            ("requirements.txt", requirements),
            ("setup.py", setup_py),
            ("environment.yml", env_yml),
            (".python-version", py_ver),
            (".tool-versions", tool_ver),
        ]
        if c is not None
    ]

    return {
        "name": "Python",
        "version": version,
        "package_manager": pkg,
        "test_framework": test_fw,
        "lint_format": " + ".join(lints) if lints else None,
        "manifests": manifests,
    }


def detect_node(root: Path) -> dict | None:
    pkg_txt = read(root / "package.json")
    nvmrc = read(root / ".nvmrc")
    if not pkg_txt:
        return None
    try:
        data = json.loads(pkg_txt)
    except json.JSONDecodeError:
        return None

    version = None
    engines = data.get("engines")
    if isinstance(engines, dict):
        version = engines.get("node")
    if not version and nvmrc:
        version = nvmrc.strip()

    lockfile = next(
        (
            lk
            for lk in ("pnpm-lock.yaml", "yarn.lock", "bun.lockb", "package-lock.json")
            if (root / lk).exists()
        ),
        None,
    )
    pkg_mgr = {
        "pnpm-lock.yaml": "pnpm",
        "yarn.lock": "yarn",
        "bun.lockb": "bun",
        "package-lock.json": "npm",
    }.get(lockfile, "npm")

    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    deps_str = " ".join(deps.keys())
    test_fw = next(
        (
            fw
            for fw in ("jest", "vitest", "mocha", "playwright", "cypress")
            if fw in deps_str
        ),
        None,
    )
    lints = [
        t for t in ("eslint", "prettier", "biome", "typescript") if t in deps_str
    ] or None

    manifests = [n for n in ("package.json", ".nvmrc") if (root / n).exists()]
    if lockfile:
        manifests.append(lockfile)

    return {
        "name": "Node",
        "version": version,
        "package_manager": pkg_mgr,
        "test_framework": test_fw,
        "lint_format": " + ".join(lints) if lints else None,
        "manifests": manifests,
    }


def detect_go(root: Path) -> dict | None:
    mod = read(root / "go.mod")
    if not mod:
        return None
    m = re.search(r"^go\s+(\S+)", mod, re.M)
    return {
        "name": "Go",
        "version": m.group(1) if m else None,
        "package_manager": "go modules",
        "test_framework": "go test",
        "lint_format": None,
        "manifests": ["go.mod"],
    }


def detect_rust(root: Path) -> dict | None:
    cargo = read(root / "Cargo.toml")
    if not cargo:
        return None
    m = re.search(r'rust-version\s*=\s*"([^"]+)"', cargo)
    return {
        "name": "Rust",
        "version": m.group(1) if m else None,
        "package_manager": "cargo",
        "test_framework": "cargo test",
        "lint_format": "clippy + rustfmt",
        "manifests": ["Cargo.toml"],
    }


def detect_ruby(root: Path) -> dict | None:
    gem = read(root / "Gemfile")
    if not gem:
        return None
    ruby_ver = (read(root / ".ruby-version") or "").strip() or None
    return {
        "name": "Ruby",
        "version": ruby_ver,
        "package_manager": "bundler",
        "test_framework": None,
        "lint_format": None,
        "manifests": [n for n in ("Gemfile", ".ruby-version") if (root / n).exists()],
    }


def detect_env_manager(root: Path) -> str | None:
    conda = os.environ.get("CONDA_DEFAULT_ENV")
    if conda and conda != "base":
        return f"conda env `{conda}` (active)"
    venv = os.environ.get("VIRTUAL_ENV")
    if venv:
        return f"venv `{venv}` (active)"
    if (root / "environment.yml").exists():
        return "conda (per environment.yml — confirm env name)"
    if (root / ".venv").is_dir():
        return "venv `.venv` (present but inactive — confirm activation)"
    py_ver = read(root / ".python-version")
    if py_ver:
        return f"pyenv `{py_ver.strip()}`"
    nvmrc = read(root / ".nvmrc")
    if nvmrc:
        return f"nvm `{nvmrc.strip()}`"
    return None


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()

    detectors = (detect_python, detect_node, detect_go, detect_rust, detect_ruby)
    languages = [r for r in (d(root) for d in detectors) if r]

    env_manager = detect_env_manager(root)

    asks: list[str] = []
    if not env_manager:
        asks.append("Env manager (which conda env / venv path / pyenv is in use)")
    if not languages:
        asks.append("Language(s) in use (no manifest detected)")
    elif len(languages) > 1:
        names = ", ".join(lang["name"] for lang in languages)
        asks.append(f"Primary language (detected: {names})")
    asks.append("Run / start command")
    asks.append("Build / CI command (or confirm none)")
    if not any(lang.get("test_framework") for lang in languages):
        asks.append("Test framework (or confirm none)")
    if not any(lang.get("lint_format") for lang in languages):
        asks.append("Lint / format (or confirm none)")

    out = {
        "root": str(root),
        "languages": languages,
        "env_manager": env_manager,
        "asks": asks,
    }
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
