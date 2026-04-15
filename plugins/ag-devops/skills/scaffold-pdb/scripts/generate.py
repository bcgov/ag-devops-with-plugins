#!/usr/bin/env python3
"""
Generate an ag-helm-templates PodDisruptionBudget Helm template file.

Writes to <output-dir>/<name>-pdb.yaml using the "set + define + include"
authoring pattern required by the ag-helm-templates library chart.
"""
import argparse
import os
import re
import sys


def to_camel_case(name: str) -> str:
    """Convert kebab-case or snake_case to camelCase for Helm values keys."""
    parts = re.split(r"[-_]", name)
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def load_template(name: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tpl_path = os.path.join(script_dir, "..", "assets", "templates", f"{name}.yaml.j2")
    with open(tpl_path, "r") as fh:
        return fh.read()


def render(tpl: str, replacements: dict) -> str:
    for marker, value in replacements.items():
        tpl = tpl.replace(marker, value)
    return tpl


def main():
    parser = argparse.ArgumentParser(
        description="Generate ag-helm-templates PodDisruptionBudget Helm template"
    )
    parser.add_argument("--name", required=True, help="Component name matching the Deployment")
    parser.add_argument(
        "--max-unavailable",
        default="10%",
        help="Max unavailable pods, int or percent string (default: 10%%)",
    )
    parser.add_argument(
        "--min-available",
        default=None,
        help="Min available pods — mutually exclusive with --max-unavailable",
    )
    parser.add_argument(
        "--output-dir",
        default="gitops/templates",
        help="Directory to write the rendered template (default: gitops/templates)",
    )
    args = parser.parse_args()

    if args.min_available is not None and args.max_unavailable != "10%":
        print("Error: --min-available and --max-unavailable are mutually exclusive.", file=sys.stderr)
        sys.exit(1)

    effective_value = args.min_available if args.min_available is not None else args.max_unavailable
    values_key = to_camel_case(args.name)

    tpl = load_template("pdb")
    content = render(
        tpl,
        {
            "@@NAME@@": args.name,
            "@@VALUES_KEY@@": values_key,
        },
    )

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, f"{args.name}-pdb.yaml")

    with open(out_path, "w") as fh:
        fh.write(content)

    print(f"✓  Written: {out_path}")
    print()
    print(f"# Add to your values.yaml under {values_key}:")
    print(f"# {values_key}:")
    print(f"#   pdb:")
    print(f'#     maxUnavailable: "{effective_value}"')


if __name__ == "__main__":
    main()
