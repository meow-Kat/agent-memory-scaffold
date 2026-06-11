"""Fixture tests for detect-env.py (stdlib only — run: python3 -m unittest discover tests).

The script is invoked as a subprocess, same as the skill does, and the JSON
output is asserted. CONDA_DEFAULT_ENV / VIRTUAL_ENV are stripped so results
don't depend on the shell the tests run from.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "detect-env.py"


def run_detect(root: Path) -> dict:
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("CONDA_DEFAULT_ENV", "VIRTUAL_ENV")
    }
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(root)],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return json.loads(proc.stdout)


class DetectEnvTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name: str, content: str):
        (self.root / name).write_text(content, encoding="utf-8")

    def lang(self, out: dict, name: str) -> dict:
        matches = [lng for lng in out["languages"] if lng["name"] == name]
        self.assertEqual(len(matches), 1, f"expected one {name} entry: {out}")
        return matches[0]

    def test_empty_repo(self):
        out = run_detect(self.root)
        self.assertEqual(out["languages"], [])
        self.assertIsNone(out["env_manager"])
        self.assertTrue(any("Language" in a for a in out["asks"]))

    def test_python_pyproject(self):
        self.write(
            "pyproject.toml",
            '[project]\nname = "demo"\nrequires-python = ">=3.11"\n'
            '[project.optional-dependencies]\ndev = ["pytest", "ruff"]\n',
        )
        out = run_detect(self.root)
        py = self.lang(out, "Python")
        self.assertEqual(py["version"], ">=3.11")
        self.assertEqual(py["package_manager"], "pyproject (pip)")
        self.assertEqual(py["test_framework"], "pytest")
        self.assertEqual(py["lint_format"], "ruff")

    def test_ipython_dep_is_not_a_version(self):
        # regression: unanchored regex used to read `ipython = "^8.0"` as the version
        self.write(
            "pyproject.toml",
            '[tool.poetry]\nname = "demo"\n'
            '[tool.poetry.dependencies]\nipython = "^8.0"\n',
        )
        out = run_detect(self.root)
        py = self.lang(out, "Python")
        self.assertIsNone(py["version"])
        self.assertEqual(py["package_manager"], "poetry")

    def test_poetry_python_version_line(self):
        self.write(
            "pyproject.toml",
            '[tool.poetry]\nname = "demo"\n'
            '[tool.poetry.dependencies]\npython = "^3.12"\n',
        )
        out = run_detect(self.root)
        self.assertEqual(self.lang(out, "Python")["version"], "^3.12")

    def test_lint_word_boundary(self):
        # "blackjack" must not register the black formatter
        self.write("requirements.txt", "blackjack==1.0\n")
        out = run_detect(self.root)
        self.assertIsNone(self.lang(out, "Python")["lint_format"])

    def test_node_package_json(self):
        self.write(
            "package.json",
            json.dumps(
                {
                    "engines": {"node": ">=20"},
                    "devDependencies": {"jest": "^29", "eslint": "^9"},
                }
            ),
        )
        self.write("package-lock.json", "{}")
        out = run_detect(self.root)
        node = self.lang(out, "Node")
        self.assertEqual(node["version"], ">=20")
        self.assertEqual(node["package_manager"], "npm")
        self.assertEqual(node["test_framework"], "jest")
        self.assertIn("eslint", node["lint_format"])

    def test_go_mod(self):
        self.write("go.mod", "module demo\n\ngo 1.22\n")
        out = run_detect(self.root)
        go = self.lang(out, "Go")
        self.assertEqual(go["version"], "1.22")
        self.assertEqual(go["test_framework"], "go test")

    def test_venv_dir_detected_inactive(self):
        (self.root / ".venv").mkdir()
        out = run_detect(self.root)
        self.assertIn("inactive", out["env_manager"])

    def test_asks_cover_undetected_fields(self):
        self.write("go.mod", "module demo\n\ngo 1.22\n")
        out = run_detect(self.root)
        self.assertTrue(any("Run / start" in a for a in out["asks"]))
        self.assertTrue(any("Lint" in a for a in out["asks"]))
        # test framework detected (go test) → must NOT be asked
        self.assertFalse(any("Test framework" in a for a in out["asks"]))


if __name__ == "__main__":
    unittest.main()
