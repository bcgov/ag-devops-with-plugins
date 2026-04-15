---
name: scaffold-configmap
description: Generate a ConfigMap Helm template for data driven by values. Use when a component needs non-secret key/value configuration.
allowed-tools:
  - Bash
  - Read
  - Write
command: python ./scripts/scaffold.py --type configmap --name "$NAME" --output-dir "$OUTPUT_DIR"
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
python ./scripts/scaffold.py --type configmap --name my-component --output-dir gitops/templates
```

## Examples

**Agent call:**
```
python ./scripts/scaffold.py --type configmap --name my-component --output-dir gitops/templates
```
