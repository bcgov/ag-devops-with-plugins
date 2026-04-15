#!/usr/bin/env python3
"""
Initialize an application repository for OpenShift Emerald deployment.

Generates the full boilerplate scaffolding:
  .github/workflows/ci.yml
  .github/workflows/cd.yml
  .github/CODEOWNERS
  gitops/Chart.yaml
  gitops/values.yaml
  gitops/values-dev.yaml
  gitops/values-test.yaml
  gitops/values-prod.yaml
  Makefile
  .gitignore  (appended)

All output is written to the target directory (default: current working directory).
Existing files are updated in-place rather than overwritten if --no-overwrite is set.

Usage
-----
python plugins/ag-devops/skills/init-emerald-repo/scripts/init.py \\
  --project my-app \\
  --registry ghcr.io/bcgov-c \\
  --team my-team \\
  --team-handle my-team-github \\
  --namespace-dev my-app-dev \\
  --namespace-test my-app-test \\
  --namespace-prod my-app-prod \\
  --solution-path ./MySolution.sln \\
  --test-folders "tests/MyApp.Tests" \\
  --main-component web-api \\
  --target-dir .
"""
import argparse
import os
import sys


TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "templates")

ENV_LABELS = {
    "dev":  "development",
    "test": "test",
    "prod": "production",
}

ENV_REPLICAS = {
    "dev":  "1",
    "test": "1",
    "prod": "2",
}

ENV_ROUTE_ENABLED = {
    "dev":  "true",
    "test": "true",
    "prod": "true",
}


def load_template(filename: str) -> str:
    path = os.path.join(TEMPLATES_DIR, filename)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def render(tpl: str, replacements: dict) -> str:
    for marker, value in replacements.items():
        tpl = tpl.replace(marker, value)
    return tpl


def write_file(path: str, content: str, overwrite: bool) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    if os.path.exists(path) and not overwrite:
        print(f"  skip (exists): {path}")
        return
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"  ✓  {path}")


def append_gitignore(target_dir: str, additions: str) -> None:
    gi_path = os.path.join(target_dir, ".gitignore")
    marker = "# Helm"
    if os.path.exists(gi_path):
        with open(gi_path, "r") as fh:
            existing = fh.read()
        if marker in existing:
            print(f"  skip (already has Helm section): {gi_path}")
            return
        with open(gi_path, "a") as fh:
            fh.write("\n" + additions)
        print(f"  ✓  appended Helm entries to {gi_path}")
    else:
        with open(gi_path, "w") as fh:
            fh.write(additions)
        print(f"  ✓  {gi_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize an application repository for OpenShift Emerald deployment"
    )
    parser.add_argument("--project", required=True,
                        help="Short project name, e.g. my-app (used as Helm release name)")
    parser.add_argument("--registry", required=True,
                        help="Container image registry, e.g. ghcr.io/bcgov-c")
    parser.add_argument("--team", default="<team-name>",
                        help="Team name for the owner label in values.yaml")
    parser.add_argument("--team-handle", default="<team-github-handle>",
                        help="GitHub team handle for CODEOWNERS, e.g. my-team")
    parser.add_argument("--namespace-dev", default="",
                        help="OpenShift namespace for dev environment, e.g. my-app-dev")
    parser.add_argument("--namespace-test", default="",
                        help="OpenShift namespace for test environment, e.g. my-app-test")
    parser.add_argument("--namespace-prod", default="",
                        help="OpenShift namespace for prod environment, e.g. my-app-prod")
    parser.add_argument("--solution-path", default="./MySolution.sln",
                        help=".NET solution file path (default: ./MySolution.sln)")
    parser.add_argument("--test-folders", default="tests/MyApp.Tests",
                        help="Space-separated test project folder(s)")
    parser.add_argument("--main-component", default="web-api",
                        help="Primary workload name for CD rollout verification (default: web-api)")
    parser.add_argument("--target-dir", default=".",
                        help="Root directory of the target repository (default: .)")
    parser.add_argument("--ag-devops-ref", default="v2.0.0",
                        help="ag-devops git ref to use in CD pipeline (default: v2.0.0)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing files (default: skip existing)")
    args = parser.parse_args()

    td = args.target_dir
    ns_dev  = args.namespace_dev  or f"{args.project}-dev"
    ns_test = args.namespace_test or f"{args.project}-test"
    ns_prod = args.namespace_prod or f"{args.project}-prod"

    base_replacements = {
        "@@PROJECT@@":        args.project,
        "@@REGISTRY@@":       args.registry,
        "@@TEAM@@":           args.team,
        "@@TEAM_HANDLE@@":    args.team_handle,
        "@@NAMESPACE_DEV@@":  ns_dev,
        "@@NAMESPACE_TEST@@": ns_test,
        "@@NAMESPACE_PROD@@": ns_prod,
        "@@SOLUTION_PATH@@":  args.solution_path,
        "@@TEST_FOLDERS@@":   args.test_folders,
        "@@MAIN_COMPONENT@@": args.main_component,
        "@@AG_DEVOPS_REF@@":  getattr(args, "ag_devops_ref", "v2.0.0"),
    }

    print("\n=== Initializing Emerald repo structure ===\n")

    # .github/workflows/ci.yml
    ci_content = render(load_template("ci.tpl.yml"), base_replacements)
    write_file(os.path.join(td, ".github", "workflows", "ci.yml"), ci_content, args.overwrite)

    # .github/workflows/cd.yml
    cd_content = render(load_template("cd.tpl.yml"), base_replacements)
    write_file(os.path.join(td, ".github", "workflows", "cd.yml"), cd_content, args.overwrite)

    # .github/CODEOWNERS
    co_content = render(load_template("CODEOWNERS.tpl"), base_replacements)
    write_file(os.path.join(td, ".github", "CODEOWNERS"), co_content, args.overwrite)

    # gitops/Chart.yaml
    chart_content = render(load_template("Chart.tpl.yaml"), base_replacements)
    write_file(os.path.join(td, "gitops", "Chart.yaml"), chart_content, args.overwrite)

    # gitops/values.yaml
    values_content = render(load_template("values.tpl.yaml"), base_replacements)
    write_file(os.path.join(td, "gitops", "values.yaml"), values_content, args.overwrite)

    # gitops/values-dev.yaml / test / prod
    for env in ("dev", "test", "prod"):
        env_replacements = {
            **base_replacements,
            "@@ENV@@":          env,
            "@@ENV_LABEL@@":    ENV_LABELS[env],
            "@@REPLICAS@@":     ENV_REPLICAS[env],
            "@@ROUTE_ENABLED@@": ENV_ROUTE_ENABLED[env],
        }
        env_content = render(load_template("values-env.tpl.yaml"), env_replacements)
        write_file(os.path.join(td, "gitops", f"values-{env}.yaml"), env_content, args.overwrite)

    # Makefile
    makefile_content = render(load_template("Makefile.tpl"), base_replacements)
    write_file(os.path.join(td, "Makefile"), makefile_content, args.overwrite)

    # .gitignore
    gitignore_additions = load_template("gitignore-additions.tpl")
    append_gitignore(td, gitignore_additions)

    # AGENTS.md — helps AI agents understand the repo layout
    agents_md = render(load_template("AGENTS.md.tpl"), base_replacements)
    write_file(os.path.join(td, "AGENTS.md"), agents_md, args.overwrite)

    print("\n=== Done! ===\n")
    print("Next steps:")
    print(f"  1. Copy shared CI workflow files from ag-devops/ci/dotnetcore/ into .github/workflows/")
    print(f"     Minimum set: dotnet-8-dependencies.yml, dotnet-8-build.yml, dotnet-8-lint.yml, dotnet-8-tests-msbuild.yml")
    print(f"  2. Run scaffold-deployment, scaffold-service, scaffold-route, scaffold-networkpolicy")
    print(f"     for each component to populate gitops/templates/")
    print(f"  3. Fill in component stubs in gitops/values.yaml")
    print(f"  4. Set GitHub secrets: OPENSHIFT_SERVER, OPENSHIFT_TOKEN (per environment)")
    print(f"  5. Create GitHub Environments: dev, test, prod")
    print(f"  6. Run: helm dependency update ./gitops && helm lint ./gitops")
    print()


if __name__ == "__main__":
    main()

