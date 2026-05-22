---
title: "VyOS"
description: "VyOS reference — open-source network OS with commit/rollback CLI, native BGP via FRRouting, and Ansible/Terraform automation support."
date: 2026-05-14
draft: false
tags: ["vyos", "networking", "bgp", "router", "vm"]
showReadingTime: false
layout: single
---

VyOS is an open-source network operating system built on Debian Linux. It runs on bare metal or as a VM, and is configured via a CLI with a commit/rollback model similar to Juniper JunOS. Configuration changes are staged and only take effect when you explicitly `commit` — there is no live-editing a running config and hoping nothing breaks.

It ships FRRouting (FRR) as the routing engine, giving it native support for BGP, OSPF, IS-IS, and other protocols. This is its main distinction from [OPNsense](/public-notes/networking/opnsense/) for homelab use: OPNsense is a firewall appliance that can do some routing; VyOS is a routing OS that can also do firewall.

---

## Configuration model

```
vyos@router# set interfaces ethernet eth0 address '192.168.1.254/24'
vyos@router# set protocols bgp system-as '65001'
vyos@router# commit
vyos@router# save
```

`configure` enters configuration mode. `set` stages a change. `commit` applies it. `save` persists it to disk. `rollback` reverts to the last committed state if something goes wrong. The separation between staging and applying is genuinely useful when changing routing configuration remotely.

---

## Key features

| Feature | Notes |
|---|---|
| BGP | Via FRRouting; full eBGP/iBGP support |
| OSPF / IS-IS | Also via FRR |
| Static routing | Standard |
| VLAN | 802.1Q trunking |
| NAT | Source and destination NAT |
| Firewall | Zone-based, stateful |
| WireGuard | Built-in |
| OpenVPN | Built-in |
| DHCP server | Built-in |
| VXLAN | Supported |

---

## VyOS vs OPNsense

VyOS is the right choice when you want a dedicated BGP peer or a router VM with a clean CLI config model. OPNsense is the right choice when you want a full gateway appliance with a web UI.

---

## Automation

VyOS is designed to be automated — the commit/rollback model maps cleanly onto infrastructure-as-code workflows.

**REST API** — built-in HTTP API for retrieving and applying configuration programmatically. Useful for scripting config changes without SSH.

**Ansible** — official `vyos.vyos` collection on Ansible Galaxy. Modules for interfaces, BGP, firewall rules, and more. Changes go through the normal commit/rollback cycle.

**Terraform** — community provider available. Less mature than the Ansible collection but usable for provisioning router config alongside other infrastructure.

---

## Related

- [VyOS documentation](https://docs.vyos.io/)
- [VyOS REST API](https://docs.vyos.io/en/latest/automation/vyos-api.html)
- [VyOS Ansible collection](https://docs.ansible.com/ansible/latest/collections/vyos/vyos/index.html)
- [VyOS rolling release downloads](https://vyos.net/get/)
- [BGP](/public-notes/networking/bgp/) — protocol background
- [OPNsense](/public-notes/networking/opnsense/) — the complementary edge gateway
- [VyOS + BGP in the homelab](/homelab/vyos-bgp/) — the actual setup
