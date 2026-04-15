# Acceptance Criteria: author-networkpolicy

## Functional Requirements

- Skill triggers on the correct prompts (see evals/evals.json)
- Produces valid `ag-template.networkpolicy` using `AllowIngressFrom`/`AllowEgressTo` intent inputs
- Never produces allow-all rules (`ingress: - {}` or `egress: - {}`)

## Output Requirements

- Helm template snippet following the set+define+include pattern

## Non-Goals

- Does not write files
- Does not handle internet egress without explicit justification
