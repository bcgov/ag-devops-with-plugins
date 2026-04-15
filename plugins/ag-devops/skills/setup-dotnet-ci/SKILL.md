---
name: setup-dotnet-ci
description: Use when wiring up GitHub Actions CI for a .NET 8 project using ag-devops shared templates, when adding build/test/lint/package workflows to an app repo, or when a CI pipeline is missing or broken for a BC Gov AG .NET service
allowed-tools:
  - Read
  - Bash
---

# Set Up .NET 8 CI with ag-devops Templates

## Overview

Wire up reusable GitHub Actions workflows from `ci/dotnetcore/` into an app repo. Two consumption models available — pick one.

## Pick Your Model

**Model A — Copy workflows (recommended for most teams)**

Copy relevant `ci/dotnetcore/*.yml` files into your app repo's `.github/workflows/`, then create a thin entry workflow that calls them.

- Easiest to debug
- No cross-repo permission issues
- Pipeline doesn't break if ag-devops changes
- Con: Must manually sync updates

**Model B — Composite actions (centralized updates)**

Reference composite actions directly from ag-devops, pinned to a release tag:

```yaml
- uses: bcgov-c/ag-devops/ci/dotnetcore/composite/dotnet-8-build@v1.2.3
  with:
    dotnet_build_path: ./MySolution.sln
```

- Con: Any breaking change in ag-devops requires coordination

## Model A: Minimum Entry Workflow

Create `.github/workflows/ci.yml` in your app repo:

```yaml
name: ci

on:
  pull_request:
  push:
    branches: [main]

jobs:
  restore:
    uses: ./.github/workflows/dotnet-8-dependencies.yml
    with:
      dotnet_build_path: ./MySolution.sln

  build:
    needs: restore
    uses: ./.github/workflows/dotnet-8-build.yml
    with:
      dotnet_build_path: ./MySolution.sln
      warn_as_error: true

  lint:
    needs: restore
    uses: ./.github/workflows/dotnet-8-lint.yml
    with:
      project_path: .

  test:
    needs: build
    uses: ./.github/workflows/dotnet-8-tests-msbuild.yml
    with:
      unit_test_folder: "tests/MyProject.Tests"
      coverage_threshold: 80
      coverage_threshold_type: "line,branch"
```

## Workflow Reference

| Workflow file | Purpose | Key inputs |
|---|---|---|
| `dotnet-8-dependencies.yml` | `dotnet restore` + vulnerability scan | `dotnet_build_path` |
| `dotnet-8-build.yml` | `dotnet build` Release | `dotnet_build_path`, `warn_as_error`, `version_prefix` |
| `dotnet-8-build-grpc.yml` | Same + installs `protoc` | Same as build |
| `dotnet-8-lint.yml` | `dotnet format --verify-no-changes` | `project_path`, `runner` |
| `dotnet-8-tests-msbuild.yml` | Unit tests + coverage threshold | `unit_test_folder` (space-separated), `coverage_threshold` |
| `dotnet-8-tests-msbuild-combined.yml` | Unit + integration tests with merged coverage | Adds `integration_test_folder` |
| `dotnet-8-tests-collector.yml` | Tests via XPlat collector | `unit_test_folder` |
| `dotnet-8-package.yml` | `dotnet publish` win-x64 | `dotnet_publish_subpath` (under `./src/`) |
| `dotnet-8-nuget-pack.yml` | `dotnet pack` → `.nupkg` | `version_prefix`, `version_suffix` |
| `dotnet-8-nuget-deploy.yml` | Push to NuGet feed | `nuget_feed`, secrets |
| `dotnet-8-ef.yml` | EF migrations script | `dotnet_ef_project`, `dotnet_ef_script` |

## Runner Requirements

- `ubuntu-latest` — all workflows except packaging
- `windows-latest` — `dotnet-8-package.yml` only (win-x64 publish)
- Self-hosted runners: must have `libxml2-utils` (`xmllint`) and `bc` installed

## Secrets Reference

| Secret | Used by | Purpose |
|---|---|---|
| `NUGET_AUTH_TOKEN` | `dotnet-8-dependencies.yml` | Read from private NuGet source |
| `NUGET_USERNAME` + `NUGET_PASSWORD` | `dotnet-8-nuget-deploy.yml` | Push to feed (basic auth) |
| `NUGET_API_KEY` | `dotnet-8-nuget-deploy.yml` | Push to feed (API key) |

## Common Mistakes

| Mistake | Fix |
|---|---|
| `unit_test_folder` path is wrong | Must be relative path to the test project folder, space-separated for multiple |
| Coverage fails on self-hosted runner | Install `libxml2-utils` and `bc`, or remove coverage threshold steps |
| `dotnet-8-package.yml` fails | Verify project is under `./src/<dotnet_publish_subpath>` |
| NuGet restore fails (`NU1301`) | Set `permissions: packages: read` and ensure `NUGET_AUTH_TOKEN` is passed |
