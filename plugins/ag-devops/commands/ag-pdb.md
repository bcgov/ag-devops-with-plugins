---
name: ag-pdb
description: "Generate a PodDisruptionBudget Helm template for an Emerald component using the scaffold-pdb scripted skill. Ensures availability during node maintenance. Writes gitops/templates/<name>-pdb.yaml directly."
---
Use the `scaffold-pdb` skill to generate a PDB Helm template. Ask for the component name and maxUnavailable or minAvailable policy, then run the script to write the file.
