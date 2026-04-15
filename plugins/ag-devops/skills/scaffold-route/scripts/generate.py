#!/usr/bin/env python3
"""
Generate an ag-helm-templates OpenShift Route Helm template file.

Writes to <output-dir>/<name>-route.yaml.
Route host and AVI annotation are driven by values.yaml under
.Values.<valuesKey>.route — this script generates the template stub
and emits the required values.yaml snippet for the developer to add.
"""
import argparse
import os
import re


def to_camel_case(name: str) -> str:
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
        description="Generate ag-helm-templates OpenShift Route Helm template"
    )
    parser.add_argument("--name", required=True, help="Component name, e.g. web-api")
    parser.add_argument("--port", type=int, default=8080, help="Service port (default: 8080)")
    parser.add_argument(
        "--data-class",
        default="low",
        choices=["low", "medium", "high"],
        help="Data classification for AVI annotation (default: low)",
    )
    parser.add_argument(
        "--host",
        default="",
        help="Route hostname, e.g. myapp-dev.apps.emerald.devops.gov.bc.ca (used in values hint only)",
    )
    parser.add_argument(
        "--output-dir",
        default="gitops/templates",
        help="Directory to write the rendered template (default: gitops/templates)",
    )
    args = parser.parse_args()

    values_key = to_camel_case(args.name)

    tpl = load_template("route")
    content = render(
        tpl,
        {
            "@@NAME@@": args.name,
            "@@PORT@@": str(args.port),
            "@@VALUES_KEY@@": values_key,
        },
    )

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, f"{args.name}-route.yaml")

    with open(out_path, "w") as fh:
        fh.write(content)

    print(f"✓  Written: {out_path}")
    print()
    print("Add the following to your values.yaml under the component section:")
    print(f"  {values_key}:")
    print( "    route:")
    print( "      enabled: true")
    host = args.host or f"<project>-<env>.apps.emerald.devops.gov.bc.ca"
    print(f"      host: {host}")
    print( "      annotations:")
    print(f"        aviinfrasetting.ako.vmware.com/name: dataclass-{args.data_class}")


if __name__ == "__main__":
    main()
