---
title: "Rook + Ceph on ODEN"
date: 2026-05-14
draft: false
showReadingTime: false
layout: single
tags: ["rook", "ceph", "storage", "kubernetes", "bare-metal"]
---

Attempting to add persistent block storage to the [ODEN](/homelab/inventory/systems/) single-node Talos cluster using [Rook](/public-notes/cloud-infrastructure/rook/) and [Ceph](/public-notes/cloud-infrastructure/ceph/). This did not fully succeed — the setup reached the point of a bound PVC and a working write test, but the cluster was not left in a clean stable state. Notes are here for completeness.

---

## Hardware

ODEN has five storage devices:

| Device         | Type                        | Size   | Role                    |
|----------------|-----------------------------|--------|-------------------------|
| `/dev/sdb`     | Kingston SA400S3 SSD (SATA) | 120 GB | Boot disk — leave alone |
| `/dev/nvme0n1` | Samsung 970 EVO NVMe        | 500 GB | OSD                     |
| `/dev/sdc`     | Kingston SA400S3 SSD (SATA) | 120 GB | OSD                     |
| `/dev/sdd`     | Kingston SA400S3 SSD (SATA) | 120 GB | OSD                     |
| `/dev/sde`     | Kingston SA400S3 SSD (SATA) | 120 GB | OSD                     |

Do not add `/dev/sdb` to Ceph. It is the boot disk.

---

## Step 1 — Install the Rook operator

```sh
kubectl apply -f https://raw.githubusercontent.com/rook/rook/refs/tags/v1.17.9/deploy/examples/crds.yaml
kubectl apply -f https://raw.githubusercontent.com/rook/rook/refs/tags/v1.17.9/deploy/examples/common.yaml
kubectl apply -f https://raw.githubusercontent.com/rook/rook/refs/tags/v1.17.9/deploy/examples/operator.yaml
```

Wait for the operator pod to be running in `rook-ceph` namespace before continuing.

---

## Step 2 — CephCluster (single-node)

Single-node requires `allowMultiplePerNode: true` and explicit disk selection. The cluster-test example from the Rook repo is a reasonable starting point:

```yaml
storage:
  useAllNodes: false
  nodes:
    - name: "192.168.1.171"
      devices:
        - name: "nvme0n1"
        - name: "sdc"
        - name: "sdd"
        - name: "sde"
```

Reference: [cluster-test.yaml](https://github.com/rook/rook/blob/release-1.17/deploy/examples/cluster-test.yaml)

---

## Step 3 — CephBlockPool and StorageClass

```yaml
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: replicapool
  namespace: rook-ceph
spec:
  replicated:
    size: 1
```

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-ceph-block
provisioner: rook-ceph.rbd.csi.ceph.com
parameters:
  clusterID: rook-ceph
  pool: replicapool
  imageFormat: "2"
  imageFeatures: layering
reclaimPolicy: Delete
```

---

## Step 4 — PVC test

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: rook-ceph-block
  resources:
    requests:
      storage: 10Gi
```

PVC reached `Bound`. A BusyBox pod mounting it could write to `/mnt`. The Ceph dashboard (`kubectl -n rook-ceph port-forward svc/rook-ceph-mgr-dashboard 7000:7000`) showed OSDs active and the pool present.

---

## What did not work

The cluster ran but was not left stable. Single-node Ceph produces health warnings by design (no redundancy, no failure domain separation). More importantly, the setup was not revisited after initial testing and there are unresolved questions about:

- CSI driver behaviour on Talos (Talos has specific requirements for CSI socket paths)
- Whether the dashboard warnings were cosmetic or indicated real issues
- Long-term stability under actual workloads

This is left as a draft until there is time to run it properly — ideally on more than one node.
