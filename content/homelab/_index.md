---
title: "Homelab"
date: 2026-04-12
draft: false
description: "A garage lab running real infrastructure on old enterprise hardware. Kubernetes on bare metal, networking experiments, and things that would be irresponsible to try on a work cluster."
layout: single
showReadingTime: false
---

A lab in the garage — blade server, OPNsense box, switches, and whatever else is needed to run real infrastructure at home. Kubernetes on bare metal, networking experiments, testing things that would be irresponsible to try on a work cluster.

Worth being clear about what this is: a **lab**, not always-on infrastructure. It gets powered up when there is something to run or test, and shut down again when the session is done. No home theatre, no NAS for the family photos. Just a place to break things intentionally and learn from it without consequences.

---

A note on the hardware: most of it is old. Enterprise gear from 2008 to 2013, picked up cheaply after data center retirements, gifted or otherwise.

> I.e. beg, borrow && steal !

The principles transfer setting up Kubernetes on a ten-year-old blade is the same discipline as setting it up on current hardware. Performance less so. Running inference on a GTX 770 will produce roughly one token per second. That is fine, I also have a subscription to Claude Code.

---

### [Hardware Inventory](/homelab/inventory/)

### [Talos Linux in the homelab PXE boot via Omni](/homelab/talos-omni/)

### [Proxmox Cluster in the homelab](/homelab/proxmox-cluster/)

### [Rook + Ceph in the homelab](/homelab/rook-ceph/)

### [OPNsense — ~~lab~~ production](/homelab/opnsense/)

*VyOS + BGP — coming soon*

*LLM Training on Bare Metal — coming soon*

*LLM Inference on Bare Metal — coming soon*
