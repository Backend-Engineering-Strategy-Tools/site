---
title: "BIFROST — Raspberry Pi jump node"
description: "A Pi as a permanent low-power bridge into the homelab. Always on, always reachable — and the options for making that actually work from the outside."
date: 2026-05-22
draft: true
showReadingTime: false
layout: single
tags: ["raspberry-pi", "networking", "tailscale", "jump-server"]
---

The homelab has no permanent always-on node that costs nothing to run. HEIMDAL is the router, ODEN runs the Talos cluster — both are on continuously, but neither is a clean entry point for remote access. The plan is to add a Raspberry Pi in that role: always on, low power, reachable from outside, a stable first hop into everything else.

The name fits. BIFROST is the bridge.

---

## The problem with "just open a port"

The home IP is dynamic. The router does NAT. Depending on the ISP, there may not even be a real public IP at the WAN interface — carrier-grade NAT is common, and if that's what you're behind then port forwarding doesn't work regardless of what you do at the router.

Even if the IP is public and dynamic, you still need DDNS, a proper firewall rule, and an SSH-hardened surface exposed to the internet. That works, but it's the most fragile option.

The better alternatives don't require open ports at all.

---

## Options

### Tailscale (recommended starting point)

Install on the Pi, install on every device you want to reach the lab from. Tailscale builds a mesh VPN in the background — WireGuard underneath, coordinated by Tailscale's control plane. No port forwarding, no DDNS, works through NAT and CGNAT.

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

The Pi gets a stable hostname in the `*.ts.net` domain. Enable subnet routing and it becomes a gateway into the entire LAN — not just a jump box but a proxy for everything on the home network.

Free tier covers 100 devices, which is more than enough for a personal lab.

The dependency is real: Tailscale's coordination server has to be reachable for new connections to be negotiated. Established connections keep working, but it's worth knowing. For a homelab this is an acceptable tradeoff.

### Cloudflare Tunnel

The Pi maintains an outbound connection to Cloudflare's edge. No open ports. Cloudflare proxies SSH (or any service) through to the Pi via a domain you control.

Works without a public IP. Zero attack surface on the home network. The browser-based SSH terminal is a convenient fallback when you don't have a proper client available.

Requires a domain. Requires trusting Cloudflare as an intermediary for traffic. For SSH that means your session passes through their infrastructure — fine for most things, worth being aware of.

### WireGuard (self-hosted)

Run a WireGuard server on the Pi. Each remote device gets a WireGuard config. Traffic goes directly into the home network.

Full ownership, no third-party dependency, very fast. Requires a real public IP at the WAN and port forwarding on HEIMDAL. Also requires DDNS if the IP is dynamic.

If the ISP does CGNAT, this doesn't work without a relay.

### Port forwarding + DDNS (classic)

Open a port on HEIMDAL, point it at the Pi, use a DDNS service to track the dynamic IP. Conceptually simple, widely understood.

Exposes SSH directly to the internet. Needs hardening: key-only auth, fail2ban or equivalent, non-standard port. Higher maintenance surface than the alternatives.

---

## Summary

| Option | Open ports | Public IP required | Third-party | Complexity |
|--------|-----------|-------------------|-------------|------------|
| Tailscale | No | No | Yes (coord) | Low |
| Cloudflare Tunnel | No | No | Yes (traffic) | Low–Medium |
| WireGuard self-hosted | Yes (UDP) | Yes | No | Medium |
| Port forward + DDNS | Yes (TCP) | Yes | DDNS only | Low–Medium |

The CGNAT question decides a lot. If the ISP gives a real public IP, WireGuard is a clean long-term option. If not, Tailscale is the path of least resistance and the free tier is genuinely free.

Starting with Tailscale and migrating to WireGuard later if the dependency becomes a concern is a reasonable sequence.

---

## Hardware

A Pi 4 (2GB or 4GB) is the practical choice — USB boot from a small SSD is more reliable than SD card for a node that's supposed to be always on. A Pi 5 adds PCIe for an NVMe hat but is harder to find at a reasonable price.

Power draw at idle: ~2–4W. Meaningful compared to the rest of the rack.

---

## TODO

- Decide on Pi 4 vs Pi 5
- Confirm whether ISP does CGNAT (`curl ifconfig.me` on the Pi vs router's WAN IP — if they match, you have a real public IP)
- Install Tailscale, enable subnet routing for the LAN
- Register `bifrost.mjnet.info` in DNS pointing at the Tailscale IP
- Configure as an SSH ProxyJump target in local `~/.ssh/config`
- Firewall rule on HEIMDAL: allow inbound from Tailscale subnet only, no direct internet exposure
