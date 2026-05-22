---
title: "Firewall and router OS options"
description: "Overview of open-source and commercial router/firewall operating systems — OPNsense, pfSense, VyOS, and alternatives. Trade-offs by use case."
date: 2026-05-22
draft: false
showReadingTime: false
layout: single
tags: ["networking", "firewall", "router", "opnsense", "pfsense", "vyos", "mikrotik"]
---

Options for running a software-defined firewall or router, from homelab appliances to full routing OS deployments.

---

## The main split: appliance vs routing OS

Most options fall into one of two categories:

**Firewall appliances** (OPNsense, pfSense, IPFire) — web UI-first, designed around the perimeter firewall use case. NAT, DHCP, DNS, VPN, IDS/IPS out of the box. Routing is possible but secondary.

**Routing operating systems** (VyOS, MikroTik RouterOS, FRRouting) — CLI-first, designed around dynamic routing protocols (BGP, OSPF). Firewall rules exist but feel like an afterthought compared to the routing capabilities.

For a homelab perimeter gateway: appliance. For BGP peering, complex routing topologies, or network-as-code: routing OS.

---

## OPNsense

Open-source firewall and routing platform based on FreeBSD. Fork of pfSense, with a stronger emphasis on community ownership and more frequent security updates.

Full gateway function: stateful firewall, NAT, DHCP, DNS (Unbound), TFTP/PXE, VPN (WireGuard, OpenVPN, IPsec), traffic shaping, IDS/IPS (Suricata), DDNS.

BGP is available via the FRRouting plugin but is not a first-class feature — VyOS is better suited for BGP-heavy setups.

→ [OPNsense reference](/public-notes/networking/opnsense/)

**Best for**: homelab perimeter gateway, home network, small office. The current actively-maintained community fork of the pfSense lineage.

---

## pfSense

The original FreeBSD-based firewall appliance. Same underlying capabilities as OPNsense — they share a common ancestor (m0n0wall).

Now owned by Netgate. The **Community Edition (CE)** remains open source; **pfSense Plus** is commercial and ships only on Netgate hardware or as a cloud image. Development focus has shifted toward Plus; CE updates have been slower.

The practical difference between OPNsense and pfSense CE is increasingly small at the feature level. The main reasons to choose one over the other are familiarity, UI preference, and update cadence. OPNsense is the more actively developed option for community use.

**Best for**: environments where pfSense is already deployed, or where existing documentation/tooling targets it.

---

## VyOS

Open-source network OS built on Debian. Configured via a CLI with a commit/rollback model (similar to Juniper JunOS). Native BGP, OSPF, IS-IS via FRRouting.

Configuration is declarative and version-controlled — the entire running config is a text file, which makes it automation-friendly (Ansible, Terraform).

The rolling release is free; LTS releases require a subscription.

→ [VyOS reference](/public-notes/networking/vyos/)

**Best for**: BGP peering, complex routing topologies, automation-driven network config, VM-based routing inside a cluster.

---

## MikroTik RouterOS

Commercial OS that runs on MikroTik hardware and as a VM (CHR — Cloud Hosted Router). Full routing OS with BGP, OSPF, MPLS, and a firewall. Configured via Winbox GUI, web UI, or CLI.

Very capable at the price point. Hardware is inexpensive. The learning curve is steeper than OPNsense but shallower than VyOS for most tasks. Community is large and documentation is thorough.

CHR (the VM version) is free for speeds up to 1Mbps; licensed tiers above that. On physical hardware, the license is included.

**Best for**: cost-conscious deployments that need routing features, or environments already using MikroTik hardware.

---

## IPFire

Linux-based firewall focused on simplicity and security hardening. Web UI, stateful firewall, IDS (Snort/Suricata), VPN (OpenVPN, WireGuard, IPsec), proxy.

Less feature-rich than OPNsense but lighter and more opinionated. No BGP. Easier to get to a secure baseline quickly.

**Best for**: simple gateway where you want a small attack surface and don't need advanced routing or a plugin ecosystem.

---

## Untangle / Arista Edge Threat Management

Commercial product with a free tier (NG Firewall). Web UI, application-layer filtering, content inspection, threat management features. More enterprise-oriented than the others.

Requires registration. The free tier is limited; the feature set that differentiates it from OPNsense is mostly in the commercial tiers.

**Best for**: environments that need application-layer filtering with a managed UI, or commercial support requirements.

---

## Comparison

| | OPNsense | pfSense CE | VyOS | MikroTik RouterOS | IPFire |
|---|---|---|---|---|---|
| Base OS | FreeBSD | FreeBSD | Debian | Proprietary | Linux |
| Primary interface | Web UI | Web UI | CLI | Winbox / CLI | Web UI |
| BGP / OSPF | Plugin (FRR) | Plugin (FRR) | Native (FRR) | Native | No |
| IDS/IPS | Suricata | Snort/Suricata | No | No | Snort/Suricata |
| WireGuard | Yes | Yes (Plus) | Yes | Yes | Yes |
| DDNS | Yes | Yes | Via script | Yes | Yes |
| Cost | Free | Free (CE) | Free (rolling) | Hardware license | Free |
| Community | Active | Slowing (CE) | Active | Active | Active |

---

## Further reading

- [OPNsense in the homelab](/homelab/opnsense/)
- [VyOS + BGP in the homelab](/homelab/vyos-bgp/)
