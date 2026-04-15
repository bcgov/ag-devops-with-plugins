#!/usr/bin/env python3
"""
Generate an ag-helm-templates StatefulSet Helm template file.

Writes to <output-dir>/<name>-statefulset.yaml using the "set + define + include"
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
        description="Generate ag-helm-templates StatefulSet Helm template"
    )
    parser.add_argument("--name", required=True, help="Component name, e.g. redis")
    parser.add_argument("--port", type=int, default=6379, help="Container port (default: 6379)")
    parser.add_argument(
        "--data-class",
        default="low",
        choices=["low", "medium", "high"],
        help="Data classification (default: low)",
    )
    parser.add_argument(
        "--service-name",
        default=None,
        help="Headless service name (default: <name>-headless)",
    )
    parser.add_argument(
        "--output-dir",
        default="gitops/templates",
        help="Directory to write the rendered template (default: gitops/templates)",
    )
    args = parser.parse_args()

    service_name = args.service_name if args.service_name else f"{args.name}-headless"
    values_key = to_camel_case(args.name)

    tpl = load_template("statefulset")
    content = render(
        tpl,
        {
            "@@NAME@@": args.name,
            "@@PORT@@": str(args.port),
            "@@DATA_CLASS@@": args.data_class,
            "@@VALUES_KEY@@": values_key,
            "@@SERVICE_NAME@@": service_name,
        },
    )

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, f"{args.name}-statefulset.yaml")

    with open(out_path, "w") as fh:
        fh.write(content)

    print(f"✓  Written: {out_path}")


if __name__ == "__main__":
    main()
