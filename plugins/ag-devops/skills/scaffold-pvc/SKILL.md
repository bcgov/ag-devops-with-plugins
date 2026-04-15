---
name: scaffold-pvc
description: Use when generating a PersistentVolumeClaim Helm template for an OpenShift Emerald stateful component using ag-helm-templates. Writes gitops/templates/<name>-pvc.yaml directly.
allowed-tools:
  - Bash
  - Read
  - Write
command: python plugins/ag-devops/skills/scaffold-pvc/scripts/generate.py --name "$NAME" --size "$SIZE" --storage-class "$STORAGE_CLASS" --output-dir "$OUTPUT_DIR"
---

# Scaffold PVC

Generate a PersistentVolumeClaim Helm template using the `ag-template.pvc`
"set + define + include" pattern.

## Parameters

| Flag | Required | Default | Description |
|---|:---:|---|---|
| `--name` | ✅ | — | Component name |
| `--size` | | `1Gi` | Storage size |
| `--storage-class` | | `netapp-file-standard` | StorageClass name |
| `--access-mode` | | `ReadWriteOnce` | Access mode |
| `--output-dir` | | `gitops/templates` | Destination directory |

## Output

`gitops/templates/<name>-pvc.yaml`
