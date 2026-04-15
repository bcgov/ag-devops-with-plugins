---
name: scaffold-sast-ci
description: Use when adding SonarQube SAST and Gitleaks secrets scanning CI to an application repo using the ag-devops sast shared composite action. Generates .github/workflows/sast.yml. Writes directly to the target workflow directory.
allowed-tools:
  - Bash
  - Read
  - Write
command: python plugins/ag-devops/skills/scaffold-sast-ci/scripts/generate.py --project-key "$PROJECT_KEY" --sonar-host "$SONAR_HOST" --output-dir "$OUTPUT_DIR"
---

# Scaffold SAST CI

Generate a `.github/workflows/sast.yml` workflow that runs SonarQube SAST analysis
and Gitleaks secrets scanning using the `bcgov-c/ag-devops` shared composite action.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--project-key` | ✅ | — | SonarQube project key |
| `--sonar-host` | | `https://ag-sonarqube-e7c7c2-prod.apps.gold.devops.gov.bc.ca/` | SonarQube host URL |
| `--sources` | | `.` | Source directory for analysis |
| `--coverage-report` | | `TestResults/coverage/coverage.cobertura.xml` | Coverage report path |
| `--output-dir` | | `.github/workflows` | Destination directory |

## Output

`.github/workflows/sast.yml`

## Notes

- Requires `SONAR_TOKEN`, `GITHUB_TOKEN`, and `GITLEAKS_LICENSE` secrets.
- Runs on push to main and on all pull requests.
