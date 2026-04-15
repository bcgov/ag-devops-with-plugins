# Acceptance Criteria: scaffold-route

## Functional Requirements

- Skill triggers on the correct prompts (see evals/evals.json)
- Script runs without error
- Output file is written to the target directory
- AVI annotation snippet is printed to stdout
- All `@@VAR@@` markers are replaced with user-supplied values

## Output Requirements

- `<name>-route.yaml` with required AVI annotation in the values snippet

## Non-Goals

- Does not create an Ingress
- Does not set TLS termination without an explicit flag
