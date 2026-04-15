---
name: scaffold-hpa
description: Use when generating a HorizontalPodAutoscaler Helm template for an OpenShift Emerald component using ag-helm-templates. Writes gitops/templates/<name>-hpa.yaml. Requires the target Deployment to already exist.
allowed-tools:
  - Bash
  - Read
  - Write
command: python plugins/ag-devops/skills/scaffold-hpa/scripts/generate.py --name "$NAME" --min-replicas "$MIN" --max-replicas "$MAX" --cpu-utilization "$CPU" --output-dir "$OUTPUT_DIR"
---

# Scaffold HPA

Generate a HorizontalPodAutoscaler Helm template using the `ag-template.hpa`
"set + define + include" pattern. The HPA scaling parameters are controlled via values.yaml.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name matching the Deployment |
| `--min-replicas` | | `1` | Minimum replica count |
| `--max-replicas` | | `3` | Maximum replica count |
| `--cpu-utilization` | | `70` | Target CPU utilization percent |
| `--memory-utilization` | | `0` | Target memory utilization percent (0 = disabled) |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Output

`gitops/templates/<name>-hpa.yaml` plus a values snippet printed to stdout.

## Notes

- Requires an existing Deployment for the same component name.
- The script prints a `values.yaml` snippet showing the required HPA configuration keys.
