# AGENTS.md — ag-devops Plugin

> **AI agents:** This file is the entry point for understanding the `ag-devops` plugin structure. Read this before attempting to use any skill, agent, or command.

## What this plugin does

The `ag-devops` plugin provides scripted, policy-compliant tooling for BC Government application teams deploying to the **OpenShift Emerald** cluster. It generates Helm chart fragments, CI/CD workflows, and validates Kubernetes manifests against BC Gov policy.

## Plugin structure

```
plugins/ag-devops/
├── AGENTS.md                    ← you are here
├── README.md                    ← installation + quickstart for humans
├── plugin.json                  ← skill/agent/command manifest
├── CLAUDE.md                    ← AI agent behavioural rules
├── symlinks.json                ← all registered symlinks (restore with symlink_manager.py)
├── assets/
│   ├── templates/               ← CANONICAL Jinja2 templates (all .yaml.j2, .yml.j2)
│   └── policies/                ← symlinks → cd/policies/ (datree, polaris, OPA, kube-linter)
├── references/                  ← symlinks → docs/ and ag-helm/docs/
├── skills/                      ← 18 scripted skills (see Skills below)
├── agents/                      ← 5 orchestration agents (see Agents below)
└── commands/                    ← 17 slash commands (see Commands below)
```

## How templates and symlinks work

- **Physical files** live at `plugins/ag-devops/assets/templates/*.yaml.j2`
- Each skill's `assets/templates/` contains **file-level symlinks** → plugin root
- Each skill's `references/` contains **file-level symlinks** → plugin root references
- On `skills update` / marketplace install, the bootstrap installer resolves all symlinks to real copies so the installed skill in `.agents/` is fully self-contained

## Skills

All skills are scripted — they invoke `python scripts/generate.py` (or `scripts/init.py`) and write output directly to the user's workspace. No copy-paste required.

### Helm Chart Fragment Generators

| Skill | Command | Template |
|---|---|---|
| `scaffold-deployment` | `/ag-deployment` | `deployment.yaml.j2` |
| `scaffold-service` | `/ag-service` | `service.yaml.j2` |
| `scaffold-route` | `/ag-route` | `route.yaml.j2` |
| `scaffold-statefulset` | `/ag-statefulset` | `statefulset.yaml.j2` |
| `scaffold-hpa` | `/ag-hpa` | `hpa.yaml.j2` |
| `scaffold-pdb` | `/ag-pdb` | `pdb.yaml.j2` |
| `scaffold-ingress` | `/ag-ingress` | `ingress.yaml.j2` |
| `scaffold-serviceaccount` | `/ag-serviceaccount` | `serviceaccount.yaml.j2` |
| `scaffold-pvc` | `/ag-pvc` | `pvc.yaml.j2` |
| `scaffold-job` | `/ag-job` | `job.yaml.j2` |
| `scaffold-networkpolicy` | `/ag-networkpolicy` | (programmatic) |
| `scaffold-openshift-deployment` | — | Deployment + SCC-safe |

### CI/CD Generators

| Skill | Command | Template |
|---|---|---|
| `init-emerald-repo` | `/ag-init` | 8 templates (Chart, workflows, values, Makefile…) |
| `scaffold-docker-ci` | `/ag-docker-ci` | `docker.yml.j2` |
| `scaffold-sast-ci` | `/ag-sast-ci` | `sast.yml.j2` |
| `setup-dotnet-ci` | `/ag-setup-ci` | Configures .NET 8 CI |

### Validation & Authoring

| Skill | Command | Description |
|---|---|---|
| `validate-emerald-manifests` | `/ag-validate` | Runs datree, polaris, kube-linter, conftest |
| `author-networkpolicy` | `/ag-networkpolicy` | Guided NetworkPolicy authoring |

## Agents

Agents orchestrate skills end-to-end. Use agents for multi-step workflows.

| Agent file | Invoke | Role |
|---|---|---|
| `agents/init-emerald.md` | `/ag-init` | Full repo bootstrap — calls `init-emerald-repo` skill |
| `agents/scaffold-emerald-app.md` | `/ag-scaffold` | Gathers app requirements, calls scaffold-* skills |
| `agents/helm-scaffolder.md` | `/ag-scaffold` | Helm chart fragment authoring orchestrator |
| `agents/manifest-validator.md` | `/ag-validate` | Policy validation orchestrator |
| `agents/initialize-emerald-repo.md` | legacy | Replaced by `init-emerald.md` |

## Commands

All commands are in `commands/*.md`. Key workflows:

```
/ag-init           → bootstrap entire repo (CI workflows + gitops chart + Makefile)
/ag-scaffold       → interactively scaffold all app components
/ag-validate       → validate rendered manifests against BC Gov policy
/ag-networkpolicy  → generate or audit NetworkPolicy for a component
/ag-deployment     → scaffold a Deployment Helm fragment
/ag-service        → scaffold a Service Helm fragment
/ag-route          → scaffold an OpenShift Route Helm fragment
/ag-statefulset    → scaffold a StatefulSet Helm fragment
/ag-hpa            → scaffold an HPA Helm fragment
/ag-pdb            → scaffold a PodDisruptionBudget Helm fragment
/ag-ingress        → scaffold an Ingress Helm fragment (AVI annotation included)
/ag-serviceaccount → scaffold a ServiceAccount Helm fragment
/ag-pvc            → scaffold a PersistentVolumeClaim Helm fragment
/ag-job            → scaffold a Job Helm fragment
/ag-docker-ci      → add Docker build/push GitHub Actions workflow
/ag-sast-ci        → add SAST GitHub Actions workflow
/ag-setup-ci       → configure .NET 8 CI pipeline
```

## How skills call scripts

Each skill's `SKILL.md` has a `command` field showing the exact Python invocation:

```
python skills/scaffold-deployment/scripts/generate.py \
  --name $NAME --port $PORT --data-class $DATA_CLASS --output-dir gitops/templates/
```

The agent resolves `$NAME`, `$PORT`, `$DATA_CLASS` from the conversation context and writes output to the user's workspace.

## Key policy constraints (enforced by validate-emerald-manifests)

- All workloads **must** have `data-class: low|medium|high` label
- All Deployments **must** have a matching NetworkPolicy
- Routes **must** use `edge` TLS termination with OPA approval annotation
- No `ingress: [{}]` or `egress: [{}]` (allow-all) in any NetworkPolicy
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

When `/ag-init` runs, the `init-emerald-repo` skill writes an `AGENTS.md` to the **project root** of the user's repo. That file describes the gitops structure so agents working in that repo understand the layout. It is maintained by the plugin, not the user.
