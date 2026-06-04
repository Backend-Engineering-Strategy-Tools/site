---
title: "Ceph"
description: "Ceph reference — distributed storage providing block, object, and file storage across multiple nodes with no single point of failure."
date: 2026-05-14
draft: false
tags: ["ceph", "storage", "distributed", "kubernetes", "block-storage", "object-storage"]
showReadingTime: false
layout: single
---

Ceph is an open-source distributed storage platform providing object, block, and file storage in a single unified system. It runs across multiple nodes and has no single point of failure.

The core idea: data is not stored on specific disks on specific nodes. Instead, the CRUSH algorithm distributes data across all available OSDs (Object Storage Daemons) based on a placement map. Add nodes and the cluster rebalances automatically. Lose a node and Ceph re-replicates from surviving copies without operator intervention.

---

## Storage types

| Type          | Interface                   | Typical use                   |
|---------------|-----------------------------|-------------------------------|
| Block (RBD)   | Kernel block device / iSCSI | Kubernetes PVCs, VM disks     |
| Object (RGW)  | S3-compatible API           | Backups, artifacts, media     |
| File (CephFS) | POSIX filesystem / NFS      | Shared filesystems, home dirs |

For Kubernetes workloads, RBD block storage via a StorageClass is the common path.

---

## Components

**MON (Monitor)** — maintains the cluster map; quorum-based, needs an odd number (typically 3 or 5). Not a data path.

**OSD (Object Storage Daemon)** — one per disk; handles actual data reads/writes and replication.

**MGR (Manager)** — collects metrics, hosts the dashboard, runs modules (balancer, alertmanager, etc.).

**MDS (Metadata Server)** — only required for CephFS; manages the filesystem namespace.

---

## Single-node constraint

A single-node Ceph cluster can be made to run (`allowMultiplePerNode: true` in Rook, replication `size: 1`), but it provides no actual redundancy. There is nothing to replicate to. This is fine for testing concepts; it is not a valid storage setup for anything you care about.

---

## Related

- [Ceph documentation](https://docs.ceph.com/)
- [Rook](/public-notes/cloud-infrastructure/rook/) — Kubernetes operator that manages Ceph clusters inside K8s
- [Proxmox](/public-notes/cloud-infrastructure/proxmox/) — Ceph is a native storage backend in Proxmox clusters
- [Rook + Ceph in the homelab](/homelab/rook-ceph/)
