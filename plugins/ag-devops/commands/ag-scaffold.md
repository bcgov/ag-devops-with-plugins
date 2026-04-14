---
description: "Scaffold a new Helm chart for OpenShift Emerald deployment using ag-helm-templates. Guides through topology questions and generates Chart.yaml, values.yaml, and policy-compliant templates."
---

Use the `scaffold-openshift-deployment` skill to scaffold a complete, policy-compliant Helm chart for OpenShift Emerald.

Start by asking the developer:
1. App name and target namespace
2. Which components (frontend, web-api, worker, database)
3. Which components need an external Route
4. Data class (low / medium / high)
5. Image registry path

Then generate all chart files and confirm they are ready for `helm lint` and policy validation.

When scaffolding is complete, remind the developer to run `validate-emerald-manifests` (or `/ag-validate`) to confirm all four policy checks pass before committing.
