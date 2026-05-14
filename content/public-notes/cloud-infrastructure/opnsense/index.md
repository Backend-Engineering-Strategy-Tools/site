---
title: "OPNsense"
description: "OPNsense reference — open-source FreeBSD-based firewall and routing platform covering the full gateway function."
date: 2026-05-14
draft: false
tags: ["opnsense", "firewall", "router", "networking", "freebsd"]
showReadingTime: false
layout: single
---

OPNsense is an open-source firewall and routing platform based on FreeBSD. It is a fork of pfSense, with a stronger emphasis on community ownership, a cleaner UI, and more frequent security updates. Both are descendants of m0n0wall.

It covers the full gateway function: stateful firewall, NAT, DHCP, DNS, TFTP, VPN, traffic shaping, and IDS/IPS — all through a web UI or via the API.

---

## Feature overview

| Feature | Notes |
|---|---|
| Stateful firewall | Zone-based rules, aliases, scheduling |
| NAT | Outbound, inbound (port forwarding), 1:1 |
| DHCP | ISC DHCPv4 and Kea; supports network boot options |
| DNS | Unbound resolver with DNSSEC; optional forwarding |
| TFTP | Simple server at `/usr/local/tftp`; used for PXE boot |
| VPN | WireGuard, OpenVPN, IPsec |
| IDS/IPS | Suricata integration |
| Traffic shaping | HFSC, PRIQ, CAKE |
| BGP / routing | FRRouting plugin available (not enabled by default) |

---

## OPNsense vs pfSense vs VyOS

| | OPNsense | pfSense | VyOS |
|---|---|---|---|
| Base | FreeBSD | FreeBSD | Debian Linux |
| License | BSD (true FOSS) | BSL (mixed) | GPL |
| Model | Firewall appliance | Firewall appliance | Network OS |
| Config interface | Web UI + API | Web UI | CLI (commit/rollback) |
| BGP | Via FRRouting plugin | Via FRRouting plugin | Native (FRRouting built-in) |
| Typical use | Edge gateway, firewall | Edge gateway, firewall | Router, BGP peer, lab router VM |

OPNsense and pfSense are both appliance-style: you configure them through a UI and they manage all the underlying services for you. [VyOS](/public-notes/cloud-infrastructure/vyos/) is a network OS in the Juniper/Cisco tradition — CLI-first, commit/rollback, intended for use as a router or BGP peer rather than a full gateway appliance.

---

## Related

- [OPNsense documentation](https://docs.opnsense.org/)
- [OPNsense plugins](https://github.com/opnsense/plugins)
- [iPXE + OPNsense](/public-notes/cloud-infrastructure/hardware-provisioning/ipxe-opnsense/) — PXE boot configuration via OPNsense DHCP and TFTP
- [OPNsense in the homelab](/homelab/opnsense/) — current setup and planned redo
