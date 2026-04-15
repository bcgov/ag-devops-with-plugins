#!/usr/bin/env python3
"""
Generate a .github/workflows/sast.yml workflow that runs SonarQube SAST analysis
and Gitleaks secrets scanning using the bcgov-c/ag-devops shared composite action.
"""
import argparse
import os
import re
import sys


def load_template(filename: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tpl_path = os.path.join(script_dir, "..", "assets", "templates", filename)
    with open(tpl_path, "r") as fh:
        return fh.read()


def render(tpl: str, replacements: dict) -> str:
    for marker, value in replacements.items():
        tpl = tpl.replace(marker, value)
    return tpl


def main():
    parser = argparse.ArgumentParser(
        description="Generate .github/workflows/sast.yml for SonarQube SAST and Gitleaks scanning"
    )
    parser.add_argument("--project-key", required=True, help="SonarQube project key")
    parser.add_argument(
        "--sonar-host",
        default="https://ag-sonarqube-e7c7c2-prod.apps.gold.devops.gov.bc.ca/",
        help="SonarQube host URL",
    )
    parser.add_argument("--sources", default=".", help="Source directory for analysis (default: .)")
    parser.add_argument(
        "--coverage-report",
        default="TestResults/coverage/coverage.cobertura.xml",
        help="Coverage report path (default: TestResults/coverage/coverage.cobertura.xml)",
    )
    parser.add_argument(
        "--output-dir",
        default=".github/workflows",
        help="Destination directory (default: .github/workflows)",
    )
    args = parser.parse_args()

    tpl = load_template("sast.yml.j2")
    content = render(
        tpl,
        {
            "@@PROJECT_KEY@@": args.project_key,
            "@@SONAR_HOST@@": args.sonar_host,
            "@@SOURCES@@": args.sources,
            "@@COVERAGE_REPORT@@": args.coverage_report,
        },
    )

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, "sast.yml")

    with open(out_path, "w") as fh:
        fh.write(content)

    print(f"✓  Written: {out_path}")


if __name__ == "__main__":
    main()
