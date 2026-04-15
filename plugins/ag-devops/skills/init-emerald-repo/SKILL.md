---
name: init-emerald-repo
description: Use when initializing a new application repository for OpenShift Emerald deployment. Generates the complete .github/workflows CI and CD pipelines, gitops Helm chart structure, per-environment values files, Makefile, .gitignore, and CODEOWNERS in a single command.
allowed-tools:
  - Bash
  - Read
  - Write
command: python plugins/ag-devops/skills/init-emerald-repo/scripts/init.py --project "$PROJECT" --registry "$REGISTRY" --team "$TEAM" --team-handle "$TEAM_HANDLE" --namespace-dev "$NAMESPACE_DEV" --namespace-test "$NAMESPACE_TEST" --namespace-prod "$NAMESPACE_PROD" --solution-path "$SOLUTION_PATH" --test-folders "$TEST_FOLDERS" --main-component "$MAIN_COMPONENT" --target-dir "$TARGET_DIR"
---

# Initialize Emerald Repository

Scaffold the complete foundation for an OpenShift Emerald application in one command.
All output files are written directly to the target directory — no copy-paste required.

## What gets generated

| File | Description |
|---|---|
| `.github/workflows/ci.yml` | .NET 8 CI pipeline (restore → build → lint → test) |
| `.github/workflows/cd.yml` | Deploy pipeline with 4-policy gate → oc login → helm upgrade |
| `.github/CODEOWNERS` | Require team review on `.github/` and `gitops/` |
| `gitops/Chart.yaml` | ag-helm-templates OCI dependency declaration |
| `gitops/values.yaml` | Base values with component stubs |
| `gitops/values-dev.yaml` | Dev environment overrides |
| `gitops/values-test.yaml` | Test environment overrides |
| `gitops/values-prod.yaml` | Production environment overrides |
| `Makefile` | `make render`, `make validate`, `make deploy` shortcuts |
| `.gitignore` | Helm chart lock and rendered.yaml entries appended |

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--project` | ✅ | — | Short project name, e.g. `my-app` |
| `--registry` | ✅ | — | Container image registry, e.g. `ghcr.io/bcgov-c` |
| `--team` | | `<team-name>` | Team name for `owner` label |
| `--team-handle` | | `<team-handle>` | GitHub team handle for CODEOWNERS |
| `--namespace-dev` | | `<project>-dev` | OpenShift namespace for dev |
| `--namespace-test` | | `<project>-test` | OpenShift namespace for test |
| `--namespace-prod` | | `<project>-prod` | OpenShift namespace for prod |
| `--solution-path` | | `./MySolution.sln` | .NET solution file path |
| `--test-folders` | | `tests/MyApp.Tests` | Space-separated test project folder(s) |
| `--main-component` | | `web-api` | Primary workload name for CD rollout verification |
| `--target-dir` | | `.` | Root directory of the target repo |
| `--overwrite` | | false | Overwrite existing files |

## Usage

```bash
python plugins/ag-devops/skills/init-emerald-repo/scripts/init.py \
  --project my-app \
  --registry ghcr.io/bcgov-c \
  --team my-team \
  --team-handle my-team-github \
  --namespace-dev my-app-dev \
  --namespace-test my-app-test \
  --namespace-prod my-app-prod \
  --solution-path ./MySolution.sln \
  --test-folders "tests/MyApp.Tests" \
  --main-component web-api \
  --target-dir .
```

## Examples

**Agent call — full initialization for `stanley-api`:**
```
python plugins/ag-devops/skills/init-emerald-repo/scripts/init.py \
  --project stanley-api \
  --registry ghcr.io/bcgov-c \
  --team stanley-team \
  --team-handle stanley-devs \
  --namespace-dev stanley-api-dev \
  --namespace-test stanley-api-test \
  --namespace-prod stanley-api-prod \
  --solution-path ./StanleyApi.sln \
  --test-folders "tests/StanleyApi.Tests" \
  --main-component web-api \
  --target-dir .
```

## After Initialization

1. **Copy shared workflow files** from `ag-devops/ci/dotnetcore/` into `.github/workflows/`:
   - `dotnet-8-dependencies.yml`
   - `dotnet-8-build.yml`
   - `dotnet-8-lint.yml`
   - `dotnet-8-tests-msbuild.yml`

2. **Scaffold components** using the scripted skills:
   ```bash
   # For each component, run scaffold-deployment + scaffold-service + scaffold-networkpolicy
   # If externally exposed: also run scaffold-route
   ```

3. **Set GitHub secrets** (Settings → Secrets → Actions):
   - `OPENSHIFT_SERVER` — `https://api.emerald.devops.gov.bc.ca:6443`
   - `OPENSHIFT_TOKEN` — service account token with deploy permissions

4. **Create GitHub Environments**: `dev`, `test`, `prod`

5. Validate: `helm dependency update ./gitops && helm lint ./gitops`
