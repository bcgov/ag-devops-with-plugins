---
name: scaffold-serviceaccount
description: Use when generating a ServiceAccount Helm template for an OpenShift Emerald component using ag-helm-templates. Required for workloads needing RBAC, image pull credentials, or pod identity. Writes gitops/templates/<name>-serviceaccount.yaml directly.
allowed-tools:
  - Bash
  - Read
  - Write
command: python ./scripts/scaffold.py --type serviceaccount --name "$NAME" --automount false --output-dir "$OUTPUT_DIR"
---

# Scaffold ServiceAccount

Generate a ServiceAccount Helm template using the `ag-template.serviceaccount`
"set + define + include" pattern.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name |
| `--automount` | | `false` | Automount service account token (store_true flag) |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Output

`gitops/templates/<name>-serviceaccount.yaml` plus a values snippet printed to stdout.

