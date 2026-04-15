---
name: ag-deployment
description: "Generate a Deployment Helm template for an OpenShift Emerald component using the scaffold-deployment scripted skill. Writes gitops/templates/<name>-deployment.yaml directly using the ag-helm-templates set+define+include pattern."
---
Use the `scaffold-deployment` skill to generate a Deployment Helm template. Ask for the component name, port (default 8080), and data class (low/medium/high), then run the script to write the file.
