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

Or use the plugin's validate.py for the same pipeline:
```bash
python plugins/ag-devops/scripts/validate.py --chart ./my-chart --release my-release
```

## Running plugin tests

```bash
cd tests
pytest test_scaffold.py -v          # 26 tests covering all 16 scaffold types
pytest test_scaffold.py --update-fixtures  # regenerate golden fixtures
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
- `podSelector` without `namespaceSelector` in an ingress peer (namespace isolation violation)
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
| NetworkPolicy namespace isolation | ❌ | ❌ | ❌ | ✅ |
| Route AVI annotation | ✅ | ✅ | ❌ | ✅ |
| Route edge termination approval | ❌ | ❌ | ❌ | ✅ |


## Claude Code Plugin (`plugins/ag-devops/`) — v2.0

This repo ships a Claude Code plugin that agents and teams can install via the marketplace.

### Plugin structure

```
plugins/ag-devops/
├── AGENTS.md              ← AI agent entry point — read this first
├── .claude-plugin/
│   ├── plugin.json        ← manifest: 20 skills, 3 agents, 21 commands (v2.0.0)
│   └── marketplace.json   ← marketplace registration
├── scripts/
│   ├── scaffold.py        ← UNIFIED scaffold CLI — all 16 resource types via --type
│   └── validate.py        ← 4-tool validation pipeline (helm → datree → polaris → kube-linter → conftest)
├── assets/
│   ├── templates/         ← 25 canonical .tpl.yaml / .tpl.yml templates (physical)
│   └── policies/          ← symlinks → cd/policies/
├── references/            ← symlinks → docs/ and ag-helm/docs/
├── skills/                ← 20 scripted skills
├── agents/                ← 3 orchestration agents
└── commands/              ← 21 slash commands (/ag-*)
```

### v2.0 scaffold.py — unified CLI

All Helm fragment generation goes through one script:

```bash
python ./scripts/scaffold.py --type deployment --name web-api --port 8080
python ./scripts/scaffold.py --type networkpolicy --name web-api --ingress-from-router
python ./scripts/scaffold.py --type configmap --name app-config
python ./scripts/scaffold.py --help
```

Templates are `*.tpl.yaml` / `*.tpl.yml` (not `.yaml.j2`). Markers use `@@VAR@@` style. A post-render guard hard-fails on any unreplaced `@@` marker.

### Skills (20 total)

Helm fragments: `scaffold-deployment`, `scaffold-service`, `scaffold-route`, `scaffold-statefulset`, `scaffold-hpa`, `scaffold-pdb`, `scaffold-ingress`, `scaffold-serviceaccount`, `scaffold-pvc`, `scaffold-job`, `scaffold-networkpolicy`, `scaffold-configmap`, `scaffold-cronjob`, `scaffold-externalsecret`

CI/CD: `scaffold-docker-ci`, `scaffold-sast-ci`, `init-emerald-repo`

Validation/authoring: `validate-emerald-manifests`, `author-networkpolicy`, `setup-dotnet-ci`

### Agents (3 total)

| Agent | Invoked by | Role |
|---|---|---|
| `init-emerald` | `/ag-init` | Full repo bootstrap |
| `scaffold-emerald-app` | `/ag-scaffold` | Topology-aware scaffold orchestrator |
| `manifest-validator` | `/ag-validate` | Policy validation + remediation |

### AGENTS.md

`/ag-init` writes an `AGENTS.md` to the **project root** of the user's repo. This file describes the gitops layout so any AI agent working in that repo understands the structure without reading every file.

## Key documentation

- Full CI reference: `docs/CI.md`
- Full CD + policy reference: `docs/CD.md`
- Helm library API contract: `cd/shared-lib/ag-helm/docs/SIMPLE-API.md`
- Helm library copy/paste examples: `cd/shared-lib/ag-helm/docs/EXAMPLES.md`
- Publishing the Helm chart to GHCR: `cd/shared-lib/ag-helm/PUBLISHING.md`