---
name: ag-sast-ci
description: "Add SonarQube SAST and Gitleaks secrets scanning CI to this repository using the scaffold-sast-ci scripted skill. Generates .github/workflows/sast.yml that calls the ag-devops sast composite action."
---
Use the `scaffold-sast-ci` skill to generate a SAST CI workflow. Ask for the SonarQube project key and host URL, then run the script to write .github/workflows/sast.yml. Remind the user to add SONAR_TOKEN and GITLEAKS_LICENSE secrets.
