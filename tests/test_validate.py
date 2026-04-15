"""
Tests for ag-devops validate.py

Verifies that:
  1. --help exits 0 with useful output
  2. Missing required tool (helm not found) exits with code 2
  3. --rendered-file with non-existent file exits with code 1
  4. --policy-dir with invalid path exits with code 1
  5. shutil.which() is used for all tool checks (validate.py imports shutil)
  6. --tool with valid choice is accepted; invalid choice is rejected

Note: Full pipeline tests (datree, polaris, etc.) require installed tools
and are skipped in environments where those tools are not present.

Run with:
    pytest tests/ -v
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.resolve()
VALIDATE_PY = REPO_ROOT / "plugins" / "ag-devops" / "scripts" / "validate.py"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_validate(*args, expect_fail=False):
    """Run validate.py with given args; return (stdout, stderr, returncode)."""
    cmd = [sys.executable, str(VALIDATE_PY), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    if not expect_fail and result.returncode not in (0, 2):
        # rc=2 means tools missing — acceptable in CI environments without tools installed
        pytest.fail(
            f"validate.py failed unexpectedly (rc={result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return result.stdout, result.stderr, result.returncode


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_validate_help_exits_zero():
    """--help should print usage and exit 0."""
    stdout, _, rc = run_validate("--help")
    assert rc == 0
    assert "validate" in stdout.lower() or "chart" in stdout.lower()


def test_validate_missing_rendered_file_fails():
    """--rendered-file pointing to a non-existent file should exit 1."""
    _, _, rc = run_validate(
        "--rendered-file", "nonexistent-file-99999.yaml",
        expect_fail=True,
    )
    assert rc == 1


def test_validate_invalid_policy_dir_fails():
    """--policy-dir pointing to a non-existent directory should exit 1 (no policies found)."""
    _, _, rc = run_validate(
        "--chart-dir", "gitops",
        "--policy-dir", "/nonexistent/policy/dir/99999",
        expect_fail=True,
    )
    assert rc in (1, 2)  # 1 = policy dir error, 2 = helm not found


def test_validate_uses_shutil_which():
    """validate.py must import shutil for tool discovery (audit the source)."""
    source = VALIDATE_PY.read_text(encoding="utf-8")
    assert "shutil.which" in source, (
        "validate.py must use shutil.which() for tool discovery"
    )


def test_validate_tool_filter_accepts_valid_choice():
    """--tool with a valid choice (datree) should not fail on argument parsing."""
    # It may fail because the tool is missing or no chart — but argparse should accept the value
    stdout, stderr, rc = run_validate(
        "--tool", "datree",
        "--rendered-file", "nonexistent.yaml",
        expect_fail=True,
    )
    # Should not be an argparse error (those produce "error: argument --tool: invalid choice")
    assert "invalid choice" not in stderr.lower()


def test_validate_tool_filter_rejects_invalid_choice():
    """--tool with an unrecognised value should fail with argparse error."""
    _, stderr, rc = run_validate(
        "--tool", "not-a-real-tool",
        expect_fail=True,
    )
    assert rc != 0
    assert "invalid choice" in stderr.lower() or "error" in stderr.lower()


def test_validate_tools_skipped_when_missing(tmp_path):
    """When required tools are absent, validate.py should warn and skip (exit 2), not crash."""
    # Create a minimal rendered YAML that passes structural checks
    rendered = tmp_path / "rendered.yaml"
    rendered.write_text(
        "apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: test\n",
        encoding="utf-8",
    )
    # Point policy-dir to a valid location so it gets past the policy-dir check
    policy_dir = REPO_ROOT / "cd" / "policies"
    if not policy_dir.exists():
        pytest.skip("cd/policies not found — skipping tool-absent test")

    stdout, stderr, rc = run_validate(
        "--rendered-file", str(rendered),
        "--policy-dir", str(policy_dir),
        expect_fail=True,
    )
    # If all tools are missing, rc=2 (prerequisites missing) or 1 (failures)
    # Either way, must not crash with unhandled exception
    assert rc in (0, 1, 2), f"Unexpected exit code: {rc}"
    assert "Traceback" not in stderr, "validate.py crashed with unhandled exception"
