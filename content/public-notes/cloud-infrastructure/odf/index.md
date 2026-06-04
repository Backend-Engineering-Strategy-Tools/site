---
title: "OpenShift Data Foundation"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["odf", "openshift", "ceph", "kubernetes", "storage", "rook"]
---

OpenShift Data Foundation (ODF) is Red Hat's enterprise Kubernetes storage platform, built on [Ceph](/public-notes/cloud-infrastructure/ceph/) orchestrated by [Rook](/public-notes/cloud-infrastructure/rook/). Where Rook-Ceph is the open source upstream, ODF packages it with an operator, a validated configuration, enterprise support, and integration with the OpenShift console. It provides block (RBD), file (CephFS), and object (S3-compatible via Ceph RGW) storage as Kubernetes StorageClasses on the same hardware.

## What it provides

Three storage modes from one cluster:

| Mode | StorageClass | Use case |
|---|---|---|
| Block (RBD) | `ocs-storagecluster-ceph-rbd` | Databases, stateful apps needing a single-writer disk |
| File (CephFS) | `ocs-storagecluster-cephfs` | Shared filesystems, multiple pods reading/writing the same volume |
| Object | S3-compatible endpoint | Buckets via `ObjectBucketClaim`, backup targets, artifact storage |

## Installation

ODF installs via the ODF operator from OperatorHub. The operator creates a `StorageCluster` CR that drives the Ceph deployment:

```yaml
apiVersion: ocs.openshift.io/v1
kind: StorageCluster
metadata:
  name: ocs-storagecluster
  namespace: openshift-storage
spec:
  storageDeviceSets:
    - name: ocs-deviceset
      count: 1
      replica: 3
      dataPVCTemplate:
        spec:
          storageClassName: local-storage
          volumeMode: Block
          resources:
            requests:
              storage: 1Ti
```

Requires at minimum three nodes with dedicated block devices. The operator handles Ceph cluster formation, monitors, MGRs, and OSDs.

## vs Rook-Ceph

ODF IS Rook-Ceph under the hood. The difference is packaging and support: ODF is tested and supported on OpenShift, includes the NooBaa multi-cloud gateway for object storage federation, and integrates with the OpenShift UI. For self-managed Kubernetes outside OpenShift, raw Rook-Ceph is the equivalent path.

## Resources

- [ODF documentation](https://access.redhat.com/documentation/en-us/red_hat_openshift_data_foundation/)
- [Rook documentation](https://rook.io/docs/rook/latest/)
