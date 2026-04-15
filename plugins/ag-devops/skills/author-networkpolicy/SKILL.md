---
name: author-networkpolicy
description: Use when writing or fixing a Kubernetes NetworkPolicy for OpenShift Emerald, when Conftest or Polaris reports allow-all or missing NetworkPolicy failures, or when configuring traffic between services in a deny-by-default namespace
allowed-tools:
  - Read
  - Bash
---

# Author NetworkPolicy for Emerald

## Overview

Write compliant NetworkPolicies using `ag-template.networkpolicy` intent inputs. The Rego policy in `cd/policies/network-policies.rego` hard-denies any rule that could accidentally allow all traffic — intent inputs are specifically designed to prevent those shapes.

## The Golden Rule

**Always specify BOTH peers (`from`/`to`) AND `ports` in every rule.** Missing either creates an allow-all that Conftest will deny.

Use intent inputs (`AllowIngressFrom` / `AllowEgressTo`) — they enforce this contract automatically.

## Recipe: Standard web-api Policy (most common pattern)

```yaml
{{- $np := dict "Values" .Values -}}
{{- $_ := set $np "ApplicationGroup" .Values.project -}}
{{- $_ := set $np "Name" "web-api" -}}
{{- $_ := set $np "Namespace" $.Release.Namespace -}}
{{- $_ := set $np "PolicyTypes" (list "Ingress" "Egress") -}}

{{- $_ := set $np "AllowIngressFrom" (dict
  "ports" (list 8080)
  "apps" (list (dict "name" "frontend"))
  "namespaces" (list (dict
    "name" "openshift-ingress"
    "podSelector" (dict "matchLabels" (dict
      "ingresscontroller.operator.openshift.io/deployment-ingresscontroller" "default"
    ))
  ))
) -}}

{{- $_ := set $np "AllowEgressTo" (dict
  "apps" (list (dict
    "name" "postgresql"
    "ports" (list (dict "port" 5432 "protocol" "TCP"))
  ))
) -}}

{{ include "ag-template.networkpolicy" $np }}
```

## Recipe Cookbook

### Allow ingress from another app in the same namespace

```yaml
{{- $_ := set $np "PolicyTypes" (list "Ingress") -}}
{{- $_ := set $np "AllowIngressFrom" (dict
  "ports" (list 8080)
  "apps" (list (dict "name" "frontend"))
) -}}
```

### Allow ingress from OpenShift router (required for Routes)

```yaml
{{- $_ := set $np "AllowIngressFrom" (dict
  "ports" (list 8080)
  "namespaces" (list (dict
    "name" "openshift-ingress"
    "podSelector" (dict "matchLabels" (dict
      "ingresscontroller.operator.openshift.io/deployment-ingresscontroller" "default"
    ))
  ))
) -}}
```

> Confirm router labels in your cluster — labels vary by OpenShift version.

### Allow egress to a database (same namespace)

```yaml
{{- $_ := set $np "AllowEgressTo" (dict
  "apps" (list (dict
    "name" "postgresql"
    "ports" (list (dict "port" 5432 "protocol" "TCP"))
  ))
) -}}
```

### Allow egress to a specific external CIDR (preferred over internet-wide)

```yaml
{{- $_ := set $np "AllowEgressTo" (dict
  "ipBlocks" (list (dict
    "cidr" "142.34.208.0/24"
    "ports" (list 443)
  ))
) -}}
```

### Approved internet-wide egress (last resort — requires approval annotations)

```yaml
{{- $_ := set $np "Annotations" (dict
  "justification" "Reason for internet-wide egress"
  "approvedBy"    "Ticket reference or approver"
) -}}
{{- $_ := set $np "AllowEgressTo" (dict
  "internet" (dict
    "enabled" true
    "cidrs"   (list "0.0.0.0/0")
    "ports"   (list 443)
  )
) -}}
```

## Topology Guide — Which Policies You Need

For a typical 3-tier topology (`frontend` → `web-api` → `postgresql`):

| Workload | Ingress allows | Egress allows |
|---|---|---|
| `frontend` | router pods (`:8080`) | `web-api` on `:8080` |
| `web-api` | `frontend` + router pods (`:8080`) | `postgresql` on `:5432`, optional CIDR on `:443` |
| `postgresql` | `web-api` (`:5432`) | _(none — StatefulSet doesn't call out)_ |

**Rule:** Every workload with a Route must allow ingress from router pods. Every caller must allow egress AND every callee must allow ingress for the same port.

## Hard Deny Patterns (Conftest will reject these)

| Pattern | Why it's denied |
|---|---|
| `ingress: - {}` | Allows all traffic from all sources |
| Ingress rule with no `from` | Allows all sources |
| Ingress rule with no `ports` | Allows all ports |
| `egress: - {}` | Allows all traffic to all destinations |
| Egress rule with no `to` | Allows all destinations |
| Egress rule with no `ports` | Allows all ports |
| `podSelector: {}` peer inside `from`/`to` | Wildcard — matches all pods |
| Internet egress without `justification` + `approvedBy` annotations | Unapproved internet exposure |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Omitting `PolicyTypes` | Without it, only listed directions are restricted. Set explicitly. |
| Egress-only policy but no egress rules → egress-deny | If `PolicyTypes` includes `Egress` and you have no rules, all egress is blocked. Add at least one rule. |
| Using `podSelector: {}` as a peer | This matches ALL pods — equivalent to allow-all. Use `apps: [{name: ...}]` instead. |
| Setting `PolicyTypes: [Egress]` when you only care about ingress | Use `[Ingress]` to restrict only what you mean to restrict. |
