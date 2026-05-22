---
title: "BGP"
description: "BGP reference — path-vector routing, eBGP vs iBGP, private ASNs, and why it matters for Kubernetes LoadBalancer services on bare metal."
date: 2026-05-14
draft: false
tags: ["bgp", "networking", "routing", "metallb", "kubernetes"]
showReadingTime: false
layout: single
---

BGP (Border Gateway Protocol) is the routing protocol that holds the internet together. Every major network operator uses it to advertise which IP prefixes they own and to exchange that information with peers. In a homelab context the scale is different but the mechanics are the same.

BGP is a path-vector protocol: each router advertises routes along with the path (sequence of ASNs) taken to reach them. Routers choose the best path based on a set of attributes and policy rules, then advertise that path to their peers.

---

## eBGP vs iBGP

**eBGP** (external BGP) — sessions between routers in *different* autonomous systems. Each party has a different ASN. This is what you configure between VyOS and OPNsense, and between VyOS and MetalLB.

**iBGP** (internal BGP) — sessions between routers in the *same* autonomous system. Used inside large networks to distribute external routes internally. Not relevant for a basic homelab setup.

---

## ASNs for private use

Autonomous System Numbers in the range **64512–65534** are reserved for private use ([RFC 6996](https://www.rfc-editor.org/rfc/rfc6996)) — the same concept as RFC 1918 private IP addresses. Assign one to each participant in your BGP topology:

| Participant             | Example ASN |
|-------------------------|-------------|
| OPNsense                | 64512       |
| VyOS                    | 64513       |
| MetalLB (Talos cluster) | 64514       |

---

## Why BGP for Kubernetes LoadBalancer IPs

Kubernetes `LoadBalancer` services need something external to the cluster to route traffic to them. In a cloud environment the cloud provider handles this automatically. On bare metal you need to do it yourself.

Two common approaches with [MetalLB](https://metallb.universe.tf):

**L2 mode** — MetalLB uses ARP (IPv4) or NDP (IPv6) to announce service IPs directly on the LAN. Simple to set up. Limitations: only one node handles traffic for each IP at a time (no real load balancing at the network layer), and the service IP must be in the same subnet as the nodes.

**[BGP mode](https://metallb.universe.tf/concepts/bgp/)** — MetalLB establishes a BGP session with an upstream router (VyOS, for example) and announces service IPs as /32 prefixes. The router learns the route and can ECMP across all nodes that are advertising it. More correct: actual load balancing, no subnet constraint, clean separation between cluster and network layer.

The tradeoff is that BGP mode requires a BGP-capable router in the path, which is why VyOS exists in this topology.

---

## Testing with a real BGP network

[DN42](https://dn42.eu) is a community-run experimental network that simulates the real internet using actual BGP, DNS, and whois infrastructure. Participants connect via WireGuard or other tunnels and peer with each other using real BGP sessions and real (private-range) ASNs. A good way to practice BGP outside the homelab without needing a production ASN.

---

## Related

- [VyOS](/public-notes/networking/vyos/) — the BGP peer router
- [VyOS + BGP experiment](/homelab/vyos-bgp/) — the actual setup in this homelab
