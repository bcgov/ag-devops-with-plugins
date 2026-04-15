---
name: scaffold-ingress
description: Use when generating a Kubernetes Ingress Helm template for an Emerald component using ag-helm-templates. NOTE: OpenShift Route is preferred on Emerald — use scaffold-route instead unless you specifically need standard k8s Ingress. Writes gitops/templates/<name>-ingress.yaml.
allowed-tools:
  - Bash
  - Read
  - Write
command: python plugins/ag-devops/skills/scaffold-ingress/scripts/generate.py --name "$NAME" --host "$HOST" --service-port "$PORT" --avi-class "$AVI_CLASS" --output-dir "$OUTPUT_DIR"
---

# Scaffold Ingress

Generate a Kubernetes Ingress Helm template using the `ag-template.ingress`
"set + define + include" pattern.

> **Note:** OpenShift Route is preferred on Emerald — use `scaffold-route` unless you specifically need standard Kubernetes Ingress.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name |
| `--host` | ✅ | — | Hostname e.g. myapp.apps.emerald.devops.gov.bc.ca |
| `--service-port` | | `8080` | Backend service port |
| `--path` | | `/` | URL path |
| `--avi-class` | | `dataclass-low` | AVI infra setting name |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Output

`gitops/templates/<name>-ingress.yaml`
