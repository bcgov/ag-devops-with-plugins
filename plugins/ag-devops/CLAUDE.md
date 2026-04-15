# ag-devops Plugin v2.0

This plugin gives Claude Code the skills and agents needed to help BC Government AG application teams deploy to OpenShift Emerald using the ag-devops shared library. Skills are **scripted** — a unified Python CLI writes files directly to the workspace, no copy-paste required.

## Scripted Skills — Helm Fragment Generators

All 16 resource types go through one shared CLI: `scripts/scaffold.py --type <resource>`.

| Skill | Trigger phrases | Invocation |
|---|---|---|
| `scaffold-deployment` | New deployment, new chart component | `python ./scripts/scaffold.py --type deployment --name <name> --port <port>` |
| `scaffold-service` | New service, expose a workload | `python ./scripts/scaffold.py --type service --name <name> --port <port>` |
| `scaffold-route` | Expose via OpenShift router, HTTPS route | `python ./scripts/scaffold.py --type route --name <name> --data-class <class>` |
| `scaffold-statefulset` | Database, persistent workload | `python ./scripts/scaffold.py --type statefulset --name <name> --port <port>` |
| `scaffold-hpa` | Autoscaling, variable load | `python ./scripts/scaffold.py --type hpa --name <name>` |
| `scaffold-pdb` | Disruption budget, availability | `python ./scripts/scaffold.py --type pdb --name <name>` |
| `scaffold-ingress` | AVI/NDP ingress, external access | `python ./scripts/scaffold.py --type ingress --name <name>` |
| `scaffold-serviceaccount` | RBAC, pod identity | `python ./scripts/scaffold.py --type serviceaccount --name <name>` |
| `scaffold-pvc` | Persistent storage volume | `python ./scripts/scaffold.py --type pvc --name <name>` |
| `scaffold-job` | One-off batch job, migration | `python ./scripts/scaffold.py --type job --name <name>` |
| `scaffold-networkpolicy` | NetworkPolicy, Conftest deny, traffic control | `python ./scripts/scaffold.py --type networkpolicy --name <name>` |
| `scaffold-configmap` | Configuration, non-sensitive settings | `python ./scripts/scaffold.py --type configmap --name <name>` |
| `scaffold-cronjob` | Scheduled task, periodic job | `python ./scripts/scaffold.py --type cronjob --name <name>` |
| `scaffold-externalsecret` | Vault secret, ExternalSecret operator | `python ./scripts/scaffold.py --type externalsecret --name <name>` |
| `scaffold-docker-ci` | Docker CI pipeline, image build | `python ./scripts/scaffold.py --type docker-ci --image <image>` |
| `scaffold-sast-ci` | SAST, CodeQL, security scanning | `python ./scripts/scaffold.py --type sast-ci` |

## Init & Validation Skills

| Skill | Triggers on | Script |
|---|---|---|
| `init-emerald-repo` | Initialize repo, boilerplate, first-time setup | `scripts/init.py --project <name> --registry <registry>` |
| `validate-emerald-manifests` | Policy check failures, pre-deploy validation | `scripts/validate.py` (helm → datree → polaris → kube-linter → conftest) |
| `author-networkpolicy` | NetworkPolicy logic questions, guided authoring | scaffold.py + guidance |
| `setup-dotnet-ci` | Wiring up .NET 8 CI pipelines | guidance |

## Template substitution pattern

Templates use `@@VAR@@`-style markers. `scaffold.py` uses plain `str.replace()` — avoids conflict with Helm `{{ }}` Go template syntax. A post-render guard **hard-fails** if any `@@` marker remains unreplaced.

Template files: `assets/templates/*.tpl.yaml` / `*.tpl.yml` — named with `.tpl` before the real extension.

## Slash Commands

| Command | What it does |
|---|---|
| `/ag-init` | **Start here** — full repo initialization |
| `/ag-scaffold` | Scaffold Helm chart resources for a component |
| `/ag-validate` | Run all four policy checks + remediation |
| `/ag-networkpolicy` | Generate a compliant NetworkPolicy |
| `/ag-setup-ci` | Set up .NET 8 GitHub Actions CI |
| `/ag-deployment` | Scaffold Deployment only |
| `/ag-service` | Scaffold Service only |
| `/ag-route` | Scaffold Route only |
| `/ag-statefulset` | Scaffold StatefulSet only |
| `/ag-hpa` | Scaffold HPA only |
| `/ag-pdb` | Scaffold PodDisruptionBudget only |
| `/ag-ingress` | Scaffold Ingress only |
| `/ag-serviceaccount` | Scaffold ServiceAccount only |
| `/ag-pvc` | Scaffold PVC only |
| `/ag-job` | Scaffold Job only |
| `/ag-configmap` | Scaffold ConfigMap only |
| `/ag-cronjob` | Scaffold CronJob only |
| `/ag-externalsecret` | Scaffold ExternalSecret only |
| `/ag-docker-ci` | Add Docker CI workflow |
| `/ag-sast-ci` | Add SAST CI workflow |

## Agents

| Agent | Role |
|---|---|
| `init-emerald` | Asks questions → runs `init-emerald-repo` skill → bootstraps full repo |
| `scaffold-emerald-app` | Topology-aware orchestrator — calls scaffold skills per component, auto-generates NetworkPolicies |
| `manifest-validator` | Called by `/ag-validate` — runs `validate.py`, structures remediation output |

## Symlinks

Each skill's `scripts/scaffold.py` and `assets/templates/` entries are symlinks to the plugin root. This eliminates duplication while keeping skills self-contained. On marketplace install, symlinks become hard copies.

Restore all symlinks: `python .agents/skills/symlink-manager/scripts/symlink_manager.py restore --manifest plugins/ag-devops/symlinks.json`

## Policy files

All policy configs live in `cd/policies/` in this repo. Skills reference them via `assets/policies/` symlinks.

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