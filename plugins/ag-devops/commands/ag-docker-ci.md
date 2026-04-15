---
name: ag-docker-ci
description: "Add a Docker build and push CI workflow to this repository using the scaffold-docker-ci scripted skill. Generates .github/workflows/docker.yml that calls the ag-devops docker-dind shared workflow. Includes Trivy vulnerability scanning and auto-tagging."
---
Use the `scaffold-docker-ci` skill to generate a Docker CI workflow. Ask for the image name, registry (default ghcr.io), Dockerfile path, and build context, then run the script to write .github/workflows/docker.yml.
