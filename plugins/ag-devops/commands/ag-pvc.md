---
name: ag-pvc
description: "Generate a PersistentVolumeClaim Helm template for an Emerald stateful component using the scaffold-pvc scripted skill. Writes gitops/templates/<name>-pvc.yaml directly."
---
Use the `scaffold-pvc` skill to generate a PVC Helm template. Ask for the component name, storage size (e.g. 10Gi), storage class, and access mode, then run the script to write the file.
