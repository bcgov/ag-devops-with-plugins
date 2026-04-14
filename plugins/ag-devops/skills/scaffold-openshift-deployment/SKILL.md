---
name: scaffold-openshift-deployment
description: Use when creating a new application chart for OpenShift Emerald deployment, starting a new BC Gov AG project, or when asked to set up Helm templates, Chart.yaml dependencies, values files, or a full deployment package from scratch
---

# Scaffold OpenShift Emerald Deployment

## Overview

Generate a complete, policy-compliant Helm chart for deployment to OpenShift Emerald using the `ag-helm-templates` library. The output passes all four policy checks (Datree, Polaris, kube-linter, Conftest) on first render.

## When to Use

- "Set up a new project for Emerald"
- "Create a Helm chart for my .NET API"
- "Scaffold my deployment"
- Starting from zero — no chart exists yet

**NOT for:** Modifying an existing chart. Use `validate-emerald-manifests` to find what needs fixing instead.

## Required Information (gather before generating)

Ask the developer these questions before writing any files:

1. **App name / namespace** — e.g. `myapp`, namespace `myapp-dev`
2. **Components** — which of: frontend (React/static), web API (.NET), background worker, database (PostgreSQL/Redis)?
3. **External exposure** — which components need an OpenShift Route?
4. **Data class** — `low`, `medium`, or `high`? (Default: `low`)
5. **Image registry** — e.g. `ghcr.io/bcgov-c` or OpenShift internal registry path
6. **Does it call an external API over HTTPS?** — needed for NetworkPolicy egress approval

## Generated Structure

```
your-chart/
  Chart.yaml              ← dependency on ag-helm-templates OCI
  values.yaml             ← all components with image/replicas/dataClass
  templates/
    _helpers.tpl          ← $p dict helpers (optional)
    frontend.yaml         ← Deployment + Service + Route + NetworkPolicy
    web-api.yaml          ← Deployment + Service + Route + NetworkPolicy
    postgresql.yaml       ← StatefulSet + Service + NetworkPolicy + PVC
```

## Chart.yaml Template

```yaml
apiVersion: v2
name: {{ app-name }}-gitops
description: GitOps deployment chart for {{ app-name }}
type: application
version: 0.1.0
appVersion: "1.0.0"

dependencies:
  - name: ag-helm-templates
    version: "1.0.3"
    repository: "oci://ghcr.io/bcgov-c/helm"
```

## Authoring Pattern (set + define + include)

Every resource uses this pattern — build a dict `$p`, set keys, include the template:

```yaml
{{- $p := dict "Values" .Values -}}
{{- $_ := set $p "ApplicationGroup" .Values.project -}}
{{- $_ := set $p "Name" "web-api" -}}
{{- $_ := set $p "Namespace" $.Release.Namespace -}}
{{- $_ := set $p "Registry" .Values.registry -}}
{{- $_ := set $p "ModuleValues" .Values.webApi -}}
{{- $_ := set $p "Ports" "webapi.ports" -}}
{{- $_ := set $p "Env"   "webapi.env" -}}
{{- $_ := set $p "Probes" "webapi.probes" -}}
{{ include "ag-template.deployment" $p }}

{{- define "webapi.ports" -}}
- name: http
  containerPort: 8080
  protocol: TCP
{{- end }}

{{- define "webapi.env" -}}
- name: ASPNETCORE_URLS
  value: http://+:8080
{{- end }}

{{- define "webapi.probes" -}}
livenessProbe:
  httpGet: { path: /health/live, port: http }
readinessProbe:
  httpGet: { path: /health/ready, port: http }
{{- end }}
```

## Required values.yaml Fields

```yaml
project: myapp
registry: ghcr.io/bcgov-c

commonLabels:
  owner: team-name
  environment: development   # production | test | development

webApi:
  dataClass: low             # low | medium | high
  image:
    tag: "1.0.0"             # or use digest: sha256:...
  replicas: 2
  resources:
    requests: { cpu: 100m, memory: 256Mi }
    limits:   { cpu: 500m, memory: 512Mi }
  route:
    enabled: true
    host: myapp-dev.apps.emerald.devops.gov.bc.ca
    annotations:
      aviinfrasetting.ako.vmware.com/name: dataclass-low
```

## Checklist Before Handing Off

- [ ] Every workload has a matching `ag-template.networkpolicy`
- [ ] Every Route/Ingress has `aviinfrasetting.ako.vmware.com/name` annotation
- [ ] `dataClass` set on every workload (`low|medium|high`)
- [ ] `commonLabels` includes `owner` and `environment`
- [ ] Resource requests/limits defined on every container
- [ ] Liveness and readiness probes defined
- [ ] `imagePullPolicy: Always` set if required by cluster policy
- [ ] Run `helm dependency update && helm lint` locally

## Common Mistakes

| Mistake | Fix |
|---|---|
| Forgot NetworkPolicy for a workload | Every Deployment/StatefulSet/Job needs one — policy tools will fail without it |
| `imagePullPolicy` not set | Add `image.pullPolicy: Always` to each component's `ModuleValues` |
| Route without AVI annotation | Required — `aviinfrasetting.ako.vmware.com/name: dataclass-low\|medium\|high\|public` |
| Fragment emits wrong YAML shape | `Ports`/`Env` must emit list items (`- ...`); `Probes` must emit map keys inline |

**REQUIRED SUB-SKILL:** Use `author-networkpolicy` to write every NetworkPolicy in the chart.

**After scaffolding:** Run `validate-emerald-manifests` to confirm all policy checks pass before committing.
