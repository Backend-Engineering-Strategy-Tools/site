---
title: "etcd"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["etcd", "kubernetes", "distributed-systems", "key-value", "raft"]
---

etcd is the distributed key-value store that backs Kubernetes. Every Kubernetes object — pods, services, deployments, configmaps, secrets — is stored in etcd. The API server is the only component that reads and writes it directly; everything else in the cluster reads from the API server's cache. etcd's reliability is the cluster's reliability: if etcd loses quorum, the Kubernetes control plane stops functioning.

## Raft consensus

etcd uses the Raft consensus algorithm. The cluster elects a leader; all writes go through the leader, which replicates them to followers before acknowledging the write. The cluster tolerates `(n-1)/2` node failures — a three-node cluster survives one failure, a five-node cluster survives two. This is why control plane node counts are always odd. Three nodes is standard for production; five for clusters where control plane availability is critical.

## Watches and revisions

Every write increments a global revision counter. Clients can watch a key or key prefix and receive every change since a given revision. This is how the Kubernetes controller manager and scheduler work — they hold long-lived watch connections and react to changes in specific resource types without polling.

## Operations

```bash
# Snapshot backup
etcdctl snapshot save /backup/etcd-snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key

# Restore from snapshot
etcdctl snapshot restore /backup/etcd-snapshot.db --data-dir=/var/lib/etcd-restore

# Check cluster health
etcdctl endpoint health --cluster
```

Backing up etcd regularly is the most critical operational task for a Kubernetes cluster. The snapshot is the only path to full recovery if cluster state is lost.

## Resources

- [etcd documentation](https://etcd.io/docs/)
- [Kubernetes etcd administration](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)
