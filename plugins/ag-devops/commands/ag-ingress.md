---
name: ag-ingress
description: "Generate a Kubernetes Ingress Helm template for an Emerald component using the scaffold-ingress scripted skill. Note: OpenShift Route is preferred on Emerald — use /ag-route unless you need standard k8s Ingress. Writes gitops/templates/<name>-ingress.yaml directly."
---
Use the `scaffold-ingress` skill to generate an Ingress Helm template. Ask for the component name, hostname, service port, path, and AVI class, then run the script to write the file.
