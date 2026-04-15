# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **shared DevOps library** for application teams. It is not an application. It provides:

- Reusable GitHub Actions workflows and composite actions for .NET 8 CI (`ci/dotnetcore/`)
- A Helm **library chart** (`cd/shared-lib/ag-helm/`) published to GHCR OCI: `ghcr.io/bcgov-c/helm/ag-helm-templates`
- Policy-as-code configs for Kubernetes manifests (`cd/policies/`)
- An example consumer chart (`cd/shared-lib/example-app/`)
- A **Claude Code plugin** (`plugins/ag-devops/`) with scripted skills and orchestrating agents for Emerald deployments

## Working with the Helm library chart

```bash
# Validate and render the example consumer chart locally
helm dependency update ./cd/shared-lib/example-app
helm lint ./cd/shared-lib/example-app
helm template ex ./cd/shared-lib/example-app --values ./cd/shared-lib/example-app/values-examples.yaml --debug

# Render any chart for policy testing
helm template my-release ./my-chart > rendered.yaml
```

## Running policy checks

All policy tools operate on **rendered YAML** (not on chart source). The standard pipeline pattern:

```bash
# 1. Render
helm template my-release ./my-chart > rendered.yaml

# 2. Datree — org label/schema rules
datree test rendered.yaml --policy-config cd/policies/datree-policies.yaml

# 3. Polaris — security and reliability best practices
polaris audit --config cd/policies/polaris.yaml --format pretty rendered.yaml

# 4. kube-linter — Kubernetes lint checks
kube-linter lint rendered.yaml --config cd/policies/kube-linter.yaml

# 5. Conftest/OPA — hard deny Rego rules (NetworkPolicy, Route termination, AVI annotations)
conftest test rendered.yaml --policy cd/policies --all-namespaces --fail-on-warn
```

## Releases

Releases are automated via **Semantic Release** (`.releaserc.json`) triggered on pushes to `main`. Use [Conventional Commits](https://www.conventionalcommits.org/):

- `fix:` → patch release
- `feat:` → minor release
- `feat!:` / `BREAKING CHANGE:` footer → major release

On a new tag, the release workflow (`release.yml`) packages and pushes the Helm chart to GHCR OCI automatically.

## Architecture: Helm library chart (`cd/shared-lib/ag-helm/`)

### "Set + define + include" authoring pattern

The library uses a single dict (`$p`) as the parameter object because `include` accepts only one argument. Callers:
1. **Set** required keys on the dict (`ApplicationGroup`, `Name`, `Registry`, `ModuleValues`)
2. **Define** small YAML fragments named as strings (ports, env, probes)
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

Workloads: `deployment`, `statefulset`, `job`
Networking: `service`, `route.openshift`, `ingress`, `networkpolicy`
Reliability: `hpa`, `pdb`, `pvc`, `priorityclass`
Identity: `serviceaccount`

ConfigMap, Secret, and CronJob templates are intentionally **not** provided.

### Fragment output shapes (common source of bugs)

- **List item** (emit `- ...`): `Ports`, `Env`, `ServicePorts`, `VolumeMounts`, `Volumes`, `InitContainers`, `IngressTemplate`, `EgressTemplate`
- **Map** (emit key/value without `-`): `LabelData`, `AnnotationData`, `Selector`
- **Inline object** (emit full keys): `Probes`, `Lifecycle`, `SecurityContext`, `Resources`

### DataClass label

All workloads must have `ModuleValues.dataClass: low|medium|high` (defaults to `low`). Invalid values **fail templating**. This becomes the `data-class` pod label and is checked by all policy tools.

### OpenShift mode

Set `global.openshift: true` in chart values. This suppresses `runAsUser`/`runAsGroup` pinning so OpenShift SCC can assign runtime UID/GID.

## Architecture: NetworkPolicy rules (`cd/policies/network-policies.rego`)

The Rego policy **hard denies** any of these patterns:

- Deployment without a matching NetworkPolicy
- `ingress: - {}` or `egress: - {}` (empty rules)
- Ingress rules missing `from` or missing `ports`
- Egress rules missing `to` or missing `ports`
- Empty peer selectors inside `from/to` (e.g. `podSelector: {}`)
- Internet egress (`0.0.0.0/0`) without both `justification` and `approvedBy` annotations

Prefer `AllowIngressFrom` / `AllowEgressTo` intent inputs on `ag-template.networkpolicy` over raw rules — they are designed to avoid accidental allow-all shapes.

## Architecture: policy matrix

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


## Claude Code Plugin (`plugins/ag-devops/`)

This repo ships a Claude Code plugin that agents and teams can install via the marketplace. It provides scripted skills (Python scripts that write files directly) and orchestrating agents.

### Plugin structure

```
plugins/ag-devops/
├── AGENTS.md              ← AI agent entry point — read this first
├── plugin.json            ← manifest: 18 skills, 5 agents, 17 commands
├── symlinks.json          ← 80 registered symlinks (restore: symlink_manager.py restore)
├── assets/
│   ├── templates/         ← CANONICAL .yaml.j2 / .yml.j2 templates (21 files, physical)
│   └── policies/          ← symlinks → cd/policies/
├── references/            ← symlinks → docs/ and ag-helm/docs/
├── skills/                ← 18 scripted skills
├── agents/                ← 5 orchestration agents
└── commands/              ← 17 slash commands (/ag-*)
```

Each skill's `assets/templates/` and `references/` contain file-level symlinks → plugin root (ADR-003). Scripts stay physically in each skill's `scripts/` (ADR-002 single-skill rule).

### Installation

```bash
# Claude Code
/plugin marketplace add bcgov-c/ag-devops
/plugin install ag-devops@ag-devops-marketplace

# GitHub Copilot CLI
copilot plugin marketplace add bcgov-c/ag-devops
copilot plugin install ag-devops@ag-devops-marketplace

# Team auto-install — add to your app repo's .claude/settings.json
{
  "extraKnownMarketplaces": {
    "ag-devops-marketplace": { "source": { "source": "github", "repo": "bcgov-c/ag-devops" } }
  },
  "enabledPlugins": { "ag-devops@ag-devops-marketplace": true }
}
```

### Scripted Skills

Each skill has `scripts/generate.py` (or `scripts/init.py`) that renders templates and writes output files directly to the workspace — no copy-paste needed. Templates use `@@VAR@@` markers (not Jinja2) to avoid conflicts with Helm `{{ }}` syntax.

**Helm Chart Fragment Generators**

| Skill | Command | Output |
|---|---|---|
| `scaffold-deployment` | `/ag-deployment` | `gitops/templates/<name>-deployment.yaml` |
| `scaffold-service` | `/ag-service` | `gitops/templates/<name>-service.yaml` |
| `scaffold-route` | `/ag-route` | `gitops/templates/<name>-route.yaml` |
| `scaffold-statefulset` | `/ag-statefulset` | `gitops/templates/<name>-statefulset.yaml` |
| `scaffold-hpa` | `/ag-hpa` | `gitops/templates/<name>-hpa.yaml` |
| `scaffold-pdb` | `/ag-pdb` | `gitops/templates/<name>-pdb.yaml` |
| `scaffold-ingress` | `/ag-ingress` | `gitops/templates/<name>-ingress.yaml` |
| `scaffold-serviceaccount` | `/ag-serviceaccount` | `gitops/templates/<name>-serviceaccount.yaml` |
| `scaffold-pvc` | `/ag-pvc` | `gitops/templates/<name>-pvc.yaml` |
| `scaffold-job` | `/ag-job` | `gitops/templates/<name>-job.yaml` |
| `scaffold-networkpolicy` | `/ag-networkpolicy` | `gitops/templates/<name>-networkpolicy.yaml` |
| `scaffold-openshift-deployment` | — | Deployment with OpenShift SCC-safe settings |

**CI/CD & Validation**

| Skill | Command | What it generates |
|---|---|---|
| `init-emerald-repo` | `/ag-init` | Full repo boilerplate — `ci.yml`, `cd.yml`, `Chart.yaml`, `values*.yaml`, `Makefile`, `CODEOWNERS`, `AGENTS.md` |
| `scaffold-docker-ci` | `/ag-docker-ci` | Docker build + push GitHub Actions workflow |
| `scaffold-sast-ci` | `/ag-sast-ci` | SAST/CodeQL GitHub Actions workflow |
| `setup-dotnet-ci` | `/ag-setup-ci` | .NET 8 CI pipeline wiring |
| `validate-emerald-manifests` | `/ag-validate` | Renders chart, runs datree + polaris + kube-linter + conftest/OPA |
| `author-networkpolicy` | `/ag-networkpolicy` | Guided NetworkPolicy authoring |

### Agents

| Agent | Invoked by | Role |
|---|---|---|
| `init-emerald` | `/ag-init` | Asks 8 questions → runs `init-emerald-repo` skill → bootstraps `.github/workflows/`, `gitops/`, `Makefile`, `CODEOWNERS`, `AGENTS.md` |
| `scaffold-emerald-app` | `/ag-scaffold` | Topology-aware orchestrator — calls all scaffold skills per component, auto-generates NetworkPolicies |
| `helm-scaffolder` | `/ag-scaffold` | Helm chart fragment authoring assistant |
| `manifest-validator` | `/ag-validate` | Runs all 4 policy tools, returns structured remediation |
| `initialize-emerald-repo` | (legacy) | Replaced by `init-emerald` |

### AGENTS.md

`/ag-init` writes an `AGENTS.md` to the **project root** of the user's repo. This file describes the gitops layout so any AI agent working in that repo understands the structure without reading every file.

## Key documentation

- Full CI reference: `docs/CI.md`
- Full CD + policy reference: `docs/CD.md`
- Helm library API contract: `cd/shared-lib/ag-helm/docs/SIMPLE-API.md`
- Helm library copy/paste examples: `cd/shared-lib/ag-helm/docs/EXAMPLES.md`
- Publishing the Helm chart to GHCR: `cd/shared-lib/ag-helm/PUBLISHING.md`