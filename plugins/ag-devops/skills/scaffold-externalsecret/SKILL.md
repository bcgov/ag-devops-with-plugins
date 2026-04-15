---
name: scaffold-externalsecret
description: Generate an ExternalSecret manifest that pulls secrets from Vault on OpenShift Emerald. Use when a component needs secrets from the platform vault.
allowed-tools:
  - Bash
  - Read
  - Write
command: python ./scripts/scaffold.py --type externalsecret --name "$NAME" --output-dir "$OUTPUT_DIR"
---

# Scaffold ExternalSecret

Generate an ExternalSecret Helm template that syncs secrets from BC Gov Vault into a Kubernetes Secret.
Output is written directly to `gitops/templates/`.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name (kebab-case, e.g. `web-api`) |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Usage

```bash
python ./scripts/scaffold.py --type externalsecret --name web-api --output-dir gitops/templates
```

## Output

`gitops/templates/<name>-externalsecret.yaml` — an ExternalSecret resource that references the component SecretStore.

## Required values.yaml additions

Add a stanza under the component camelCase key:

```yaml
webApi:
  dataClass: medium
  vault:
    path: apps/data/my-namespace/web-api
    keys:
      - DB_PASSWORD
      - API_KEY
```

## Notes

- ExternalSecret requires a matching **SecretStore** (`scaffold-externalsecret` does not create one — provision via platform ops).
- The Vault path convention for BC Gov Emerald is: `apps/data/<namespace>/<component>`.
- Secrets are synced on a configurable refresh interval (default: 1m).
- Always pair with a NetworkPolicy allowing egress to Vault (port 8200).
- The generated Kubernetes Secret name matches `<name>` — reference it in your Deployment via `envFrom.secretRef`.