# Acceptance Criteria: scaffold-networkpolicy

## Functional Requirements

- Skill triggers on the correct prompts (see evals/evals.json)
- Script builds a Helm NetworkPolicy from topology flags
- Output passes all Conftest/OPA rules
- No allow-all shapes are possible regardless of inputs

## Output Requirements

- `<name>-networkpolicy.yaml` using `AllowIngressFrom`/`AllowEgressTo` intent inputs

## Non-Goals

- Does not generate raw NetworkPolicy rules
- Internet egress requires `--justification` and `--approved-by` flags
