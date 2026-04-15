---
name: scaffold-route
description: Use when generating an OpenShift Route Helm template for an Emerald component using ag-helm-templates. Provide the component name and data class; the script writes gitops/templates/<name>-route.yaml and prints the required values.yaml snippet.
allowed-tools:
  - Bash
  - Read
  - Write
command: python ./scripts/scaffold.py --type route --name "$NAME" --host "$HOST" --data-class "$DATA_CLASS" --output-dir "$OUTPUT_DIR"
---

# Scaffold OpenShift Route

Generate an OpenShift Route Helm template using `ag-template.route.openshift`. Output
is written directly to `gitops/templates/`. The script also prints the required
`values.yaml` snippet including the mandatory AVI annotation.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name (e.g., `web-api`, `frontend`) |
| `--port` | | `8080` | Service port |
| `--data-class` | | `low` | `low`, `medium`, or `high` — determines AVI annotation |
| `--host` | | auto-hint | Route hostname (e.g., `myapp-dev.apps.emerald.devops.gov.bc.ca`) |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Usage

```bash
python ./scripts/scaffold.py --type route \
  --name web-api \
  --port 8080 \
  --data-class low \
  --host myapp-dev.apps.emerald.devops.gov.bc.ca \
  --output-dir gitops/templates
```

## Output

- `gitops/templates/web-api-route.yaml` — Helm template using `ag-template.route.openshift`
- Printed values.yaml snippet with `route.enabled`, `route.host`, and `aviinfrasetting` annotation

## Required values.yaml additions

The script prints this after generating the file:

```yaml
webApi:
  route:
    enabled: true
    host: myapp-dev.apps.emerald.devops.gov.bc.ca
    annotations:
      aviinfrasetting.ako.vmware.com/name: dataclass-low
```

> The AVI annotation is **required** — Datree and Conftest will hard-fail without it.

## Examples

**Agent call — expose web-api via Route:**
```
python ./scripts/scaffold.py --type route \
  --name web-api --port 8080 --data-class low \
  --host myapp-dev.apps.emerald.devops.gov.bc.ca --output-dir gitops/templates
```

**Agent call — expose frontend via Route:**
```
python ./scripts/scaffold.py --type route \
  --name frontend --port 8080 --data-class low \
  --host myapp-dev.apps.emerald.devops.gov.bc.ca --output-dir gitops/templates
```

## Notes

- Route host and AVI annotation live in `values.yaml`; use separate `values-dev.yaml` / `values-prod.yaml` overrides for per-environment hostnames.
- If using `reencrypt` or `passthrough` termination, update the generated template's route settings accordingly.
- Components with a Route **must** also have a NetworkPolicy that allows ingress from `openshift-ingress` router pods — use `scaffold-networkpolicy --ingress-from-router`.

