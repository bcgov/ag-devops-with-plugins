---
name: ag-hpa
description: "Generate a HorizontalPodAutoscaler Helm template for an Emerald component using the scaffold-hpa scripted skill. Prints the required values.yaml autoscaling snippet. Writes gitops/templates/<name>-hpa.yaml directly."
---
Use the `scaffold-hpa` skill to generate an HPA Helm template. Ask for the component name, min/max replicas, and CPU utilization target, then run the script to write the file and print the values snippet.
