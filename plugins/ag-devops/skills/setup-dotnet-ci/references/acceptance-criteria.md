# Acceptance Criteria: setup-dotnet-ci

## Functional Requirements

- Skill triggers on the correct prompts (see evals/evals.json)
- Guides user to set up `.github/workflows` using `dotnet-8-*` shared workflows from `bcgov-c/ag-devops`
- Covers both consumption models (direct call and wrapper workflow)

## Output Requirements

- Correct workflow YAML with proper `uses:` references to shared workflows

## Non-Goals

- Does not write files
- Does not handle non-.NET CI
