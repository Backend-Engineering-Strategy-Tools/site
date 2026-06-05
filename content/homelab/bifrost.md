---
title: "BIFROST — Raspberry Pi jump node"
description: "A first-gen Raspberry Pi in the rack as a permanent low-power SSH entry point into the homelab. Port forwarding through OPNsense, Route53 CNAME, and a DNS override for split-horizon resolution."
date: 2026-06-05
draft: false
showReadingTime: false
layout: single
tags: ["raspberry-pi", "networking", "ssh", "jump-server", "opnsense", "route53"]
---

The homelab needed a permanent always-on entry point — something low power, always reachable, a stable first hop. A first-gen Raspberry Pi in the rack fills that role. BIFROST.

---

## Hardware

Raspberry Pi 1 Model B running Raspbian, mounted in the rack with a [3D printed 1U mount](/homelab/rack-3d-prints/). Draws under 2W at idle. Nothing runs on it except sshd.

---

## How it works

```
ssh -p 22222 user@bifrost.mjnet.info
```

The chain:

1. `bifrost.mjnet.info` — Route53 CNAME pointing to `router.mjnet.info`
2. `router.mjnet.info` — HEIMDAL (SYS-009), kept current via DDNS
3. OPNsense port forward: external TCP 22222 → Pi:22
4. OPNsense DNS override: `bifrost.mjnet.info` → Pi's internal IP

The DNS override means the same hostname resolves to the internal IP when used inside the network — no split config needed in `~/.ssh/config`.

---

## OPNsense config

**Port forward** (Firewall → NAT → Port Forward):
- Interface: WAN
- Protocol: TCP
- Destination port: 22222
- Redirect target: Pi internal IP, port 22

**DNS override** (Services → Unbound DNS → Host Overrides):
- Host: `bifrost`
- Domain: `mjnet.info`
- IP: Pi internal IP

---

## SSH config

Add to `~/.ssh/config` on any client:

```
Host bifrost
    HostName bifrost.mjnet.info
    Port 22222
    User pi
```

Then `ssh bifrost` from anywhere.

---

If a more robust solution becomes necessary later (no open ports, survives CGNAT), the [options doc](/homelab/bifrost-rpi-options/) covers Tailscale, Cloudflare Tunnel, and WireGuard.
