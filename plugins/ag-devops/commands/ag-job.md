---
name: ag-job
description: "Generate a Job Helm template for an OpenShift Emerald component using the scaffold-job scripted skill. For one-shot batch workloads, DB migrations, or initialization tasks. Writes gitops/templates/<name>-job.yaml directly."
---
Use the `scaffold-job` skill to generate a Job Helm template. Ask for the job name, data class, backoff limit, and TTL seconds after finished, then run the script to write the file.
