---
name: ag-route
description: "Generate an OpenShift Route Helm template for an Emerald component using the scaffold-route scripted skill. Includes the required AVI annotation values snippet. Writes gitops/templates/<name>-route.yaml directly."
---
Use the `scaffold-route` skill to generate an OpenShift Route Helm template. Ask for the component name, port, data class, and optional hostname, then run the script to write the file and print the required values.yaml snippet.
