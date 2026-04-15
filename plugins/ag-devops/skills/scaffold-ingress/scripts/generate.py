#!/usr/bin/env python3
"""
Generate an ag-helm-templates Ingress Helm template file.

Writes to <output-dir>/<name>-ingress.yaml using the "set + define + include"
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
        description="Generate ag-helm-templates Ingress Helm template"
    )
    parser.add_argument("--name", required=True, help="Component name")
    parser.add_argument("--host", required=True, help="Hostname e.g. myapp.apps.emerald.devops.gov.bc.ca")
    parser.add_argument("--service-port", type=int, default=8080, help="Backend service port (default: 8080)")
    parser.add_argument("--path", default="/", help="URL path (default: /)")
    parser.add_argument(
        "--avi-class",
        default="dataclass-low",
        choices=["dataclass-low", "dataclass-medium", "dataclass-high", "dataclass-public"],
        help="AVI infra setting name (default: dataclass-low)",
    )
    parser.add_argument(
        "--output-dir",
        default="gitops/templates",
        help="Directory to write the rendered template (default: gitops/templates)",
    )
    args = parser.parse_args()

    values_key = to_camel_case(args.name)

    tpl = load_template("ingress")
    content = render(
        tpl,
        {
            "@@NAME@@": args.name,
            "@@VALUES_KEY@@": values_key,
            "@@HOST@@": args.host,
            "@@SERVICE_PORT@@": str(args.service_port),
            "@@AVI_CLASS@@": args.avi_class,
            "@@PATH@@": args.path,
        },
    )

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, f"{args.name}-ingress.yaml")

    with open(out_path, "w") as fh:
        fh.write(content)

    print(f"✓  Written: {out_path}")


if __name__ == "__main__":
    main()
