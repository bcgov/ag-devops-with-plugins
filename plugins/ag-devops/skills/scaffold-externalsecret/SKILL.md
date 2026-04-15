---
name: scaffold-externalsecret
description: Generate an ExternalSecret manifest that pulls secrets from Vault on OpenShift Emerald. Use when a component needs secrets from the platform vault.
allowed-tools:
  - Bash
  - Read
  - Write
command: python ./scripts/scaffold.py --type externalsecret --name "$NAME" --output-dir "$OUTPUT_DIR"
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
python ./scripts/scaffold.py --type externalsecret --name my-component --output-dir gitops/templates
```

## Examples

**Agent call:**
```
python ./scripts/scaffold.py --type externalsecret --name my-component --output-dir gitops/templates
```
