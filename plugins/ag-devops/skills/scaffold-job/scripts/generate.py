#!/usr/bin/env python3
"""
Generate an ag-helm-templates Job Helm template file.

Writes to <output-dir>/<name>-job.yaml using the "set + define + include"
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
        description="Generate ag-helm-templates Job Helm template"
    )
    parser.add_argument("--name", required=True, help="Component name, e.g. db-migrate")
    parser.add_argument(
        "--data-class",
        default="low",
        choices=["low", "medium", "high"],
        help="Data classification (default: low)",
    )
    parser.add_argument("--backoff-limit", type=int, default=3, help="Retries before marking failed (default: 3)")
    parser.add_argument("--ttl", type=int, default=86400, help="Seconds after completion before deletion (default: 86400)")
    parser.add_argument(
        "--output-dir",
        default="gitops/templates",
        help="Directory to write the rendered template (default: gitops/templates)",
    )
    args = parser.parse_args()

    values_key = to_camel_case(args.name)

    tpl = load_template("job")
    content = render(
        tpl,
        {
            "@@NAME@@": args.name,
            "@@DATA_CLASS@@": args.data_class,
            "@@VALUES_KEY@@": values_key,
            "@@BACKOFF_LIMIT@@": str(args.backoff_limit),
            "@@TTL@@": str(args.ttl),
        },
    )

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, f"{args.name}-job.yaml")

    with open(out_path, "w") as fh:
        fh.write(content)

    print(f"✓  Written: {out_path}")


if __name__ == "__main__":
    main()
