---
name: scaffold-cronjob
description: Generate a CronJob Helm template using ag-helm-templates. Use when a component needs scheduled task execution on OpenShift Emerald.
allowed-tools:
  - Bash
  - Read
  - Write
command: python ./scripts/scaffold.py --type cronjob --name "$NAME" --schedule "$SCHEDULE" --output-dir "$OUTPUT_DIR"
---

# Scaffold CronJob

Generate a CronJob Helm template using the `ag-template`-compatible pattern.
Output is written directly to `gitops/templates/`.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name (kebab-case, e.g. `db-backup`) |
| `--schedule` | ✅ | — | Cron schedule expression, e.g. `0 2 * * *` |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Usage

```bash
python ./scripts/scaffold.py --type cronjob --name db-backup --schedule "0 2 * * *" --output-dir gitops/templates
```

## Output

`gitops/templates/<name>-cronjob.yaml` — a Helm CronJob template driven by `values.yaml`.

## Required values.yaml additions

Add a stanza under the component camelCase key:

```yaml
dbBackup:
  dataClass: low
  schedule: "0 2 * * *"
  image: my-backup-image
  tag: latest
```

## Notes

- The `--schedule` argument uses standard cron syntax (`minute hour dom month dow`).
- CronJobs should have their own NetworkPolicy if they make outbound network calls.
- Set `dataClass: medium` or `high` if the job processes sensitive data.
- CronJob templates do **not** include a Service or Route — they run to completion and exit.