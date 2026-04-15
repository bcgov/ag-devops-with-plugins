# Acceptance Criteria: scaffold-deployment

## Functional Requirements

- Skill triggers on the correct prompts (see evals/evals.json)
- Script runs without error
- Output file is written to `gitops/templates/`
- All `@@VAR@@` markers are replaced with user-supplied values
- Output is valid Helm YAML

## Output Requirements

- `<name>-deployment.yaml` using the set+define+include pattern

## Non-Goals

- Does not create `values.yaml`
- Does not create a NetworkPolicy
