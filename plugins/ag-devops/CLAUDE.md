# ag-devops Plugin

This plugin gives Claude Code the skills and agents needed to help BC Government AG application teams deploy to OpenShift Emerald using the ag-devops shared library. Skills are **scripted** — Python scripts write files directly to the workspace, no copy-paste required.

## Scripted Skills (write files via Python)

| Skill | Trigger phrases | Script |
|---|---|---|
| `scaffold-deployment` | Creating a new deployment, new chart component | `scripts/generate.py --name <name> --port <port>` |
| `scaffold-service` | Creating a new service, exposing a workload | `scripts/generate.py --name <name> --port <port>` |
| `scaffold-route` | Creating a route, exposing via OpenShift router | `scripts/generate.py --name <name> --data-class <class>` |
| `scaffold-networkpolicy` | NetworkPolicy needed, Conftest allow-all denial | `scripts/generate.py --name <name> [topology flags]` |
| `init-emerald-repo` | Initialize repo, boilerplate, first-time setup | `scripts/init.py --project <name> --registry <registry>` |

## Guidance Skills (pattern + reference)

| Skill | Triggers on |
|---|---|
| `scaffold-openshift-deployment` | Manual chart authoring reference |
| `validate-emerald-manifests` | Policy check failures, pre-deploy validation |
| `author-networkpolicy` | NetworkPolicy logic questions, manual authoring |
| `setup-dotnet-ci` | Wiring up .NET 8 CI pipelines |

## Slash Commands

| Command | What it does |
|---|---|
| `/ag-init` | **Start here** — full repo initialization |
| `/ag-scaffold` | Scaffold Helm chart resources for a component |
| `/ag-validate` | Run all four policy checks + remediation |
| `/ag-networkpolicy` | Generate a compliant NetworkPolicy |
| `/ag-setup-ci` | Set up .NET 8 GitHub Actions CI |

## Agents

| Agent | Role |
|---|---|
| `init-emerald` | Asks 8 questions → runs `init-emerald-repo` skill → bootstraps the full repo structure |
| `scaffold-emerald-app` | Topology-aware orchestrator — calls all 4 scaffold skills per component, auto-generates NetworkPolicies |
| `initialize-emerald-repo` | Legacy guidance-only init agent |
| `manifest-validator` | Called by `/ag-validate` — runs policy tools and structures output |
| `helm-scaffolder` | Called by `/ag-scaffold` — Helm chart scaffolding guidance |

## Template substitution pattern

All templates use `@@VAR@@`-style markers instead of Jinja2 to avoid conflicts with Helm `{{ }}` Go template syntax. Scripts use plain `str.replace()` — no extra dependencies required.

## Installation (from an app repo)

```bash
# Claude Code marketplace
/plugin marketplace add bcgov-c/ag-devops
/plugin install ag-devops@ag-devops-marketplace

# Team auto-install via .claude/settings.json
{
  "extraKnownMarketplaces": {
    "ag-devops-marketplace": { "source": { "source": "github", "repo": "bcgov-c/ag-devops" } }
  },
  "enabledPlugins": { "ag-devops@ag-devops-marketplace": true }
}
```

## Policy files

All policy configs live in `cd/policies/` in this repo. Skills reference them directly — no separate config needed when running inside the ag-devops repo.
