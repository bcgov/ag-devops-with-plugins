---
name: scaffold-deployment
description: Use when generating a Deployment Helm template for an OpenShift Emerald component using ag-helm-templates. Provide the component name and port; the script writes gitops/templates/<name>-deployment.yaml directly.
allowed-tools:
  - Bash
  - Read
  - Write
command: python plugins/ag-devops/skills/scaffold-deployment/scripts/generate.py --name "$NAME" --port "$PORT" --data-class "$DATA_CLASS" --output-dir "$OUTPUT_DIR"
---

# Scaffold Deployment

Generate a policy-compliant Deployment Helm template using the `ag-template.deployment`
"set + define + include" pattern. Output is written directly to `gitops/templates/`.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name (e.g., `web-api`, `frontend`) |
| `--port` | | `8080` | Container port |
| `--data-class` | | `low` | `low`, `medium`, or `high` |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Usage

```bash
python plugins/ag-devops/skills/scaffold-deployment/scripts/generate.py \
  --name web-api \
  --port 8080 \
  --data-class low \
  --output-dir gitops/templates
```

## Output

`gitops/templates/web-api-deployment.yaml` — a Helm template file ready for `helm template`.

## What the generated template includes

- `$p` dict built with `ApplicationGroup`, `Name`, `Registry`, `ModuleValues`
- `ag-template.deployment` include
- `<name>.ports` fragment (list item — emits `- name: http ...`)
- `<name>.env` fragment setting `ASPNETCORE_URLS`
- `<name>.probes` fragment with liveness + readiness on `/health/live` and `/health/ready`

## Required values.yaml additions

Add a stanza under the component's camelCase key (e.g., `webApi` for `web-api`):

```yaml
webApi:
  dataClass: low          # must match --data-class
  image:
    tag: "1.0.0"
    pullPolicy: Always
  replicas: 2
  resources:
    requests: { cpu: 100m, memory: 256Mi }
    limits:   { cpu: 500m, memory: 512Mi }
```

## Examples

**Agent call — generate web-api deployment:**
```
python plugins/ag-devops/skills/scaffold-deployment/scripts/generate.py \
  --name web-api --port 8080 --data-class low --output-dir gitops/templates
```

**Agent call — generate frontend deployment:**
```
python plugins/ag-devops/skills/scaffold-deployment/scripts/generate.py \
  --name frontend --port 8080 --data-class low --output-dir gitops/templates
```

**Agent call — generate worker (no HTTP port, use internal port 8081):**
```
python plugins/ag-devops/skills/scaffold-deployment/scripts/generate.py \
  --name worker --port 8081 --data-class low --output-dir gitops/templates
```

## Notes

- Always pair with `scaffold-networkpolicy` — every Deployment must have a matching NetworkPolicy or Conftest will fail.
- Always pair with `scaffold-service` if the component receives traffic.
- The generated probes use `/health/live` and `/health/ready` — update the paths if your app uses different health endpoints.
