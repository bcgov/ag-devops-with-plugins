---
description: "Validate a rendered Helm chart against all four Emerald policy tools (Datree, Polaris, kube-linter, Conftest/OPA). Reports pass/fail per tool with specific remediation steps for every failure."
---

Use the `validate-emerald-manifests` skill to run all four required policy checks against the current chart.

If a rendered.yaml does not already exist in the current directory, render it first:

```bash
helm template my-release ./my-chart --values ./values.yaml > rendered.yaml
```

Then run all four policy tools and return a structured summary:
- Pass/fail status for each tool
- Specific resource and rule for each failure
- Exact YAML or values.yaml fix for each issue

If all checks pass, confirm the chart is ready to deploy.
