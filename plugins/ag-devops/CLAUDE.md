# ag-devops Plugin

This plugin gives Claude Code the skills and agents needed to help BC Government AG application teams deploy to OpenShift Emerald using the ag-devops shared library.

## Skills (auto-loaded based on context)

| Skill | Triggers on |
|---|---|
| `scaffold-openshift-deployment` | Creating new charts, setting up Emerald deployments from scratch |
| `validate-emerald-manifests` | Policy check failures, pre-deploy validation, CI failures |
| `author-networkpolicy` | Writing or fixing NetworkPolicies, Conftest allow-all denials |
| `setup-dotnet-ci` | Wiring up .NET 8 CI pipelines with shared workflow templates |

## Slash Commands

| Command | What it does |
|---|---|
| `/ag-init` | **Start here** — full repo initialization, generates everything for a new project |
| `/ag-scaffold` | Scaffold a Helm chart only (existing repo, no CI/CD) |
| `/ag-validate` | Run all four policy checks + remediation |
| `/ag-networkpolicy` | Generate a compliant NetworkPolicy for a workload |
| `/ag-setup-ci` | Set up .NET 8 GitHub Actions CI only |

## Agents

| Agent | When invoked |
|---|---|
| `initialize-emerald-repo` | Called by `/ag-init` — generates every file a new repo needs to deploy to Emerald |
| `manifest-validator` | Called by `/ag-validate` — runs policy tools and structures output |
| `helm-scaffolder` | Called by `/ag-scaffold` — generates complete chart files |

## Policy files

All policy configs live in `cd/policies/` in this repo. Skills reference them directly — no separate config needed when running inside the ag-devops repo.

## Installing from another repo

To use this plugin in an app repo, install it via the Claude Code plugin marketplace or reference it locally:

```bash
# Via marketplace (once published)
claude plugin install ag-devops

# Local install (from ag-devops repo root)
claude plugin install ./plugins/ag-devops
```
