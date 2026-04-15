# Copilot Instructions

## Repository overview

This is a **shared DevOps library** for application teams — not an application. It provides:

- Reusable GitHub Actions workflows and composite actions for .NET 8 CI (`ci/dotnetcore/`)
- A Helm **library chart** (`cd/shared-lib/ag-helm/`) published to GHCR OCI: `ghcr.io/bcgov-c/helm/ag-helm-templates`
- Policy-as-code configs for Kubernetes manifests (`cd/policies/`)
- An example consumer chart (`cd/shared-lib/example-app/`)

## Key documentation

- CI reference: `docs/CI.md`
- CD + policy reference: `docs/CD.md`
- Helm library API contract: `cd/shared-lib/ag-helm/docs/SIMPLE-API.md`
- Helm library copy/paste examples: `cd/shared-lib/ag-helm/docs/EXAMPLES.md`
- Publishing the Helm chart to GHCR: `cd/shared-lib/ag-helm/PUBLISHING.md`


## Claude Code Plugin (`plugins/ag-devops/`)

The `ag-devops` plugin provides scripted skills and orchestrating agents for scaffolding compliant Emerald deployments. Skills write files directly to the workspace — no copy-paste.

### Installation

```bash
# Claude Code
/plugin marketplace add bcgov-c/ag-devops
/plugin install ag-devops@ag-devops-marketplace

# GitHub Copilot CLI
copilot plugin marketplace add bcgov-c/ag-devops
copilot plugin install ag-devops@ag-devops-marketplace
```

**Team auto-install** — add to your app repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ag-devops-marketplace": {
      "source": { "source": "github", "repo": "bcgov-c/ag-devops" }
    }
  },
  "enabledPlugins": { "ag-devops@ag-devops-marketplace": true }
}
```

### Agents

| Agent | Invoked by | What it does |
|---|---|---|
| `init-emerald` | `/ag-init` | Bootstraps `.github/workflows/`, `gitops/`, `Makefile`, `CODEOWNERS`, `.gitignore` |
| `scaffold-emerald-app` | `/ag-scaffold` | Topology-aware: calls all 4 scaffold skills per component, auto-generates NetworkPolicies |
| `manifest-validator` | `/ag-validate` | Runs all 4 policy tools, returns structured remediation |

### Scripted Skills

| Skill | Output file |
|---|---|
| `scaffold-deployment` | `gitops/templates/<name>-deployment.yaml` |
| `scaffold-service` | `gitops/templates/<name>-service.yaml` |
| `scaffold-route` | `gitops/templates/<name>-route.yaml` |
| `scaffold-networkpolicy` | `gitops/templates/<name>-networkpolicy.yaml` |
| `init-emerald-repo` | Full repo boilerplate (10 files) |
## Helm library chart (`cd/shared-lib/ag-helm/`)

### "Set + define + include" authoring pattern

The library uses a single dict (`$p`) as the parameter object because Helm `include` accepts only one argument. Callers must:

1. **Set** required keys on the dict: `ApplicationGroup`, `Name`, `Registry`, `ModuleValues`
2. **Define** named YAML fragment templates (ports, env, probes, etc.)
3. **Include** a public `ag-template.*` entrypoint

```yaml
{{- $p := dict "Values" .Values -}}
{{- $_ := set $p "ApplicationGroup" .Values.project -}}
{{- $_ := set $p "Name" "web-api" -}}
{{- $_ := set $p "Registry" "ghcr.io/my-org" -}}
{{- $_ := set $p "ModuleValues" .Values.backend -}}
{{- $_ := set $p "Ports" "webapi.ports" -}}
{{ include "ag-template.deployment" $p }}

{{- define "webapi.ports" -}}
- name: http
  containerPort: 8080
  protocol: TCP
{{- end }}
```

### Public entrypoints (`ag-template.*`)

| Category | Templates |
|---|---|
| Workloads | `deployment`, `statefulset`, `job` |
| Networking | `service`, `route.openshift`, `ingress`, `networkpolicy` |
| Reliability | `hpa`, `pdb`, `pvc`, `priorityclass` |
| Identity | `serviceaccount` |

> ConfigMap, Secret, and CronJob templates are intentionally **not** provided.

### Fragment output shapes

This is a common source of bugs — each fragment type must emit the correct YAML shape:

- **List item** (emit `- ...`): `Ports`, `Env`, `ServicePorts`, `VolumeMounts`, `Volumes`, `InitContainers`, `IngressTemplate`, `EgressTemplate`
- **Map** (emit key/value, no `-`): `LabelData`, `AnnotationData`, `Selector`
- **Inline object** (emit full keys): `Probes`, `Lifecycle`, `SecurityContext`, `Resources`

### DataClass label

All workloads require `ModuleValues.dataClass: low|medium|high` (defaults to `low`). Invalid values **fail templating**. This value becomes the `data-class` pod label enforced by all policy tools.

### OpenShift mode

Set `global.openshift: true` to suppress `runAsUser`/`runAsGroup` pinning and let OpenShift SCC assign runtime UID/GID.

### Local validation commands

```bash
helm dependency update ./cd/shared-lib/example-app
helm lint ./cd/shared-lib/example-app
helm template ex ./cd/shared-lib/example-app --values ./cd/shared-lib/example-app/values-examples.yaml --debug
```

## Policy checks

All policy tools operate on **rendered YAML**, not chart source. Always render first:

```bash
helm template my-release ./my-chart > rendered.yaml
```

Then run the full policy suite:

```bash
# Org label/schema rules
datree test rendered.yaml --policy-config cd/policies/datree-policies.yaml

# Security and reliability best practices
polaris audit --config cd/policies/polaris.yaml --format pretty rendered.yaml

# Kubernetes lint checks
kube-linter lint rendered.yaml --config cd/policies/kube-linter.yaml

# Hard deny Rego rules (NetworkPolicy, Route termination, AVI annotations)
conftest test rendered.yaml --policy cd/policies --all-namespaces --fail-on-warn
```

### Policy matrix

| Concern | Datree | Polaris | kube-linter | Conftest/OPA |
|---|:---:|:---:|:---:|:---:|
| DataClass label | ✅ | ✅ | ❌ | ✅ |
| Owner/environment labels | ✅ | ❌ | ✅ | ❌ |
| Image tags / floating tag | ✅ | ✅ | ✅ | ❌ |
| Privileged / host namespaces | ✅ | ✅ | ✅ | ❌ |
| Resource requests/limits | ✅ | ✅ | ❌ | ❌ |
| Probes | ✅ | ✅ | ❌ | ❌ |
| NetworkPolicy exists | ✅ | ✅ | ❌ | ✅ |
| NetworkPolicy not allow-all | ✅ | partial | ❌ | ✅ |
| Route AVI annotation | ✅ | ✅ | ❌ | ✅ |
| Route edge termination approval | ❌ | ❌ | ❌ | ✅ |

## NetworkPolicy rules (`cd/policies/network-policies.rego`)

The Rego policy **hard denies** any of these patterns:

- Deployment without a matching NetworkPolicy
- `ingress: - {}` or `egress: - {}` (empty/wildcard rules)
- Ingress rules missing `from` or `ports`
- Egress rules missing `to` or `ports`
- Empty peer selectors inside `from/to` (e.g. `podSelector: {}`)
- Internet egress (`0.0.0.0/0`) without both `justification` and `approvedBy` annotations

Prefer `AllowIngressFrom` / `AllowEgressTo` intent inputs on `ag-template.networkpolicy` over raw rules to avoid accidental allow-all shapes.

## Releases

Releases are automated via **Semantic Release** (`.releaserc.json`) on pushes to `main`. Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Commit prefix | Release type |
|---|---|
| `fix:` | patch |
| `feat:` | minor |
| `feat!:` or `BREAKING CHANGE:` footer | major |

On a new tag, `release.yml` packages and pushes the Helm chart to GHCR OCI automatically.
