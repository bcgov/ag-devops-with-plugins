"""
Smoke tests for init-emerald-repo init.py

Verifies that running init.py with minimal required args:
  1. Exits with code 0
  2. Generates all expected files
  3. No unreplaced @@MARKER@@ tokens remain in any generated file
  4. Generated YAML files (Chart.yaml, values.yaml, values-env) are parseable

Run with:
    pytest tests/ -v
"""

import os
import re
import subprocess
import sys
import shutil
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.resolve()
INIT_PY = REPO_ROOT / "plugins" / "ag-devops" / "skills" / "init-emerald-repo" / "scripts" / "init.py"

EXPECTED_FILES = [
    ".github/workflows/ci.yml",
    ".github/workflows/cd.yml",
    ".github/CODEOWNERS",
    "gitops/Chart.yaml",
    "gitops/values.yaml",
    "gitops/values-dev.yaml",
    "gitops/values-test.yaml",
    "gitops/values-prod.yaml",
    "Makefile",
    ".gitignore",
    "AGENTS.md",
]

MINIMAL_ARGS = [
    "--project", "test-app",
    "--registry", "ghcr.io/bcgov-c",
    "--team", "test-team",
    "--team-handle", "test-team-github",
]

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def init_target_dir(tmp_path):
    """Provide an isolated temp directory for each test."""
    yield tmp_path
    # tmp_path is cleaned up automatically by pytest


def run_init(*extra_args, target_dir, expect_fail=False):
    """Run init.py with MINIMAL_ARGS + extra_args into target_dir."""
    cmd = [
        sys.executable, str(INIT_PY),
        *MINIMAL_ARGS,
        "--target-dir", str(target_dir),
        *extra_args,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    if not expect_fail and result.returncode != 0:
        pytest.fail(
            f"init.py failed (rc={result.returncode}):\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout, result.stderr, result.returncode


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_init_exits_zero(init_target_dir):
    """init.py with minimal required args should succeed."""
    _, _, rc = run_init(target_dir=init_target_dir)
    assert rc == 0


def test_init_generates_all_expected_files(init_target_dir):
    """All expected boilerplate files must be created."""
    run_init(target_dir=init_target_dir)
    for rel in EXPECTED_FILES:
        path = init_target_dir / rel
        assert path.exists(), f"Expected file not created: {rel}"


def test_init_no_unreplaced_markers(init_target_dir):
    """No @@MARKER@@ tokens should remain in any generated file."""
    run_init(target_dir=init_target_dir)
    marker_pattern = re.compile(r"@@\w+@@")
    offenders = []
    for rel in EXPECTED_FILES:
        path = init_target_dir / rel
        if path.exists():
            content = path.read_text(encoding="utf-8")
            remaining = marker_pattern.findall(content)
            if remaining:
                offenders.append(f"{rel}: {sorted(set(remaining))}")
    assert not offenders, "Unreplaced markers found:\n" + "\n".join(offenders)


def test_init_generated_yaml_is_valid(init_target_dir):
    """Chart.yaml, values.yaml, and per-env values files must be parseable YAML."""
    run_init(target_dir=init_target_dir)
    yaml_files = [
        "gitops/Chart.yaml",
        "gitops/values.yaml",
        "gitops/values-dev.yaml",
        "gitops/values-test.yaml",
        "gitops/values-prod.yaml",
    ]
    for rel in yaml_files:
        path = init_target_dir / rel
        assert path.exists(), f"Missing YAML file: {rel}"
        content = path.read_text(encoding="utf-8")
        try:
            list(yaml.safe_load_all(content))
        except yaml.YAMLError as exc:
            pytest.fail(f"Invalid YAML in {rel}:\n{exc}")


def test_init_project_name_in_generated_files(init_target_dir):
    """The project name should appear in Chart.yaml and values.yaml."""
    run_init(target_dir=init_target_dir)
    for rel in ("gitops/Chart.yaml", "gitops/values.yaml"):
        content = (init_target_dir / rel).read_text(encoding="utf-8")
        assert "test-app" in content, f"Project name 'test-app' not found in {rel}"


def test_init_no_overwrite_skips_existing(init_target_dir):
    """Running init twice without --overwrite should skip existing files."""
    run_init(target_dir=init_target_dir)
    # Stamp a sentinel in values.yaml
    values_path = init_target_dir / "gitops" / "values.yaml"
    original = values_path.read_text(encoding="utf-8")
    values_path.write_text("# SENTINEL\n" + original, encoding="utf-8")

    stdout, _, _ = run_init(target_dir=init_target_dir)
    # File should be skipped (not overwritten)
    assert values_path.read_text(encoding="utf-8").startswith("# SENTINEL"), (
        "Existing file was overwritten without --overwrite"
    )
    assert "skip" in stdout.lower()


def test_init_overwrite_replaces_existing(init_target_dir):
    """Running init with --overwrite should replace existing files."""
    run_init(target_dir=init_target_dir)
    values_path = init_target_dir / "gitops" / "values.yaml"
    values_path.write_text("# SENTINEL\n", encoding="utf-8")

    run_init("--overwrite", target_dir=init_target_dir)
    content = values_path.read_text(encoding="utf-8")
    assert not content.startswith("# SENTINEL"), "File was not overwritten with --overwrite"


def test_init_requires_project(init_target_dir):
    """Missing --project should fail."""
    cmd = [sys.executable, str(INIT_PY), "--registry", "ghcr.io/bcgov-c", "--target-dir", str(init_target_dir)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    assert result.returncode != 0, "Should fail when --project is missing"


def test_init_requires_registry(init_target_dir):
    """Missing --registry should fail."""
    cmd = [sys.executable, str(INIT_PY), "--project", "test-app", "--target-dir", str(init_target_dir)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    assert result.returncode != 0, "Should fail when --registry is missing"
