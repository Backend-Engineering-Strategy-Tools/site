---
title: "Proxmox Cluster in the homelab"
description: "Building a three-node Proxmox VE cluster on IBM rack servers — a shared virtualization platform for running VMs and LXC containers."
date: 2026-05-14
draft: false
showReadingTime: false
layout: single
tags: ["proxmox", "virtualization", "bare-metal", "cluster"]
---

Getting a three-node [Proxmox VE](/public-notes/cloud-infrastructure/proxmox/) cluster running in the homelab.

The goal is a shared virtualization platform for running VMs and LXC containers across the rack. Also, a good excuse to kick the tires on Proxmox itself so, naturally, let's needlessly complicate things with some self-imposed constraints: 

1. run it clustered
2. don't use any hardware already earmarked for other projects

---

## Hardware

I am going try and use three IBM rack servers from the [inventory](/homelab/inventory/systems/).

| Asset ID | Hostname | Model                      | Form Factor | RAM  | CPU    |
|----------|----------|----------------------------|-------------|------|--------|
| SYS-001  | FREJA    | IBM System x3550 M1 (7978) | 1U          | 24GB | single |
| SYS-002  | TYR      | IBM System x3650 M1 (7979) | 2U          | 64GB | dual   |
| SYS-003  | TOR      | IBM System x3650 M1 (7979) | 2U          | 64GB | dual |

Three nodes satisfies Corosync quorum without needing a `qdevice` — losing one node still leaves a majority.

---

## Installation

*In progress.*

---

## Cluster formation

*In progress.*
