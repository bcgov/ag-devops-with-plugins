---
name: scaffold-configmap
description: Use when generating a ConfigMap Helm template for an OpenShift Emerald component. Use for non-secret key/value configuration data driven by chart values. Writes gitops/templates/<name>-configmap.yaml directly.
allowed-tools:
  - Bash
  - Read
  - Write
command: python ./scripts/scaffold.py --type configmap --name "$NAME" --output-dir "$OUTPUT_DIR"
---

# Scaffold ConfigMap

Generate a ConfigMap Helm template using the `ag-template`-compatible pattern.
Output is written directly to `gitops/templates/`.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name (kebab-case, e.g. `app-config`) |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Usage

```bash
python ./scripts/scaffold.py --type configmap --name app-config --output-dir gitops/templates
```

## Output

`gitops/templates/<name>-configmap.yaml` — a Helm template file that reads data from `values.yaml`.

## Required values.yaml additions

Add a stanza under the component's camelCase key:

```yaml
appConfig:
  dataClass: low
  data:
    APP_ENV: "production"
    LOG_LEVEL: "info"
    DB_HOST: "postgresql"
```

## Notes

- ConfigMaps hold **non-secret** configuration only. Use `scaffold-externalsecret` for secrets.
- The generated template exposes all keys under `ModuleValues.data` as ConfigMap entries.
- Always pair with a Deployment that mounts the ConfigMap via `envFrom` or a volume.
- No NetworkPolicy is needed for a ConfigMap — only for Deployments, Services, and StatefulSets.