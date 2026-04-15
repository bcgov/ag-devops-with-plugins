# ag-devops — Claude Code Plugin

A Claude Code plugin for BC Government AG application teams deploying to OpenShift Emerald.

## What it does

Converts the ag-devops shared library (CI templates, Helm library chart, policy configs) into interactive Claude Code skills, agents, and commands that guide developers through:

- Scaffolding a new compliant Helm chart from scratch
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
    plugin.json          # Plugin metadata
    marketplace.json     # Marketplace registration
  skills/
    scaffold-openshift-deployment/SKILL.md
    validate-emerald-manifests/SKILL.md
    author-networkpolicy/SKILL.md
    setup-dotnet-ci/SKILL.md
  agents/
    initialize-emerald-repo.md   # Full repo init — .github + gitops + Makefile
    manifest-validator.md
    helm-scaffolder.md
  commands/
    ag-init.md             # /ag-init — full repo initialization
    ag-scaffold.md
    ag-validate.md
    ag-networkpolicy.md
    ag-setup-ci.md
  CLAUDE.md
  package.json
```

## Source library

This plugin wraps the ag-devops shared library. See:
- `docs/CI.md` — CI reference
- `docs/CD.md` — Helm library + policy reference
- `docs/DEVELOPERS-GUIDE.md` — deny-by-default cluster walkthrough
