---
name: manage-marketplace
description: Use when publishing or updating the ag-devops plugin to the Claude Code marketplace, registering the marketplace with a team, configuring auto-install via settings.json, or troubleshooting plugin load failures
---

# Manage the ag-devops Marketplace

## Overview

The ag-devops plugin is distributed via a GitHub-hosted Claude Code marketplace. The marketplace catalog lives at the **repo root** in `.claude-plugin/marketplace.json`. The plugin itself lives in `plugins/ag-devops/`.

## File Layout

```
ag-devops/                          ← repo root
  .claude-plugin/
    marketplace.json                ← ROOT-LEVEL catalog (GitHub distribution)
  plugins/
    ag-devops/
      .claude-plugin/
        plugin.json                 ← plugin metadata + component bindings
        marketplace.json            ← (internal — plugin-level only)
      skills/ agents/ commands/
```

> The root `.claude-plugin/marketplace.json` is what Claude Code fetches. The plugin-level `plugin.json` is what it reads after downloading the plugin. Both must exist.

## Consumer: Register and Install

```bash
# 1. Register the marketplace (one-time per machine/project)
/plugin marketplace add bcgov-c/ag-devops

# 2. Install the plugin
/plugin install ag-devops

# 3. Activate without restarting
/reload-plugins
```

Expected output from `/reload-plugins`:
```
Reloaded: 1 plugins · 5 skills · 3 agents · 0 hooks · 0 plugin MCP servers
```

## Team Auto-Install (`.claude/settings.json`)

To auto-enable the plugin for all team members in this repo:

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

Commit this to the app repo. Every team member gets the plugin automatically on next Claude Code start.

## Releasing a New Version

This repo uses Semantic Release (`.releaserc.json`). A new plugin version is published by:

1. Merging changes to `main` using conventional commits
2. Semantic Release creates a GitHub tag (`v1.x.x`)
3. Update `plugins/ag-devops/.claude-plugin/plugin.json` → `version` field to match

Consumers pin to a version via `ref` in their marketplace registration:
```json
{ "source": { "source": "github", "repo": "bcgov-c/ag-devops", "ref": "v1.2.0" } }
```

## Validation Before Publishing

```bash
# Validate plugin structure (requires Claude Code CLI)
claude plugin validate ./plugins/ag-devops

# Common errors and fixes
```

| Error | Fix |
|---|---|
| `File not found: .claude-plugin/marketplace.json` | Root `.claude-plugin/marketplace.json` is missing — create it |
| `strict: true` + no `plugin.json` in plugin dir | Add `plugins/ag-devops/.claude-plugin/plugin.json` |
| `YAML frontmatter failed to parse` | Fix YAML syntax in the failing skill/agent/command file |
| Plugin silently fails to load | Check `/plugin` → Errors tab for the specific failure |
| Skill not found after install | Verify skill directory name matches entry in `plugin.json` `skills` list |

## Scope Options at Install Time

```bash
/plugin install ag-devops                        # user scope — all your repos
/plugin install ag-devops --scope project        # project scope — shared with collaborators
/plugin install ag-devops --scope local          # local scope — this machine only
```

## Component Binding (plugin.json)

Every skill, agent, and command must be listed in `plugins/ag-devops/.claude-plugin/plugin.json`. Missing entries cause silent load failures.

Current bindings:
- **Skills:** `scaffold-openshift-deployment`, `validate-emerald-manifests`, `author-networkpolicy`, `setup-dotnet-ci`, `manage-marketplace`
- **Agents:** `initialize-emerald-repo`, `manifest-validator`, `helm-scaffolder`
- **Commands:** `ag-init`, `ag-scaffold`, `ag-validate`, `ag-networkpolicy`, `ag-setup-ci`

When adding a new component, update `plugin.json` immediately — do not wait.

## SkillsMP.com Indexing

Skills in this plugin are eligible for indexing at [skillsmp.com](https://skillsmp.com).

Requirements:
1. Public GitHub repo
2. `SKILL.md` files with `name` + `description` frontmatter
3. GitHub topic tags: `claude-skills` and `claude-code-skill` on the repo

Skills nested at `plugins/<plugin>/skills/<skill>/SKILL.md` (4 levels deep) may not be auto-crawled. If not indexed, mirror the skill folders under a top-level `skills/` directory.
