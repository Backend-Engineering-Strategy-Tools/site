---
title: "Rook"
date: 2026-05-14
draft: false
tags: ["rook", "ceph", "storage", "kubernetes", "operator"]
showReadingTime: false
layout: single
---

Rook is a Kubernetes operator that deploys and manages storage systems — primarily [Ceph](/public-notes/cloud-infrastructure/ceph/) — as native Kubernetes resources. The distinction: Ceph is the storage system; Rook is the Kubernetes wiring around it.

Without Rook you would run Ceph manually (or via `cephadm`) and then configure the Kubernetes CSI driver separately. Rook collapses that into CRDs and handles the full lifecycle: deployment, configuration, expansion, upgrades, and failure recovery.

---

## How it works

Rook introduces several CRDs:

**CephCluster** — declares the cluster: which nodes, which disks to use as OSDs, replication settings.

**CephBlockPool** — defines a Ceph pool (replication factor, failure domain). Maps to an RBD pool.

**StorageClass** — references a CephBlockPool and enables dynamic PVC provisioning. Kubernetes workloads request storage; Rook/Ceph fulfils it.

**CephFilesystem** — deploys CephFS + MDS for POSIX shared filesystem access.

**CephObjectStore** — deploys the Ceph RGW S3-compatible object storage gateway.

---

## Typical install sequence

```sh
kubectl apply -f https://raw.githubusercontent.com/rook/rook/refs/tags/v1.17.9/deploy/examples/crds.yaml
kubectl apply -f https://raw.githubusercontent.com/rook/rook/refs/tags/v1.17.9/deploy/examples/common.yaml
kubectl apply -f https://raw.githubusercontent.com/rook/rook/refs/tags/v1.17.9/deploy/examples/operator.yaml
```

Then apply a `CephCluster` manifest declaring your storage topology, followed by `CephBlockPool` and `StorageClass` for PVC support.

---

## Single-node considerations

A single-node setup requires `allowMultiplePerNode: true` in the `CephCluster` spec (MONs, MGR, and OSDs all land on the same node). Replication `size` must be set to `1` — there is nowhere else to replicate. This works for experimentation; it is not a production configuration. See [Ceph](/public-notes/cloud-infrastructure/ceph/) for details on the replication model.

---

## Related

- [Ceph](/public-notes/cloud-infrastructure/ceph/) — the underlying storage system
