---
title: "OPNsense in the homelab"
description: "OPNsense on the Sun Fire X4150 — perimeter gateway for both the homelab and the house. Running, not clean, redo on the todo list."
date: 2026-05-14
draft: false
showReadingTime: false
layout: single
tags: ["opnsense", "firewall", "networking"]
---

[OPNsense](/public-notes/networking/opnsense/) running on the Sun Fire X4150 — perimeter gateway for both the homelab and the home network.

Current state: inherited setup, not clean, not properly documented. It works, but it was not built with intention. A redo is on the todo list.

Dual role is intentional and will stay that way — OPNsense on the Sun Fire handles both the homelab and the house. One box, one gateway.

The Sun Fire X4150 handles it without breaking a sweat. Old, but solid.

---

## TODO: Clean reinstall

- Fresh OPNsense install on the Sun Fire
- Rename from `router.mjnet.info` → `heimdal.mjnet.info`
- Document the full configuration: firewall rules, DHCP, DNS (Unbound), TFTP/PXE, BGP peering with VyOS

**On the hostname rename**: making the router's hostname publicly resolvable is a mild information disclosure — it signals which host is the perimeter device. In practice the IP is what matters, and if it's already reachable the name adds little. Still worth being deliberate about what resolves publicly.

---

## Intended role

```
ISP/WAN → OPNsense (heimdal.mjnet.info) → LAN switch → rack
```

- Perimeter firewall and NAT gateway
- DHCP for the LAN
- DNS via Unbound
- TFTP/PXE for bare-metal provisioning
- eBGP peer upstream of VyOS (future — see [VyOS + BGP](/homelab/vyos-bgp/))
