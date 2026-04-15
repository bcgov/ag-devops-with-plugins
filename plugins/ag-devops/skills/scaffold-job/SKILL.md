---
name: scaffold-job
description: Use when generating a Kubernetes Job Helm template for an OpenShift Emerald component using ag-helm-templates. For one-shot batch workloads, DB migrations, or initialization tasks. Writes gitops/templates/<name>-job.yaml directly.
allowed-tools:
  - Bash
  - Read
  - Write
command: python plugins/ag-devops/skills/scaffold-job/scripts/generate.py --name "$NAME" --data-class "$DATA_CLASS" --backoff-limit "$BACKOFF" --output-dir "$OUTPUT_DIR"
---

# Scaffold Job

Generate a Kubernetes Job Helm template using the `ag-template.job`
"set + define + include" pattern.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name (e.g., `db-migrate`) |
| `--data-class` | | `low` | `low`, `medium`, or `high` |
| `--backoff-limit` | | `3` | Number of retries before marking as failed |
| `--ttl` | | `86400` | Seconds after completion before deletion |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Output

`gitops/templates/<name>-job.yaml`

## Notes

- Jobs are one-shot; always pair with a NetworkPolicy if the job calls external services.
- Use `--ttl 0` to delete immediately after completion.
