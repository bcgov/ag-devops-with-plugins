# AG DevOps — Shared CI/CD Library

## What this repo is

`ag-devops` is a **shared infrastructure library** — not an application. It gives BC Government (AG) development teams a ready-made, standards-compliant CI/CD foundation so teams don't have to solve the same problems independently.

It contains three distinct assets:

| Asset | Location | What it provides |
|---|---|---|
| **CI templates** | `ci/dotnetcore/` | Reusable GitHub Actions workflows and composite actions for .NET 8 |
| **Helm library chart** | `cd/shared-lib/ag-helm/` | Reusable Kubernetes/OpenShift resource templates (`ag-template.*`) |
| **Policy-as-code configs** | `cd/policies/` | Datree, Polaris, kube-linter, and Conftest/OPA rules enforced before every deploy |

---

## Purpose

Standardize how AG application teams build, test, package, and deploy software so that:

- All pipelines follow the same structure and quality gates
- Kubernetes manifests meet security and compliance requirements before they reach the cluster
- Teams starting new projects inherit a known-good baseline instead of building from scratch

---

## Target audience

**Application development teams** within BC Government (AG) who:

- Build .NET 8 services deployed to OpenShift
- Need a consistent, compliant path from source code to running workload
- Are deploying into a **deny-by-default** OpenShift cluster where explicit NetworkPolicy rules are required

This repo is **consumed** by app teams — it is maintained by a platform/DevOps team.

---

## Problems it solves

| Problem | How this repo addresses it |
|---|---|
| Inconsistent CI across teams | Shared reusable workflows mean every team builds, tests, and packages the same way |
| Copy-paste YAML drift | App charts depend on a versioned Helm library; fixes propagate on upgrade |
| Security and compliance gaps at deploy time | Four policy tools run on every rendered manifest before a deploy is allowed to proceed |
| Accidental allow-all NetworkPolicy rules | Rego hard-denies any policy with empty rules, missing peers, or missing ports |
| New team onboarding time | A single chart dependency + policy config file is enough to get a compliant deployment |
| Internet egress without review | Conftest enforces `justification` and `approvedBy` annotations on any `0.0.0.0/0` egress rule |

---

## How to use it

### CI (GitHub Actions)

1. Copy the relevant workflow files from `ci/dotnetcore/` into your app repo's `.github/workflows/`
2. Create a thin entry workflow that calls them — see `docs/CI.md` for a minimal example
3. Alternatively, reference composite actions cross-repo and pin to a release tag

### CD (Helm + policies)

1. Add the Helm library as a dependency in your app chart:
   ```yaml
   dependencies:
     - name: ag-helm-templates
       version: "1.0.3"
       repository: "oci://ghcr.io/bcgov-c/helm"
   ```
2. Use the `ag-template.*` entrypoints inside your chart templates to render Deployments, Services, Routes, NetworkPolicies, etc.
3. Before deploying, render your chart and run all four policy checks against the output:
   ```bash
   helm template my-release ./my-chart > rendered.yaml
   datree test rendered.yaml --policy-config cd/policies/datree-policies.yaml
   polaris audit --config cd/policies/polaris.yaml --format pretty rendered.yaml
   kube-linter lint rendered.yaml --config cd/policies/kube-linter.yaml
   conftest test rendered.yaml --policy cd/policies --all-namespaces --fail-on-warn
   ```

---

## What a typical app topology looks like

A standard AG application namespace contains:

```
frontend   → Deployment + Service + Route + NetworkPolicy
web-api    → Deployment + Service + Route + NetworkPolicy
postgresql → StatefulSet + Service + NetworkPolicy
```

Traffic flows through OpenShift's router (in `openshift-ingress`) → Route → Service → Pods.
Because the cluster is deny-by-default, **every workload must have an explicit NetworkPolicy**
granting only the traffic it actually needs.

---

## Reference docs

| Document | Purpose |
|---|---|
| `docs/CI.md` | Full CI workflow reference — all inputs, secrets, artifacts |
| `docs/CD.md` | Full CD reference — Helm library contract, policy tools, NetworkPolicy cookbook |
| `docs/DEVELOPERS-GUIDE.md` | App developer guide — deny-by-default cluster walkthrough |
| `cd/shared-lib/ag-helm/docs/SIMPLE-API.md` | Helm library API contract (inputs/outputs for every `ag-template.*`) |
| `cd/shared-lib/ag-helm/docs/EXAMPLES.md` | Copy/paste Helm template examples |

---

## Diagrams

- [`cicd-sequence.mmd`](cicd-sequence.mmd) — end-to-end CI/CD GitOps sequence
- [`deployment.mmd`](deployment.mmd) — all moving parts and services