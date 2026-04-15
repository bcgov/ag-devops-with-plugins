# Copilot Instructions

## Repository overview

This is a **shared DevOps library** for application teams — not an application. It provides:

- Reusable GitHub Actions workflows and composite actions for .NET 8 CI (`ci/dotnetcore/`)
- A Helm **library chart** (`cd/shared-lib/ag-helm/`) published to GHCR OCI: `ghcr.io/bcgov-c/helm/ag-helm-templates`
- Policy-as-code configs for Kubernetes manifests (`cd/policies/`)
- An example consumer chart (`cd/shared-lib/example-app/`)
- A **Claude Code plugin** (`plugins/ag-devops/`) v2.0 with scripted skills, agents, and commands for Emerald deployments

## Key documentation

- CI reference: `docs/CI.md`
- CD + policy reference: `docs/CD.md`
- Helm library API contract: `cd/shared-lib/ag-helm/docs/SIMPLE-API.md`
- Helm library copy/paste examples: `cd/shared-lib/ag-helm/docs/EXAMPLES.md`
- Publishing the Helm chart to GHCR: `cd/shared-lib/ag-helm/PUBLISHING.md`


## Claude Code Plugin (`plugins/ag-devops/`) — v2.0

The `ag-devops` plugin provides scripted skills and orchestrating agents for scaffolding compliant Emerald deployments. Skills write files directly to the workspace — no copy-paste.

> **AI agents:** Read `plugins/ag-devops/AGENTS.md` first — it is the authoritative entry point for the plugin's structure, skills, agents, and commands.

### Plugin structure

```
plugins/ag-devops/
├── AGENTS.md              ← AI agent entry point
├── .claude-plugin/
│   ├── plugin.json        ← manifest: 20 skills, 3 agents, 21 commands (v2.0.0)
│   └── marketplace.json   ← marketplace registration
├── scripts/
│   ├── scaffold.py        ← UNIFIED scaffold CLI (16 resource types via --type)
│   └── validate.py        ← 4-tool validation pipeline runner
├── assets/
│   ├── templates/         ← 25 canonical .tpl.yaml/.tpl.yml templates (physical files)
│   └── policies/          ← symlinks → cd/policies/
├── references/            ← symlinks → docs/ and ag-helm/docs/
├── skills/                ← 20 scripted skills
├── agents/                ← 3 orchestration agents
└── commands/              ← 21 slash commands (/ag-*)
```

Templates are physical at the plugin root; skill `scripts/scaffold.py` and `assets/templates/` dirs contain file-level symlinks (ADR-003). On marketplace install, symlinks become hard copies — fully self-contained.

### v2.0 Architecture: Unified scaffold.py

All 16 resource types go through one script:

```bash
python ./scripts/scaffold.py --type deployment --name web-api --port 8080
python ./scripts/scaffold.py --type networkpolicy --name web-api --ingress-from-router
python ./scripts/scaffold.py --type configmap --name app-config
python ./scripts/scaffold.py --dry-run --type pvc --name pg-data
python ./scripts/scaffold.py --help
```

Templates use `@@VAR@@` markers (not Jinja2), plain `str.replace()` — no conflict with Helm `{{ }}`. Post-render guard hard-fails on any unreplaced `@@` marker.

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

### Agents (3)

| Agent | Invoked by | What it does |
|---|---|---|
| `init-emerald` | `/ag-init` | Bootstraps `.github/workflows/`, `gitops/`, `Makefile`, `CODEOWNERS`, `AGENTS.md` |
| `scaffold-emerald-app` | `/ag-scaffold` | Topology-aware: calls scaffold-* skills per component, auto-generates NetworkPolicies |
| `manifest-validator` | `/ag-validate` | Runs all 4 policy tools via `validate.py`, returns structured remediation |

### Scripted Skills — Helm Fragments (14)

| Skill | Command | `--type` | Output |
|---|---|---|---|
| `scaffold-deployment` | `/ag-deployment` | `deployment` | `<name>-deployment.yaml` |
| `scaffold-service` | `/ag-service` | `service` | `<name>-service.yaml` |
| `scaffold-route` | `/ag-route` | `route` | `<name>-route.yaml` |
| `scaffold-statefulset` | `/ag-statefulset` | `statefulset` | `<name>-statefulset.yaml` |
| `scaffold-hpa` | `/ag-hpa` | `hpa` | `<name>-hpa.yaml` |
| `scaffold-pdb` | `/ag-pdb` | `pdb` | `<name>-pdb.yaml` |
| `scaffold-ingress` | `/ag-ingress` | `ingress` | `<name>-ingress.yaml` |
| `scaffold-serviceaccount` | `/ag-serviceaccount` | `serviceaccount` | `<name>-serviceaccount.yaml` |
| `scaffold-pvc` | `/ag-pvc` | `pvc` | `<name>-pvc.yaml` |
| `scaffold-job` | `/ag-job` | `job` | `<name>-job.yaml` |
| `scaffold-networkpolicy` | `/ag-networkpolicy` | `networkpolicy` | `<name>-networkpolicy.yaml` |
| `scaffold-configmap` | `/ag-configmap` | `configmap` | `<name>-configmap.yaml` |
| `scaffold-cronjob` | `/ag-cronjob` | `cronjob` | `<name>-cronjob.yaml` |
| `scaffold-externalsecret` | `/ag-externalsecret` | `externalsecret` | `<name>-externalsecret.yaml` |

### Scripted Skills — CI/CD & Validation (6)

| Skill | Command | What it generates |
|---|---|---|
| `init-emerald-repo` | `/ag-init` | Full repo boilerplate (ci.yml, cd.yml, Chart.yaml, values*.yaml, Makefile, CODEOWNERS, AGENTS.md) |
| `scaffold-docker-ci` | `/ag-docker-ci` | Docker build + push GitHub Actions workflow |
| `scaffold-sast-ci` | `/ag-sast-ci` | SAST/CodeQL GitHub Actions workflow |
| `setup-dotnet-ci` | `/ag-setup-ci` | .NET 8 CI pipeline wiring |
| `validate-emerald-manifests` | `/ag-validate` | Runs `validate.py`: helm template → datree → polaris → kube-linter → conftest/OPA |
| `author-networkpolicy` | `/ag-networkpolicy` | Guided NetworkPolicy authoring |

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

Or use the plugin's automation:
```bash
python plugins/ag-devops/scripts/validate.py --chart ./my-chart --release my-release
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
| NetworkPolicy namespace isolation | ❌ | ❌ | ❌ | ✅ |
| Route AVI annotation | ✅ | ✅ | ❌ | ✅ |
| Route edge termination approval | ❌ | ❌ | ❌ | ✅ |

## NetworkPolicy rules (`cd/policies/network-policies.rego`)

The Rego policy **hard denies** any of these patterns:

- Deployment without a matching NetworkPolicy
- `ingress: - {}` or `egress: - {}` (empty/wildcard rules)
- Ingress rules missing `from` or `ports`
- Egress rules missing `to` or `ports`
- Empty peer selectors inside `from/to` (e.g. `podSelector: {}`)
- `podSelector` without `namespaceSelector` in an ingress peer (namespace isolation violation)
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