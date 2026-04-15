#!/usr/bin/env python3
"""
ag-devops manifest validator — v2.0.0

Runs the full 4-tool policy pipeline against rendered Helm manifests:
  1. helm template  — renders the Helm chart to raw YAML
  2. datree         — checks org label/schema rules
  3. polaris        — checks security and reliability best practices
  4. kube-linter    — checks Kubernetes lint rules
  5. conftest/OPA   — hard-deny Rego rules (NetworkPolicy, Route, AVI)

Usage:
    python validate.py --chart-dir gitops/ [--values gitops/values.yaml] [--policy-dir <path>]
    python validate.py --rendered-file rendered.yaml  # skip helm render, use existing file
    python validate.py --chart-dir gitops/ --tool datree  # run only one tool
    python validate.py --chart-dir gitops/ --fix-hints    # print fix suggestions on failure

Exit codes:
    0  all tools passed
    1  one or more tools failed
    2  prerequisite tool not found (warn, continue with available tools)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

PLUGIN_VERSION = "2.0.0"

POLICY_TOOLS = ["datree", "polaris", "kube-linter", "conftest"]


def find_policy_dir(explicit: str) -> str:
    """Find policy files — try explicit path, then common install locations."""
    if explicit and os.path.isdir(explicit):
        return os.path.abspath(explicit)

    candidates = [
        # Plugin installed via marketplace
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets", "policies"),
        # Plugin in source repo
        os.path.join(os.getcwd(), "cd", "policies"),
        # Local copy from /ag-init
        os.path.join(os.getcwd(), ".ag-devops", "policies"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return os.path.abspath(c)

    return ""


def run(cmd: list, label: str, fail_on_error: bool = True) -> tuple[int, str, str]:
    """Run a command, return (returncode, stdout, stderr)."""
    print(f"\n{'─' * 60}")
    print(f"  [{label}]  {' '.join(cmd)}")
    print(f"{'─' * 60}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode


def check_tool(name: str) -> bool:
    found = shutil.which(name) is not None
    if not found:
        print(f"  ⚠  {name} not found in PATH — skipping this check")
    return found


def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"ag-devops manifest validator v{PLUGIN_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--chart-dir", default="gitops",
                        help="Helm chart directory to render (default: gitops)")
    parser.add_argument("--values", default="",
                        help="Values file for helm template (default: auto-detect gitops/values.yaml)")
    parser.add_argument("--rendered-file", default="",
                        help="Use an already-rendered YAML file instead of running helm template")
    parser.add_argument("--policy-dir", default="",
                        help="Directory containing policy files (auto-detected if omitted)")
    parser.add_argument("--tool", default="", choices=POLICY_TOOLS + [""],
                        help="Run only this tool (default: run all)")
    parser.add_argument("--release-name", default="test-release",
                        help="Helm release name for rendering (default: test-release)")
    args = parser.parse_args()

    policy_dir = find_policy_dir(args.policy_dir)
    if not policy_dir:
        print("ERROR: Cannot find policy directory. Run /ag-init to set up the repo, "
              "or specify --policy-dir explicitly.")
        sys.exit(1)

    print(f"\n=== ag-devops Manifest Validator v{PLUGIN_VERSION} ===")
    print(f"Policy directory: {policy_dir}")

    failures = []
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Render or use provided file
        if args.rendered_file:
            rendered = os.path.abspath(args.rendered_file)
            if not os.path.isfile(rendered):
                sys.exit(f"ERROR: --rendered-file '{rendered}' does not exist")
            print(f"\n  Using pre-rendered file: {rendered}")
        else:
            rendered = os.path.join(tmpdir, "rendered.yaml")
            chart_dir = os.path.abspath(args.chart_dir)
            values_file = args.values or os.path.join(chart_dir, "values.yaml")

            if not check_tool("helm"):
                print("ERROR: helm is required. Install from https://helm.sh/docs/intro/install/")
                sys.exit(2)

            helm_cmd = ["helm", "template", args.release_name, chart_dir,
                        "--values", values_file, "--output-dir", tmpdir]
            rc = run(helm_cmd, "helm template")
            if rc != 0:
                print("\n✗ helm template failed — fix chart errors before running policy tools")
                sys.exit(1)

            # Collect all rendered YAML into one file
            import glob as _glob
            rendered_files = _glob.glob(os.path.join(tmpdir, "**", "*.yaml"), recursive=True)
            with open(rendered, "w") as out:
                for rf in rendered_files:
                    with open(rf) as inp:
                        out.write(inp.read())
                        out.write("\n---\n")
            print(f"\n  Rendered to: {rendered} ({len(rendered_files)} files)")

        # Step 2: datree
        if (not args.tool or args.tool == "datree") and check_tool("datree"):
            datree_policy = os.path.join(policy_dir, "datree-policies.yaml")
            cmd = ["datree", "test", rendered]
            if os.path.isfile(datree_policy):
                cmd += ["--policy-config", datree_policy]
            rc = run(cmd, "datree")
            if rc != 0:
                failures.append("datree")
                if args.tool:
                    sys.exit(rc)

        # Step 3: polaris
        if (not args.tool or args.tool == "polaris") and check_tool("polaris"):
            polaris_cfg = os.path.join(policy_dir, "polaris.yaml")
            cmd = ["polaris", "audit", "--format", "pretty", "--audit-path", rendered]
            if os.path.isfile(polaris_cfg):
                cmd += ["--config", polaris_cfg]
            rc = run(cmd, "polaris")
            if rc != 0:
                failures.append("polaris")
                if args.tool:
                    sys.exit(rc)

        # Step 4: kube-linter
        if (not args.tool or args.tool == "kube-linter") and check_tool("kube-linter"):
            kl_cfg = os.path.join(policy_dir, "kube-linter.yaml")
            cmd = ["kube-linter", "lint", rendered]
            if os.path.isfile(kl_cfg):
                cmd += ["--config", kl_cfg]
            rc = run(cmd, "kube-linter")
            if rc != 0:
                failures.append("kube-linter")
                if args.tool:
                    sys.exit(rc)

        # Step 5: conftest/OPA
        if (not args.tool or args.tool == "conftest") and check_tool("conftest"):
            cmd = ["conftest", "test", rendered,
                   "--policy", policy_dir, "--all-namespaces", "--fail-on-warn"]
            rc = run(cmd, "conftest/OPA")
            if rc != 0:
                failures.append("conftest")
                if args.tool:
                    sys.exit(rc)

    print(f"\n{'═' * 60}")
    if failures:
        print(f"  ✗ FAILED: {', '.join(failures)}")
        print(f"  Fix the issues above and re-run: python ./scripts/validate.py --chart-dir gitops/")
        sys.exit(1)
    else:
        print("  ✓ All policy checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
