# Acceptance Criteria: init-emerald-repo

## Functional Requirements

- Skill triggers on the correct prompts (see evals/evals.json)
- Script generates all 10 output files in a single invocation
- Idempotent when run with the `--overwrite` flag
- All `@@VAR@@` markers are replaced with user-supplied values
- Generated YAML and workflow syntax is valid

## Output Requirements

- `.github/workflows/ci.yml`, `.github/workflows/cd.yml`, `gitops/Chart.yaml`, `gitops/values.yaml`, `gitops/values-dev.yaml`, `gitops/values-test.yaml`, `gitops/values-prod.yaml`, `Makefile`, `.gitignore` additions, `CODEOWNERS`

## Non-Goals

- Does not push to git
- Does not create GitHub secrets
