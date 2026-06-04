---
title: "Proxmox VE"
description: "Proxmox VE reference — open-source hypervisor combining KVM and LXC with a web UI. The practical VMware replacement."
date: 2026-05-14
draft: false
tags: ["proxmox", "virtualization", "kvm", "lxc", "bare-metal", "hypervisor", "clustering"]
showReadingTime: false
layout: single
---

Proxmox VE (Virtual Environment) is an open-source Type 1 hypervisor built on Debian. It runs KVM for full virtual machines and LXC for lightweight containers, managed through a web UI or API. The subscription model is optional — the community edition is fully functional without a paid license; the subscription gives access to the enterprise update repository and support.

---

## Comparison

| Platform       | License                    | VMs (KVM) | Containers | Clustering    | Web UI |
|----------------|----------------------------|-----------|------------|---------------|--------|
| Proxmox VE     | Open-source (optional sub) | Yes       | Yes (LXC)  | Yes           | Yes    |
| VMware ESXi    | Commercial                 | Yes       | No         | Yes (vCenter) | Yes    |
| Standalone KVM | Open-source                | Yes       | No         | Manual        | No     |
| oVirt          | Open-source                | Yes       | No         | Yes           | Yes    |

Proxmox is the practical choice when you want VMware-style management without the licensing cost, or when you want to run both VMs and containers on the same node.

---

## Core concepts

**Node** — a physical host running Proxmox VE. Managed independently or as part of a cluster.

**Cluster** — multiple nodes joined together. Share a unified management view and allow live migration of VMs between nodes. Uses [Corosync](https://corosync.github.io/corosync/) for distributed consensus.

**Quorum** — clusters require a majority of nodes to be reachable to avoid split-brain. Minimum useful cluster size is 3 nodes (loss of one node still leaves a majority). Two-node clusters need a quorum device (`qdevice`) to function safely.

**VM** — full virtual machine backed by QEMU/KVM. Hardware-level isolation. Arbitrary OS.

**Container (CT)** — LXC container. Shares the host kernel; lower overhead than a VM. Linux-only. Useful for services where you want process-level isolation without a full OS.

**Storage pool** — where disks and images live. Supported backends: local directory, LVM, LVM-thin, ZFS, NFS, CIFS, and Ceph (via `rbd`). ZFS and Ceph are the most capable options for a cluster — ZFS for local redundancy, Ceph for shared storage across nodes.

---

## Related

- [Proxmox VE documentation](https://pve.proxmox.com/pve-docs/)
- [Proxmox community forum](https://forum.proxmox.com/)
- [Corosync documentation](https://corosync.github.io/corosync/)
- [Ceph](/public-notes/cloud-infrastructure/ceph/) — distributed storage backend for Proxmox clusters
- [OpenStack](/public-notes/cloud-infrastructure/openstack/) — the next tier up the scale spectrum
- [Proxmox cluster in the homelab](/homelab/proxmox-cluster/)
