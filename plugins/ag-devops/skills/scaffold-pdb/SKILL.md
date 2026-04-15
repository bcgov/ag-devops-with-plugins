---
name: scaffold-pdb
description: Use when generating a PodDisruptionBudget Helm template for an OpenShift Emerald component using ag-helm-templates. Ensures availability during node maintenance. Writes gitops/templates/<name>-pdb.yaml directly.
allowed-tools:
  - Bash
  - Read
  - Write
command: python plugins/ag-devops/skills/scaffold-pdb/scripts/generate.py --name "$NAME" --max-unavailable "$MAX_UNAVAILABLE" --output-dir "$OUTPUT_DIR"
---

# Scaffold PDB

Generate a PodDisruptionBudget Helm template using the `ag-template.pdb`
"set + define + include" pattern. Ensures workload availability during voluntary disruptions.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name matching the Deployment |
| `--max-unavailable` | | `10%` | Max unavailable pods (int or percent string) |
| `--min-available` | | — | Min available pods — mutually exclusive with --max-unavailable |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Output

`gitops/templates/<name>-pdb.yaml` plus a values snippet printed to stdout.

## Notes

- `--min-available` and `--max-unavailable` are mutually exclusive; script exits if both are provided.
- The script prints a `values.yaml` snippet showing the required PDB configuration keys.
