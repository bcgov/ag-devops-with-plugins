---
name: scaffold-networkpolicy
description: Use when generating a NetworkPolicy Helm template for an OpenShift Emerald component using ag-helm-templates. Accepts ingress/egress topology flags and writes gitops/templates/<name>-networkpolicy.yaml. Replaces the manual author-networkpolicy skill with an automated script.
allowed-tools:
  - Bash
  - Read
  - Write
command: python plugins/ag-devops/skills/scaffold-networkpolicy/scripts/generate.py --name "$NAME" --port "$PORT" $INGRESS_FLAGS $EGRESS_FLAGS --output-dir "$OUTPUT_DIR"
---

# Scaffold NetworkPolicy

Generate a fully compliant NetworkPolicy Helm template using `ag-template.networkpolicy`
with `AllowIngressFrom` / `AllowEgressTo` intent inputs — the only safe pattern for
Conftest/OPA compliance. Output is written directly to `gitops/templates/`.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name (e.g., `web-api`) |
| `--port` | | `8080` | Ingress port for this component |
| `--ingress-from-router` | | false | Allow ingress from OpenShift router (required if component has a Route) |
| `--ingress-from-apps` | | — | Comma-separated app names sending traffic here, e.g. `frontend,worker` |
| `--egress-to-apps` | | — | Comma-separated `name:port` pairs, e.g. `postgresql:5432,redis:6379` |
| `--egress-to-cidr` | | — | Comma-separated `cidr:port` pairs, e.g. `142.34.208.0/24:443` |
| `--egress-internet` | | false | Allow `0.0.0.0/0` egress — requires `--justification` + `--approved-by` |
| `--justification` | cond. | — | Required with `--egress-internet` |
| `--approved-by` | cond. | — | Required with `--egress-internet` |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Usage

```bash
# Standard web-api: ingress from router + frontend; egress to postgresql
python plugins/ag-devops/skills/scaffold-networkpolicy/scripts/generate.py \
  --name web-api \
  --port 8080 \
  --ingress-from-router \
  --ingress-from-apps frontend \
  --egress-to-apps postgresql:5432 \
  --output-dir gitops/templates
```

## Topology Guide

| Component type | Recommended flags |
|---|---|
| Exposed via Route | `--ingress-from-router` |
| Called by another app | `--ingress-from-apps <caller>` |
| Calls a database | `--egress-to-apps postgresql:5432` |
| Calls an external API | `--egress-to-cidr 142.34.208.0/24:443` |
| Calls internet (approved) | `--egress-internet --justification "..." --approved-by "..."` |
| Database / StatefulSet | `--ingress-from-apps <caller>` only (no egress needed) |

## Examples

**Agent call — frontend (Route-exposed, calls web-api):**
```
python plugins/ag-devops/skills/scaffold-networkpolicy/scripts/generate.py \
  --name frontend --port 8080 \
  --ingress-from-router \
  --egress-to-apps web-api:8080 \
  --output-dir gitops/templates
```

**Agent call — web-api (Route-exposed, called by frontend, calls postgresql):**
```
python plugins/ag-devops/skills/scaffold-networkpolicy/scripts/generate.py \
  --name web-api --port 8080 \
  --ingress-from-router --ingress-from-apps frontend \
  --egress-to-apps postgresql:5432 \
  --output-dir gitops/templates
```

**Agent call — postgresql (receives from web-api only, no egress):**
```
python plugins/ag-devops/skills/scaffold-networkpolicy/scripts/generate.py \
  --name postgresql --port 5432 \
  --ingress-from-apps web-api \
  --output-dir gitops/templates
```

**Agent call — worker with approved internet egress:**
```
python plugins/ag-devops/skills/scaffold-networkpolicy/scripts/generate.py \
  --name worker --port 8081 \
  --egress-internet \
  --justification "Sends notifications to external webhook" \
  --approved-by "JIRA-4242" \
  --output-dir gitops/templates
```

## Hard Deny Patterns (Conftest will reject these — the script prevents them)

| Pattern | Why denied |
|---|---|
| Ingress rule with no `from` | Allows all sources |
| Ingress rule with no `ports` | Allows all ports |
| `egress: - {}` | Allows all egress |
| `podSelector: {}` inside `from/to` | Wildcard — matches all pods |
| Internet egress without annotations | Unapproved internet exposure |

## Notes

- Every Deployment, StatefulSet, and Job **must** have a matching NetworkPolicy or Conftest will deny the entire render.
- `PolicyTypes` is inferred automatically: if you provide ingress flags, `Ingress` is included; egress flags → `Egress` is included.
- After generating, run `validate-emerald-manifests` to confirm all four policy checks pass.
