#!/usr/bin/env python3
"""
Generate an ag-helm-templates NetworkPolicy Helm template file.

Writes to <output-dir>/<name>-networkpolicy.yaml using the AllowIngressFrom /
AllowEgressTo intent-input pattern, which prevents accidental allow-all shapes
that Conftest/OPA will hard-deny.

Usage examples
--------------
# Ingress from OpenShift router only (component has a Route)
python generate.py --name web-api --port 8080 --ingress-from-router

# Ingress from another app + router
python generate.py --name web-api --port 8080 \\
    --ingress-from-router --ingress-from-apps frontend

# Egress to a database
python generate.py --name web-api --port 8080 \\
    --ingress-from-router --egress-to-apps postgresql:5432

# Egress to specific CIDR
python generate.py --name web-api --port 8080 \\
    --ingress-from-router --egress-to-cidr 142.34.208.0/24:443

# Approved internet-wide egress (requires justification + approvedBy)
python generate.py --name web-api --port 8080 \\
    --ingress-from-router --egress-internet \\
    --justification "Calls external OAuth provider" \\
    --approved-by "JIRA-1234"
"""
import argparse
import os
import sys


def to_camel_case(name: str) -> str:
    import re
    parts = re.split(r"[-_]", name)
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def build_annotations_section(args) -> str:
    if not args.egress_internet:
        return ""
    return (
        f'{{{{- $_ := set $np "Annotations" (dict\n'
        f'  "justification" "{args.justification}"\n'
        f'  "approvedBy"    "{args.approved_by}"\n'
        f') -}}}}\n'
    )


def build_ingress_section(args) -> str:
    """Build the AllowIngressFrom block."""
    has_router = args.ingress_from_router
    app_names = [a.strip() for a in args.ingress_from_apps.split(",")] if args.ingress_from_apps else []

    if not has_router and not app_names:
        return ""

    lines = [f'{{{{- $_ := set $np "AllowIngressFrom" (dict']
    lines.append(f'  "ports" (list {args.port})')

    if app_names:
        app_items = "\n".join(f'    (dict "name" "{a}")' for a in app_names)
        lines.append(f'  "apps" (list\n{app_items}\n  )')

    if has_router:
        lines.append(
            '  "namespaces" (list (dict\n'
            '    "name" "openshift-ingress"\n'
            '    "podSelector" (dict "matchLabels" (dict\n'
            '      "ingresscontroller.operator.openshift.io/deployment-ingresscontroller" "default"\n'
            '    ))\n'
            '  ))'
        )

    lines.append(') -}}')
    return "\n".join(lines) + "\n"


def build_egress_section(args) -> str:
    """Build the AllowEgressTo block."""
    app_pairs = []
    if args.egress_to_apps:
        for pair in args.egress_to_apps.split(","):
            pair = pair.strip()
            if ":" not in pair:
                print(f"ERROR: --egress-to-apps value '{pair}' must be name:port", file=sys.stderr)
                sys.exit(1)
            app_name, port = pair.rsplit(":", 1)
            app_pairs.append((app_name.strip(), int(port.strip())))

    cidr_entries = []
    if args.egress_to_cidr:
        for entry in args.egress_to_cidr.split(","):
            entry = entry.strip()
            if ":" not in entry:
                print(f"ERROR: --egress-to-cidr value '{entry}' must be cidr:port", file=sys.stderr)
                sys.exit(1)
            cidr, port = entry.rsplit(":", 1)
            cidr_entries.append((cidr.strip(), int(port.strip())))

    has_internet = args.egress_internet

    if not app_pairs and not cidr_entries and not has_internet:
        return ""

    lines = [f'{{{{- $_ := set $np "AllowEgressTo" (dict']

    if app_pairs:
        app_items = []
        for app_name, port in app_pairs:
            app_items.append(
                f'    (dict\n'
                f'      "name" "{app_name}"\n'
                f'      "ports" (list (dict "port" {port} "protocol" "TCP"))\n'
                f'    )'
            )
        lines.append('  "apps" (list\n' + "\n".join(app_items) + "\n  )")

    if cidr_entries:
        cidr_items = []
        for cidr, port in cidr_entries:
            cidr_items.append(
                f'    (dict\n'
                f'      "cidr" "{cidr}"\n'
                f'      "ports" (list {port})\n'
                f'    )'
            )
        lines.append('  "ipBlocks" (list\n' + "\n".join(cidr_items) + "\n  )")

    if has_internet:
        lines.append(
            '  "internet" (dict\n'
            '    "enabled" true\n'
            '    "cidrs" (list "0.0.0.0/0")\n'
            '    "ports" (list 443)\n'
            '  )'
        )

    lines.append(') -}}')
    return "\n".join(lines) + "\n"


def build_policy_types(args) -> str:
    types = []
    has_ingress = args.ingress_from_router or args.ingress_from_apps
    has_egress = args.egress_to_apps or args.egress_to_cidr or args.egress_internet
    if has_ingress:
        types.append('"Ingress"')
    if has_egress:
        types.append('"Egress"')
    if not types:
        types = ['"Ingress"']
    return " ".join(types)


def build_content(args) -> str:
    policy_types = build_policy_types(args)
    annotations = build_annotations_section(args)
    ingress = build_ingress_section(args)
    egress = build_egress_section(args)

    lines = [
        "{{- $np := dict \"Values\" .Values -}}",
        "{{- $_ := set $np \"ApplicationGroup\" .Values.project -}}",
        f'{{{{- $_ := set $np "Name" "{args.name}" -}}}}',
        "{{- $_ := set $np \"Namespace\" $.Release.Namespace -}}",
        f'{{{{- $_ := set $np "PolicyTypes" (list {policy_types}) -}}}}',
    ]

    if annotations:
        lines.append(annotations.rstrip())
    if ingress:
        lines.append(ingress.rstrip())
    if egress:
        lines.append(egress.rstrip())

    lines.append('{{ include "ag-template.networkpolicy" $np }}')
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate ag-helm-templates NetworkPolicy Helm template"
    )
    parser.add_argument("--name", required=True, help="Component name, e.g. web-api")
    parser.add_argument("--port", type=int, default=8080, help="Ingress port for this component (default: 8080)")

    # Ingress
    parser.add_argument("--ingress-from-router", action="store_true",
                        help="Allow ingress from OpenShift router (required if component has a Route)")
    parser.add_argument("--ingress-from-apps", default="",
                        help="Comma-separated app names that send traffic to this component, e.g. frontend,worker")

    # Egress
    parser.add_argument("--egress-to-apps", default="",
                        help="Comma-separated name:port pairs, e.g. postgresql:5432,redis:6379")
    parser.add_argument("--egress-to-cidr", default="",
                        help="Comma-separated cidr:port pairs, e.g. 142.34.208.0/24:443")
    parser.add_argument("--egress-internet", action="store_true",
                        help="Allow internet-wide egress (0.0.0.0/0) — requires --justification and --approved-by")
    parser.add_argument("--justification", default="",
                        help="Required with --egress-internet: reason for internet-wide egress")
    parser.add_argument("--approved-by", default="",
                        help="Required with --egress-internet: ticket reference or approver name")

    parser.add_argument("--output-dir", default="gitops/templates",
                        help="Directory to write the rendered template (default: gitops/templates)")
    args = parser.parse_args()

    if args.egress_internet and (not args.justification or not args.approved_by):
        print("ERROR: --justification and --approved-by are required when --egress-internet is set",
              file=sys.stderr)
        sys.exit(1)

    content = build_content(args)

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, f"{args.name}-networkpolicy.yaml")

    with open(out_path, "w") as fh:
        fh.write(content)

    print(f"✓  Written: {out_path}")


if __name__ == "__main__":
    main()
