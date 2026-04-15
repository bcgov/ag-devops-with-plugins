---
name: ag-statefulset
description: "Generate a StatefulSet Helm template for an OpenShift Emerald stateful component using the scaffold-statefulset scripted skill. For databases, message queues, or other ordered stateful workloads. Writes gitops/templates/<name>-statefulset.yaml directly."
---
Use the `scaffold-statefulset` skill to generate a StatefulSet Helm template. Ask for the component name, port, data class, and headless service name, then run the script to write the file.
