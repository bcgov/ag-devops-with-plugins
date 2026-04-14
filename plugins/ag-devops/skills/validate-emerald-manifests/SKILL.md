---
name: validate-emerald-manifests
description: Use when checking if a Helm chart is ready to deploy to OpenShift Emerald, when policy checks are failing in CI, when datree or polaris or kube-linter or conftest report errors, or when asked to validate or lint Kubernetes manifests
---

# Validate Emerald Manifests

## Overview

Render a Helm chart to YAML and run all four required policy tools against it. Interpret failures and provide specific, actionable fixes. All four tools must pass before a deploy is allowed.

## Quick Start

```bash
# 1. Login to GHCR if chart has ag-helm-templates dependency
echo $GITHUB_TOKEN | helm registry login ghcr.io -u <github-user> --password-stdin
helm dependency update ./my-chart

# 2. Render all manifests to a single file
helm template my-release ./my-chart --values ./values.yaml > rendered.yaml

# 3. Run all four checks
datree test rendered.yaml --policy-config cd/policies/datree-policies.yaml
polaris audit --config cd/policies/polaris.yaml --format pretty rendered.yaml
kube-linter lint rendered.yaml --config cd/policies/kube-linter.yaml
conftest test rendered.yaml --policy cd/policies --all-namespaces --fail-on-warn
```

## Policy Tools Quick Reference

| Tool | Config | Primary Concerns |
|---|---|---|
| Datree | `cd/policies/datree-policies.yaml` | DataClass label, AVI annotation, owner/environment labels, imagePullPolicy, probes, resources |
| Polaris | `cd/policies/polaris.yaml` | Security context, NetworkPolicy coverage, replicas, hostIPC/PID/Network, runAsRoot |
| kube-linter | `cd/policies/kube-linter.yaml` | Service selectors, RBAC, latest-tag, env var secrets, selector mismatches |
| Conftest/OPA | `cd/policies/` (Rego) | NetworkPolicy allow-all shapes, Route edge termination approval, internet egress annotations |

## Common Failures and Fixes

### Datree: DataClass label missing or invalid

```
FAILED: workload must have DataClass label set to Low, Medium, or High
```

**Fix:** Set `ModuleValues.dataClass: low` (or `medium`/`high`) in values.yaml. The library renders it as `data-class: Low`.

---

### Datree: AVI annotation missing on Route/Ingress

```
FAILED: route must have aviinfrasetting.ako.vmware.com/name annotation
```

**Fix:** Add to route config in values.yaml:
```yaml
route:
  annotations:
    aviinfrasetting.ako.vmware.com/name: dataclass-low
```
Allowed values: `dataclass-low | dataclass-medium | dataclass-high | dataclass-public`

---

### Datree: imagePullPolicy not Always

**Fix:** Set `ModuleValues.image.pullPolicy: Always` for each workload component.

---

### Polaris / Conftest: NetworkPolicy missing or no coverage

```
FAILED: Deployment web-api does not have a matching NetworkPolicy
```

**Fix:** Add a NetworkPolicy that selects the same pod labels. Use `ag-template.networkpolicy` with `AllowIngressFrom`/`AllowEgressTo` intent inputs. See `author-networkpolicy` skill.

---

### Conftest: NetworkPolicy allow-all pattern

```
DENIED: NetworkPolicy has ingress rule without 'from' (allows all sources)
DENIED: NetworkPolicy has egress rule without 'ports' (allows all ports)
```

**Fix:** All ingress/egress rules must specify BOTH peers (`from`/`to`) AND `ports`. Switch to intent inputs — they enforce this automatically.

---

### Conftest: Internet egress without approval annotations

```
DENIED: NetworkPolicy allows internet egress (0.0.0.0/0) without justification/approvedBy annotations
```

**Fix:** Add both annotations to the NetworkPolicy metadata:
```yaml
annotations:
  justification: "Reason this service needs internet-wide egress"
  approvedBy: "Ticket reference or approver name"
```

---

### Conftest: Route edge termination not approved

```
DENIED: Route uses edge termination without approval annotation
```

**Fix:** Either change to `reencrypt` termination, OR add the annotation:
```yaml
annotations:
  isb.gov.bc.ca/edge-termination-approval: "ticket-reference"
```
OR add label `app.kubernetes.io/component: frontend` if this is truly a frontend service.

---

### Polaris: runAsRoot / security context

**Fix:** For OpenShift, ensure `global.openshift: true` is set in values — the library then omits `runAsUser` so SCC assigns a safe UID at runtime.

---

### kube-linter: Service selector mismatch

**Fix:** Ensure the Service's selector labels match the Deployment's pod template labels. When using `ag-template.service` + `ag-template.deployment` with the same `Name`, labels are generated consistently.

## Running a Single Tool

```bash
# Just Conftest (fastest for NetworkPolicy issues)
conftest test rendered.yaml --policy cd/policies --all-namespaces --fail-on-warn

# Just Datree
datree test rendered.yaml --policy-config cd/policies/datree-policies.yaml

# Just Polaris with JSON output
polaris audit --config cd/policies/polaris.yaml --format json rendered.yaml | jq '.Results[].Results[]|select(.Success==false)'
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Running tools against chart source (not rendered YAML) | Always render first: `helm template ... > rendered.yaml` |
| Running tools against partial render (missing some components) | Include all resources in one render so cross-resource checks work |
| Fixing one tool's output and breaking another | Run all four after each fix |
