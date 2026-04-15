---
name: scaffold-docker-ci
description: Use when adding Docker build and push CI to an application repo using the ag-devops docker-dind shared workflow. Generates .github/workflows/docker.yml that calls ci/.shared/docker.yml from bcgov-c/ag-devops. Writes directly to the target workflow directory.
allowed-tools:
  - Bash
  - Read
  - Write
command: python ./scripts/scaffold.py --type docker-ci --image "$IMAGE" --registry "$REGISTRY" --context "$CONTEXT" --output-dir "$OUTPUT_DIR"
---

# Scaffold Docker CI

Generate a `.github/workflows/docker.yml` consumer workflow that calls the
`bcgov-c/ag-devops` shared Docker build and push workflow.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--image` | ✅ | — | Image name e.g. my-api |
| `--registry` | | `ghcr.io` | Container registry |
| `--context` | | `.` | Docker build context |
| `--file` | | `Dockerfile` | Path to Dockerfile |
| `--platforms` | | `linux/amd64` | Target platforms |
| `--output-dir` | | `.github/workflows` | Destination directory |

## Output

`.github/workflows/docker.yml`

## Notes

- Requires `GHCR_TOKEN` and `GHCR_USERNAME` secrets in the repository.
- `push: true` only on push events to main; PRs only build and scan.
- The shared workflow handles tagging automatically with `auto_tagging: true`.

