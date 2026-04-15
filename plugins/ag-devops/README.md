# ag-devops — Claude Code Plugin v2.0

A Claude Code plugin for BC Government AG application teams deploying to OpenShift Emerald.

## What it does

Converts the ag-devops shared library (CI templates, Helm library chart, policy configs) into interactive Claude Code skills, agents, and commands that guide developers through:

- Scaffolding a new compliant Helm chart from scratch (16 resource types)
- Validating manifests against all four policy tools (Datree, Polaris, kube-linter, Conftest)
- Authoring NetworkPolicies that pass Rego hard-deny rules
- Wiring up .NET 8 CI pipelines

## Quick Start

```bash
# Install
claude plugin install ag-devops   # from marketplace
# or
claude plugin install ./plugins/ag-devops   # from this repo
```

**New project? Start here:**
```
/ag-init
```
Answers 10 questions, then generates every file your repo needs — `.github/workflows/`, `gitops/` Helm chart, values per environment, NetworkPolicies, Makefile, and a GitHub secrets checklist. Commit and push; CI and CD run automatically.

**Other commands:**
```
/ag-validate       # Policy check + remediation on existing chart
/ag-networkpolicy  # Author a compliant NetworkPolicy
/ag-scaffold       # Helm chart only (no CI/CD)
/ag-setup-ci       # .NET 8 CI only
```

## Contents

```
plugins/ag-devops/
  .claude-plugin/
    plugin.json          # Plugin metadata (v2.0.0 — 20 skills, 3 agents, 21 commands)
    marketplace.json     # Marketplace registration
  scripts/
    scaffold.py          # UNIFIED scaffold CLI — all 16 resource types via --type
    validate.py          # 4-tool validation pipeline runner
  assets/templates/      # 25 canonical .tpl.yaml/.tpl.yml templates (physical files)
  skills/
    scaffold-deployment/     scaffold-service/      scaffold-route/
    scaffold-statefulset/    scaffold-hpa/          scaffold-pdb/
    scaffold-ingress/        scaffold-pvc/          scaffold-job/
    scaffold-serviceaccount/ scaffold-networkpolicy/ scaffold-configmap/
    scaffold-cronjob/        scaffold-externalsecret/ scaffold-docker-ci/
    scaffold-sast-ci/        init-emerald-repo/     validate-emerald-manifests/
    author-networkpolicy/    setup-dotnet-ci/
  agents/
    init-emerald.md          # Full repo init — .github + gitops + Makefile
    scaffold-emerald-app.md  # Topology-aware orchestrator
    manifest-validator.md    # Policy validation orchestrator
  commands/
    ag-init.md ag-scaffold.md ag-validate.md ag-networkpolicy.md ag-setup-ci.md
    ag-deployment.md ag-service.md ag-route.md ag-statefulset.md ag-hpa.md
    ag-pdb.md ag-ingress.md ag-serviceaccount.md ag-pvc.md ag-job.md
    ag-docker-ci.md ag-sast-ci.md ag-configmap.md ag-cronjob.md ag-externalsecret.md
  symlinks.json            # 104 registered symlinks (scaffold.py + templates per skill)
  AGENTS.md                # AI agent entry point
  CLAUDE.md                # AI behavioural rules
```

## v2.0 Architecture: Unified scaffold.py

All 16 resource types go through one script at the plugin root:

```bash
python ./scripts/scaffold.py --type deployment --name web-api --port 8080
python ./scripts/scaffold.py --type networkpolicy --name web-api --port 8080 --ingress-from-router
python ./scripts/scaffold.py --type configmap --name my-config
python ./scripts/scaffold.py --help   # full options list
```

Each skill's `scripts/scaffold.py` is a **symlink** to `plugins/ag-devops/scripts/scaffold.py`.
After marketplace install, symlinks become hard copies — no broken paths in installed plugins.

## Source library

This plugin wraps the ag-devops shared library. See:
- `docs/CI.md` — CI reference
- `docs/CD.md` — Helm library + policy reference
- `docs/DEVELOPERS-GUIDE.md` — deny-by-default cluster walkthrough
