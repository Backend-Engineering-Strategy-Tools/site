---
title: "VyOS + BGP on Proxmox"
date: 2026-05-14
draft: true
showReadingTime: false
layout: single
tags: ["vyos", "bgp", "proxmox", "metallb", "networking"]
---

Running [VyOS](/public-notes/cloud-infrastructure/vyos/) as a VM on the [Proxmox cluster](/homelab/proxmox-cluster/) and establishing a [BGP](/public-notes/cloud-infrastructure/bgp/) session with [OPNsense](/public-notes/cloud-infrastructure/opnsense/). The end goal is MetalLB on the [ODEN Talos cluster](/homelab/talos-omni/) announcing Kubernetes LoadBalancer service IPs through VyOS to OPNsense.

This page is a stub — the Proxmox cluster is not yet set up.

---

## Intended topology

```
Internet
    │
OPNsense / HEIMDAL (AS 64512)
    │  eBGP
VyOS VM on Proxmox (AS 64513)
    │  eBGP
MetalLB on ODEN / Talos (AS 64514)
```

MetalLB announces service /32 prefixes to VyOS. VyOS re-advertises upstream to OPNsense. Traffic for Kubernetes LoadBalancer services enters via OPNsense and routes through VyOS to the cluster.

---

## Hardware

| Role | Host | Notes |
|---|---|---|
| VyOS VM | Proxmox cluster (FREJA / TOR / TYR) | Iteration 1: single VM, no HA |
| Talos cluster | ODEN (SYS-005) | MetalLB in BGP mode |
| Gateway | HEIMDAL (SYS-009) | OPNsense, BGP peer upstream |

---

## Iteration 1 scope

- Deploy VyOS as a KVM VM on Proxmox
- Configure a basic eBGP session between VyOS and OPNsense
- Verify route advertisement and basic routing

MetalLB peering and service IP announcement come after Iteration 1 is stable.

---

## Notes

*In progress — to be filled in once the Proxmox cluster is running.*
