---
title: "Velero"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["velero", "kubernetes", "backup", "disaster-recovery", "migration"]
---

Velero backs up and restores Kubernetes clusters. It captures both Kubernetes resource definitions (deployments, services, configmaps, secrets, CRDs) and persistent volume data, stores them in object storage (S3, GCS, Azure Blob), and can restore them to the same cluster or a different one. The primary use cases are disaster recovery, cluster migration, and namespace cloning.

## How it works

Velero runs as a controller in the cluster. A `Backup` CR triggers a snapshot of selected resources:

```yaml
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: daily-backup
  namespace: velero
spec:
  includedNamespaces:
    - production
  storageLocation: default
  ttl: 720h  # 30 days
```

Persistent volume data is handled via storage provider snapshots (CSI snapshots, AWS EBS snapshots) or a file-system-level backup using the node-agent daemonset (formerly Restic). CSI snapshot integration is the preferred modern approach.

Scheduled backups run via a `Schedule` CR:

```yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: daily
  namespace: velero
spec:
  schedule: "0 2 * * *"
  template:
    includedNamespaces:
      - production
    ttl: 720h
```

## Restore

Restoring is a `Restore` CR pointing at a backup:

```bash
velero restore create --from-backup daily-backup
```

Velero recreates the Kubernetes objects and restores volume data. Namespaces can be remapped on restore — useful for cloning production to staging.

## Cluster migration

The standard migration pattern: back up from the source cluster, configure the destination cluster to point at the same object storage bucket, restore. Velero handles the resource recreation; DNS cutover is a separate step.

## Resources

- [Velero documentation](https://velero.io/docs/)
- [CSI snapshot support](https://velero.io/docs/main/csi/)
