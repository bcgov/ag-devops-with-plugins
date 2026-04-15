---
name: scaffold-statefulset
description: Use when generating a StatefulSet Helm template for an OpenShift Emerald component using ag-helm-templates. For stateful workloads like databases or message queues. Writes gitops/templates/<name>-statefulset.yaml directly.
allowed-tools:
  - Bash
  - Read
  - Write
command: python ./scripts/scaffold.py --type statefulset --name "$NAME" --port "$PORT" --data-class "$DATA_CLASS" --service-name "$SERVICE_NAME" --output-dir "$OUTPUT_DIR"
---

# Scaffold StatefulSet

Generate a policy-compliant StatefulSet Helm template using the `ag-template.statefulset`
"set + define + include" pattern. Output is written directly to `gitops/templates/`.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name (e.g., `redis`, `postgres`) |
| `--port` | | `6379` | Container port |
| `--data-class` | | `low` | `low`, `medium`, or `high` |
| `--service-name` | | `<name>-headless` | Headless service name for stable network IDs |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Usage

```bash
python ./scripts/scaffold.py --type statefulset \
  --name redis \
  --port 6379 \
  --data-class low \
  --output-dir gitops/templates
```

## Output

`gitops/templates/redis-statefulset.yaml` — a Helm template file ready for `helm template`.

## Notes

- Always pair with `scaffold-networkpolicy` — every StatefulSet must have a matching NetworkPolicy.
- Always pair with `scaffold-service` if the component receives traffic.
- The `ServiceName` must match a headless Service in the same chart.

