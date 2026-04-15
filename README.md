# AG Reusable DevOps Template and Library

Shared CI/CD templates, policy-as-code, and an AI-assisted Claude Code plugin for BC Government AG application teams deploying to OpenShift Emerald.

[![CI](https://img.shields.io/badge/CI-.NET%208-blue)](#ci-templates)
[![CD](https://img.shields.io/badge/CD-Helm%20%2B%20Policies-purple)](#cd--helm-library)
[![Helm](https://img.shields.io/badge/Helm-Library%20Chart-0F1689)](#cd--helm-library)
[![Policies](https://img.shields.io/badge/Policies-Datree%20%7C%20Polaris%20%7C%20kube--linter%20%7C%20OPA-orange)](#policy-checks)
[![Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet)](#claude-code-plugin)

---

## What this repo is

This repository is a **shared DevOps library** for application teams. It is not an application. It provides:

- **CI templates** — reusable GitHub Actions workflows and composite actions for .NET 8 (`ci/dotnetcore/`)
- **Helm library chart** — `ag-helm-templates` published to GHCR OCI (`cd/shared-lib/ag-helm/`)
- **Policy-as-code** — Datree, Polaris, kube-linter, and Conftest/OPA configs for Kubernetes manifests (`cd/policies/`)
- **Claude Code plugin** — AI agents and scripted skills that scaffold entire repos in one command (`plugins/ag-devops/`)

---

## Claude Code Plugin

The `ag-devops` plugin gives Claude Code the tools to scaffold a fully policy-compliant Emerald deployment without copy-paste. One agent conversation generates every file your repo needs.

### What it does

| Command / Agent | What happens |
|---|---|
| `/ag-init` → `init-emerald` agent | Asks 8 questions → runs `init.py` → writes `.github/workflows/`, `gitops/`, `Makefile`, `CODEOWNERS`, `.gitignore` |
| `/ag-scaffold` → `scaffold-emerald-app` agent | Asks topology questions → calls scripted skills → writes one template file per resource directly into `gitops/templates/` |
| `/ag-validate` → `manifest-validator` agent | Renders the chart → runs all 4 policy tools → returns structured remediation |
| `/ag-networkpolicy` | Generates a compliant NetworkPolicy via `scaffold-networkpolicy` script |

### Scripted Skills (Python — write files, no copy-paste)

| Skill | Script | Output |
|---|---|---|
| `scaffold-deployment` | `scripts/generate.py --name web-api --port 8080` | `gitops/templates/web-api-deployment.yaml` |
| `scaffold-service` | `scripts/generate.py --name web-api --port 8080` | `gitops/templates/web-api-service.yaml` |
| `scaffold-route` | `scripts/generate.py --name web-api --data-class low` | `gitops/templates/web-api-route.yaml` |
| `scaffold-networkpolicy` | `scripts/generate.py --name web-api --ingress-from-router` | `gitops/templates/web-api-networkpolicy.yaml` |
| `init-emerald-repo` | `scripts/init.py --project my-app --registry ghcr.io/bcgov-c` | Full repo boilerplate (10 files) |

### Installation

#### Claude Code (via Plugin Marketplace)

```bash
/plugin marketplace add bcgov-c/ag-devops
/plugin install ag-devops@ag-devops-marketplace
```

#### GitHub Copilot CLI

```bash
copilot plugin marketplace add bcgov-c/ag-devops
copilot plugin install ag-devops@ag-devops-marketplace
```

#### Team Auto-Install (recommended)

Add to your app repo's `.claude/settings.json` and commit — every collaborator gets the plugin automatically:

```json
{
  "extraKnownMarketplaces": {
    "ag-devops-marketplace": {
      "source": {
        "source": "github",
        "repo": "bcgov-c/ag-devops"
      }
    }
  },
  "enabledPlugins": {
    "ag-devops@ag-devops-marketplace": true
  }
}
```

#### Pin to a release (production)

```json
{ "source": { "source": "github", "repo": "bcgov-c/ag-devops", "ref": "v1.1.0" } }
```

#### Verify Installation

Start a new session and ask: *"Initialize my repo for Emerald"* or *"Scaffold a web-api deployment"*. The agent will automatically invoke the relevant skill.

---

## Repository Structure

```
ag-devops/
  ci/dotnetcore/             <- reusable .NET 8 GitHub Actions workflows + composite actions
  cd/shared-lib/ag-helm/     <- Helm library chart (ag-helm-templates)
  cd/shared-lib/example-app/ <- example consumer chart
  cd/policies/               <- Datree, Polaris, kube-linter, Conftest/OPA configs
  plugins/ag-devops/         <- Claude Code plugin (agents, skills, commands)
  docs/                      <- full CI and CD reference documentation
```

---

## CI Templates

> Use these when you want consistent .NET 8 build/test/pack steps across repos.

Templates and composite actions live in [`ci/dotnetcore/`](ci/dotnetcore/). Full reference: [`docs/CI.md`](docs/CI.md).

**Minimum entry workflow** in your app repo:

```yaml
jobs:
  restore:
    uses: ./.github/workflows/dotnet-8-dependencies.yml
    with: { dotnet_build_path: ./MySolution.sln }
  build:
    needs: restore
    uses: ./.github/workflows/dotnet-8-build.yml
    with: { dotnet_build_path: ./MySolution.sln, warn_as_error: true }
  test:
    needs: build
    uses: ./.github/workflows/dotnet-8-tests-msbuild.yml
    with: { unit_test_folder: "tests/MyApp.Tests", coverage_threshold: 80 }
```

---

## CD + Helm Library

> Use these when you deploy via Helm and want enforced Kubernetes/OpenShift standards.

- Helm library chart: [`cd/shared-lib/ag-helm/`](cd/shared-lib/ag-helm/)
- Example consumer: [`cd/shared-lib/example-app/`](cd/shared-lib/example-app/)
- API contract: [`cd/shared-lib/ag-helm/docs/SIMPLE-API.md`](cd/shared-lib/ag-helm/docs/SIMPLE-API.md)
- Full reference: [`docs/CD.md`](docs/CD.md)

**Every resource uses the "set + define + include" pattern:**

```yaml
{{- $p := dict "Values" .Values -}}
{{- $_ := set $p "Name" "web-api" -}}
{{- $_ := set $p "ModuleValues" .Values.webApi -}}
{{- $_ := set $p "Ports" "webapi.ports" -}}
{{ include "ag-template.deployment" $p }}
```

---

## Policy Checks

All four tools run against **rendered YAML** (not chart source). The CD pipeline enforces them before every deploy.

```bash
helm template my-release ./gitops > rendered.yaml
datree test rendered.yaml --policy-config cd/policies/datree-policies.yaml
polaris audit --config cd/policies/polaris.yaml --format pretty rendered.yaml
kube-linter lint rendered.yaml --config cd/policies/kube-linter.yaml
conftest test rendered.yaml --policy cd/policies --all-namespaces --fail-on-warn
```

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

---

## Releases

Releases are automated via **Semantic Release** on pushes to `main`. Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Release |
|---|---|
| `fix:` | patch |
| `feat:` | minor |
| `feat!:` / `BREAKING CHANGE:` | major |

On a new tag, `release.yml` packages and pushes the Helm chart to GHCR OCI automatically.

---

## Quick Links

- Start here (CI/CD): [docs/CI-CD-START-HERE.md](docs/CI-CD-START-HERE.md)
- Developer guide: [docs/DEVELOPERS-GUIDE.md](docs/DEVELOPERS-GUIDE.md)
- CI reference: [docs/CI.md](docs/CI.md)
- CD reference: [docs/CD.md](docs/CD.md)
- Helm API contract: [cd/shared-lib/ag-helm/docs/SIMPLE-API.md](cd/shared-lib/ag-helm/docs/SIMPLE-API.md)
- Publishing the chart: [cd/shared-lib/ag-helm/PUBLISHING.md](cd/shared-lib/ag-helm/PUBLISHING.md)
