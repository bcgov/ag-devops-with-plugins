# Acceptance Criteria: scaffold-service

## Functional Requirements

- Skill triggers on the correct prompts (see evals/evals.json)
- Script runs without error
- Output file is written to the target directory
- All `@@VAR@@` markers are replaced with user-supplied values
- Output is valid Helm YAML

## Output Requirements

- `<name>-service.yaml` using the set+define+include pattern

## Non-Goals

- Does not create a Route or Ingress
