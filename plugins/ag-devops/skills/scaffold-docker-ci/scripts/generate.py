#!/usr/bin/env python3
"""
Generate a .github/workflows/docker.yml consumer workflow that calls the
bcgov-c/ag-devops shared Docker build and push workflow.
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
        description="Generate .github/workflows/docker.yml for Docker build and push"
    )
    parser.add_argument("--image", required=True, help="Image name e.g. my-api")
    parser.add_argument("--registry", default="ghcr.io", help="Container registry (default: ghcr.io)")
    parser.add_argument("--context", default=".", help="Docker build context (default: .)")
    parser.add_argument("--file", default="Dockerfile", help="Path to Dockerfile (default: Dockerfile)")
    parser.add_argument("--platforms", default="linux/amd64", help="Target platforms (default: linux/amd64)")
    parser.add_argument(
        "--output-dir",
        default=".github/workflows",
        help="Destination directory (default: .github/workflows)",
    )
    args = parser.parse_args()

    tpl = load_template("docker.yml.j2")
    content = render(
        tpl,
        {
            "@@IMAGE@@": args.image,
            "@@REGISTRY@@": args.registry,
            "@@CONTEXT@@": args.context,
            "@@FILE@@": args.file,
            "@@PLATFORMS@@": args.platforms,
        },
    )

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, "docker.yml")

    with open(out_path, "w") as fh:
        fh.write(content)

    print(f"✓  Written: {out_path}")


if __name__ == "__main__":
    main()
