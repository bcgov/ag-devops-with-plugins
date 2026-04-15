#!/usr/bin/env python3
"""
Generate an ag-helm-templates PersistentVolumeClaim Helm template file.

Writes to <output-dir>/<name>-pvc.yaml using the "set + define + include"
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
        description="Generate ag-helm-templates PersistentVolumeClaim Helm template"
    )
    parser.add_argument("--name", required=True, help="Component name")
    parser.add_argument("--size", default="1Gi", help="Storage size (default: 1Gi)")
    parser.add_argument(
        "--storage-class",
        default="netapp-file-standard",
        help="StorageClass name (default: netapp-file-standard)",
    )
    parser.add_argument(
        "--access-mode",
        default="ReadWriteOnce",
        choices=["ReadWriteOnce", "ReadWriteMany", "ReadOnlyMany"],
        help="Access mode (default: ReadWriteOnce)",
    )
    parser.add_argument(
        "--output-dir",
        default="gitops/templates",
        help="Directory to write the rendered template (default: gitops/templates)",
    )
    args = parser.parse_args()

    values_key = to_camel_case(args.name)

    tpl = load_template("pvc")
    content = render(
        tpl,
        {
            "@@NAME@@": args.name,
            "@@VALUES_KEY@@": values_key,
            "@@SIZE@@": args.size,
            "@@STORAGE_CLASS@@": args.storage_class,
            "@@ACCESS_MODE@@": args.access_mode,
        },
    )

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, f"{args.name}-pvc.yaml")

    with open(out_path, "w") as fh:
        fh.write(content)

    print(f"✓  Written: {out_path}")


if __name__ == "__main__":
    main()
