---
description: "Initialize a new application repository for OpenShift Emerald deployment end-to-end. Asks topology questions then generates .github/workflows (CI + CD), gitops Helm chart, values files per environment, NetworkPolicies, Makefile, CODEOWNERS, and a GitHub secrets checklist. The first push just works."
---

Use the `initialize-emerald-repo` agent to fully initialize this repository for OpenShift Emerald deployment.

The agent will ask a short series of questions about your application topology, then generate every file needed so that:

- CI (build / test / lint) runs automatically on every PR
- CD (policy checks + Helm deploy) runs automatically on merge to main
- All four Emerald policy tools (Datree, Polaris, kube-linter, Conftest) pass before any deploy is attempted

When the agent finishes, it will output a GitHub secrets checklist and first-push instructions. Set the secrets, commit the generated files, and push — everything else is automated.
