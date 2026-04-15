---
name: scaffold-cronjob
description: Generate a CronJob Helm template using ag-helm-templates. Use when a component needs scheduled task execution.
allowed-tools:
  - Bash
  - Read
  - Write
command: python ./scripts/scaffold.py --type cronjob --name "$NAME" --schedule "$SCHEDULE" --data-class "$DATA_CLASS" --output-dir "$OUTPUT_DIR"
---
# 

Generate a policy-compliant $(System.Collections.Hashtable.type) resource using the ag-helm-templates library.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name (kebab-case) |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Usage

```bash
python ./scripts/scaffold.py --type cronjob --name my-component --output-dir gitops/templates
```

## Examples

**Agent call:**
```
python ./scripts/scaffold.py --type cronjob --name my-component --output-dir gitops/templates
```
