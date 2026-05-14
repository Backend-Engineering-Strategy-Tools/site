---
title: "OpenStack"
description: "OpenStack reference — open-source IaaS for building private clouds, with notes on scale fit and running OpenStack on Kubernetes."
date: 2026-05-14
draft: false
tags: ["openstack", "iaas", "cloud", "bare-metal", "virtualization"]
showReadingTime: false
layout: single
---

OpenStack is an open-source IaaS platform — it turns a pool of bare-metal servers into a self-service cloud: virtual machines, block storage, networking, and object storage, all driven by API.

https://www.openstack.org/

---

## Scale and fit

There is a rough spectrum of virtualization tools, and picking the wrong tier is a common mistake:

**Proxmox / VMware / Hyper-V** — the right choice when you want to run virtual machines. SMB, homelab, or a small ops team managing infrastructure directly. Reasonable setup cost, manageable operational overhead, one or a few admins in control. Think of it as a VMware replacement.

**OpenStack** — the right choice when you are *building a cloud*, not just running VMs. Multi-tenant infrastructure where teams self-service their own compute, networking, and storage via API. The operational complexity is real and significant; it pays off when the cloud-like abstraction is the actual product, or when the scale justifies the overhead.

The rule of thumb: if the question is "how do I replace VMware?", the answer is Proxmox. If the question is "how do I build a private cloud platform?", the answer might be OpenStack.

---

## Core Components

| Service | Code Name | What it does |
|---|---|---|
| Compute | Nova | Schedules and manages VM lifecycle |
| Networking | Neutron | Virtual networks, routers, floating IPs, security groups |
| Block Storage | Cinder | Persistent volumes attached to VMs |
| Image Service | Glance | Stores and serves OS images |
| Identity | Keystone | Auth, service catalog, RBAC |
| Dashboard | Horizon | Web UI (optional) |
| Object Storage | Swift | S3-like object storage (optional) |
| Bare Metal | Ironic | Provisions physical machines instead of VMs |

You do not need all of them. A minimal useful deployment is Nova + Neutron + Cinder + Glance + Keystone.

---

## OpenStack on Kubernetes

OpenStack services are just applications — and they can run as Kubernetes workloads. Two projects make this practical:

**[OpenStack-Helm](https://github.com/openstack/openstack-helm)** — official Helm charts for deploying OpenStack services on an existing Kubernetes cluster. Each service (Nova, Neutron, Cinder, etc.) becomes a Helm release. Upgrades follow standard rolling deployment patterns.

**[Atmosphere](https://github.com/vexxhost/atmosphere)** (by VEXXHOST) — a higher-level operator built on top of OpenStack-Helm. Adds Ansible automation, health checks, and a more opinionated deployment model. Targets production use.

The practical implication: you can run a Talos cluster and deploy OpenStack on top of it — OpenStack as a tenant of Kubernetes rather than a separate platform. This inverts the usual relationship (where Kubernetes runs on top of OpenStack) and is an interesting architectural option for homelab and small private cloud deployments.

[Fairbanks](https://www.fairbanks.nl/) (Dutch hosting company specialising in sovereign private clouds) does exactly this in production. Their talk [OpenStack on Talos Linux](https://www.youtube.com/watch?v=zU8mT2f2Hxc) is the clearest real-world example of the pattern.

---

## Deployment Options

**Kolla-Ansible**  
https://docs.openstack.org/kolla-ansible/latest/  
Containerised OpenStack deployed via Ansible. Production-grade, well-maintained. The practical choice for homelab and small-scale production deployments. Each service runs in its own container.

**DevStack**  
https://docs.openstack.org/devstack/latest/  
All-in-one development install. Not for production or anything you want to survive a reboot. Good for learning the API surface.

**Canonical OpenStack (Juju / Sunbeam)**  
https://ubuntu.com/openstack  
Ubuntu-opinionated deployment. Sunbeam is a newer minimal footprint option. Good if you're already in the Ubuntu/Juju ecosystem.

---

## Concepts Worth Understanding

**Flavors** — VM sizing templates (vCPU, RAM, disk). You define these; instances pick from them.

**Security Groups** — stateful firewall rules applied per-port. Default-deny inbound.

**Floating IPs** — externally routable IPs that can be associated/disassociated from instances dynamically.

**Availability Zones** — logical groupings of compute nodes. Useful for fault isolation even at small scale.

**Hypervisors** — Nova supports KVM (default), QEMU, VMware, and others. KVM on Linux is the standard.

---

## Relevance to the Lab

The [LLM training experiment](/homelab/llm-training/) plans to use OpenStack as the IaaS layer over the [blade nodes](/homelab/inventory/systems/) in ASGARD — Nova for compute scheduling, Neutron for cluster networking, Cinder for shared model/dataset storage backed by Ceph.
