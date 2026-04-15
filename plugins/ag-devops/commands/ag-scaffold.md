---
name: ag-scaffold
description: "Scaffold one or more Helm components for an Emerald deployment using scripted skills. The orchestrating agent asks about your topology (components, ports, data class, NetworkPolicy rules) then calls scaffold-deployment, scaffold-service, scaffold-route, and scaffold-networkpolicy scripts to write all files into gitops/templates/ directly."
---
Use the `scaffold-emerald-app` agent to scaffold all required Helm templates for this application.
