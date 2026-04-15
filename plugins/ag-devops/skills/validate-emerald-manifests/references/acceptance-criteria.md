# Acceptance Criteria: validate-emerald-manifests

## Functional Requirements

- Skill triggers on the correct prompts (see evals/evals.json)
- Renders Helm chart to YAML before running any policy tool
- Runs datree, polaris, kube-linter, and conftest in sequence
- Interprets each failure and provides actionable remediation

## Output Requirements

- Structured list of failures with specific remediation steps per tool

## Non-Goals

- Does not fix the chart
- Does not skip any policy tool
