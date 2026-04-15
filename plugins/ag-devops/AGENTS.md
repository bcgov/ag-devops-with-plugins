# AGENTS.md — ag-devops Plugin v2.0

> **AI agents:** This file is the entry point for understanding the `ag-devops` plugin structure. Read this before attempting to use any skill, agent, or command.

## What this plugin does

The `ag-devops` plugin provides scripted, policy-compliant tooling for BC Government application teams deploying to the **OpenShift Emerald** cluster. It generates Helm chart fragments, CI/CD workflows, and validates Kubernetes manifests against BC Gov policy.

## Plugin structure

```
plugins/ag-devops/
├── AGENTS.md                    ← you are here
├── README.md                    ← installation + quickstart for humans
├── .claude-plugin/
│   ├── plugin.json              ← manifest (v2.0.0 — 20 skills, 3 agents, 21 commands)
│   └── marketplace.json         ← marketplace registration
├── scripts/
│   ├── scaffold.py              ← UNIFIED scaffold CLI (16 resource types via --type)
│   └── validate.py              ← 4-tool validation pipeline runner
├── assets/
│   ├── templates/               ← 25 canonical .tpl.yaml / .tpl.yml templates (physical)
│   └── policies/                ← symlinks → cd/policies/ (datree, polaris, OPA, kube-linter)
├── references/                  ← symlinks → docs/ and ag-helm/docs/
├── skills/                      ← 20 scripted skills (see Skills below)
├── agents/                      ← 3 orchestration agents (see Agents below)
├── commands/                    ← 21 slash commands (see Commands below)
└── symlinks.json                ← 104 registered symlinks (restore with symlink_manager.py)
```

## How templates and symlinks work

**Physical files** live at the plugin root:
- `scripts/scaffold.py` — the single scaffold CLI for all 16 resource types
- `scripts/validate.py` — the validation pipeline runner
- `assets/templates/*.tpl.yaml` / `*.tpl.yml` — all 25 templates

Each skill's `scripts/scaffold.py` and `assets/templates/` contain **file-level symlinks** → plugin root (ADR-003). On marketplace install, symlinks become hard copies — fully self-contained.

To restore symlinks after `git reset --hard`:
```bash
python .agents/skills/symlink-manager/scripts/symlink_manager.py restore --manifest plugins/ag-devops/symlinks.json
```

## How scaffold.py works

All resource generation goes through a single script:

```bash
python ./scripts/scaffold.py --type deployment --name web-api --port 8080
python ./scripts/scaffold.py --type networkpolicy --name web-api --ingress-from-router
python ./scripts/scaffold.py --type configmap --name app-config
python ./scripts/scaffold.py --dry-run --type pvc --name pg-data  # preview only
python ./scripts/scaffold.py --help  # full options
```

Safety features: post-render `@@` guard, path traversal guard, `--dry-run`, `--force`, Kubernetes name validation, traceability header in every output file.

## Skills

### Helm Chart Fragment Generators

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

All output goes to `gitops/templates/` by default.

### CI/CD Generators

| Skill | Command | Description |
|---|---|---|
| `scaffold-docker-ci` | `/ag-docker-ci` | Docker build + push GitHub Actions workflow |
| `scaffold-sast-ci` | `/ag-sast-ci` | SAST/CodeQL GitHub Actions workflow |
| `init-emerald-repo` | `/ag-init` | Full repo boilerplate (uses `scripts/init.py`) |

### Validation & Authoring

| Skill | Command | Description |
|---|---|---|
| `validate-emerald-manifests` | `/ag-validate` | Runs `validate.py` → helm template → datree → polaris → kube-linter → conftest |
| `author-networkpolicy` | `/ag-networkpolicy` | Guided NetworkPolicy authoring via scaffold.py |
| `setup-dotnet-ci` | `/ag-setup-ci` | .NET 8 CI pipeline guidance |

## Agents

Agents orchestrate skills end-to-end. Use agents for multi-step workflows.

| Agent file | Invoke | Role |
|---|---|---|
| `agents/init-emerald.md` | `/ag-init` | Full repo bootstrap — calls `init-emerald-repo` skill |
| `agents/scaffold-emerald-app.md` | `/ag-scaffold` | Gathers app topology, calls scaffold-* skills for each component |
| `agents/manifest-validator.md` | `/ag-validate` | Policy validation orchestrator |

## Commands

All commands are in `commands/*.md`. Key workflows:

```
/ag-init           → bootstrap entire repo (CI workflows + gitops chart + Makefile)
/ag-scaffold       → interactively scaffold all app components
/ag-validate       → validate rendered manifests against BC Gov policy
/ag-networkpolicy  → generate or audit NetworkPolicy for a component

/ag-deployment     → scaffold Deployment Helm fragment
/ag-service        → scaffold Service Helm fragment
/ag-route          → scaffold OpenShift Route Helm fragment
/ag-statefulset    → scaffold StatefulSet Helm fragment
/ag-hpa            → scaffold HPA Helm fragment
/ag-pdb            → scaffold PodDisruptionBudget Helm fragment
/ag-ingress        → scaffold Ingress Helm fragment (AVI annotation included)
/ag-serviceaccount → scaffold ServiceAccount Helm fragment
/ag-pvc            → scaffold PersistentVolumeClaim Helm fragment
/ag-job            → scaffold Job Helm fragment
/ag-configmap      → scaffold ConfigMap Helm fragment
/ag-cronjob        → scaffold CronJob Helm fragment
/ag-externalsecret → scaffold ExternalSecret manifest (Vault integration)
/ag-docker-ci      → add Docker build/push GitHub Actions workflow
/ag-sast-ci        → add SAST GitHub Actions workflow
/ag-setup-ci       → configure .NET 8 CI pipeline
```

## How skills call scripts

Each skill's `SKILL.md` has a `command:` field showing the exact Python invocation:

```yaml
command: python ./scripts/scaffold.py --type deployment --name "$NAME" --port "$PORT" \
         --data-class "$DATA_CLASS" --output-dir "$OUTPUT_DIR"
```

The `./scripts/scaffold.py` path resolves against the skill directory — whether in the source repo or after marketplace install.

## Key policy constraints (enforced by validate-emerald-manifests)

- All workloads **must** have `data-class: low|medium|high` label
- All Deployments **must** have a matching NetworkPolicy
- Routes **must** use `edge` TLS termination with OPA approval annotation
- No `ingress: [{}]` or `egress: [{}]` (allow-all) in any NetworkPolicy
- Ingress peers using `podSelector` without `namespaceSelector` are denied (cross-namespace risk)
- Internet egress requires `justification` + `approvedBy` annotations
- AVI infrasetting annotation required on all Route/Ingress resources

## References

- `references/CI.md` — CI workflow reference
- `references/CD.md` — CD Helm + policy reference
- `references/CI-CD-START-HERE.md` — Getting started index
- `references/SIMPLE-API.md` — Helm library API contract
- `references/EXAMPLES.md` — Helm library copy-paste examples
- `references/DEVELOPERS-GUIDE.md` — Full developer guide
- `references/overview.md` — Repo architecture overview
- `assets/policies/` — Policy configs: datree, polaris, kube-linter, conftest/OPA

## AGENTS.md in user repos

When `/ag-init` runs, the `init-emerald-repo` skill writes an `AGENTS.md` to the **project root** of the user's repo. That file describes the gitops structure so agents working in that repo understand the layout without reading every file.