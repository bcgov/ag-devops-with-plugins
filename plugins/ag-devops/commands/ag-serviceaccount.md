---
name: ag-serviceaccount
description: "Generate a ServiceAccount Helm template for an Emerald component using the scaffold-serviceaccount scripted skill. Required for RBAC, image pull credentials, or pod identity. Writes gitops/templates/<name>-serviceaccount.yaml directly."
---
Use the `scaffold-serviceaccount` skill to generate a ServiceAccount Helm template. Ask for the component name and whether to automount the token, then run the script to write the file and print the values snippet.
