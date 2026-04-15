---
name: ag-networkpolicy
description: "Generate a compliant NetworkPolicy Helm template for an Emerald workload using the scaffold-networkpolicy scripted skill. Accepts topology flags (--ingress-from-router, --egress-to-apps, etc.) and writes gitops/templates/<name>-networkpolicy.yaml directly. For guidance on manual authoring, ask about the author-networkpolicy skill."
---
Use the `scaffold-networkpolicy` skill to generate a compliant NetworkPolicy for the specified workload. Ask for the component name and topology requirements (ingress sources, egress targets), then run the script to write the file.
