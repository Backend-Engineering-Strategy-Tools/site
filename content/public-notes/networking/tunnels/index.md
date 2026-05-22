---
title: "Tunnels — remote network access"
description: "Options for reaching a private network from outside: Tailscale, WireGuard, Cloudflare Tunnel, and port forwarding with DDNS. Trade-offs by dependency, public IP requirement, and CGNAT behaviour."
date: 2026-05-22
draft: false
showReadingTime: false
layout: single
tags: ["networking", "tailscale", "wireguard", "cloudflare", "vpn", "tunneling"]
---

Approaches for accessing a private network (home lab, office) from outside, when you don't have a static public IP and may be behind NAT or CGNAT.

---

## First: check if you're behind CGNAT

Run on a device inside the network:

```bash
curl ifconfig.me
```

Compare the result to the WAN IP shown in your router. If they match — you have a real public IP (possibly dynamic). If they differ — you're behind CGNAT, and port forwarding will not work regardless of router config.

---

## Tailscale

WireGuard-based mesh VPN. Each device gets a node in a private overlay network coordinated by Tailscale's control plane. Connections are peer-to-peer where possible; relay servers (DERP) handle cases where direct traversal fails.

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

**Subnet routing**: one node (e.g. a Pi on the LAN) advertises the local subnet. Other Tailscale nodes route through it — the whole LAN becomes reachable, not just that one node.

```bash
sudo tailscale up --advertise-routes=192.168.1.0/24
```

**Exit node**: route all internet traffic through a Tailscale node — useful on untrusted networks.

| Property | |
|----------|-|
| Open ports required | No |
| Public IP required | No |
| Works through CGNAT | Yes |
| Third-party dependency | Yes (coordination server) |
| Free tier | 100 devices |
| Self-hostable | Yes — [Headscale](https://github.com/juanfont/headscale) |

The coordination server must be reachable to establish new connections. Existing sessions survive outages. Headscale replaces the coordination server while reusing the same clients.

---

## Cloudflare Tunnel

The device on your private network runs `cloudflared`, which holds an outbound connection to Cloudflare's edge. Cloudflare proxies inbound traffic through it. No open ports, no public IP needed.

Works for SSH, HTTP, and other TCP services. Native SSH support: access via `cloudflared access ssh` or a browser terminal.

```bash
cloudflared tunnel login
cloudflared tunnel create homelab
cloudflared tunnel route dns homelab ssh.yourdomain.com
cloudflared tunnel run homelab
```

| Property | |
|----------|-|
| Open ports required | No |
| Public IP required | No |
| Works through CGNAT | Yes |
| Third-party dependency | Yes — traffic passes through Cloudflare |
| Requires | Domain on Cloudflare |
| Cost | Free (Zero Trust free tier) |

Traffic passes through Cloudflare's infrastructure. For SSH this means an encrypted session transiting a third party's edge.

---

## WireGuard (self-hosted)

WireGuard server on a node in the private network. Remote clients connect with a config containing the server's public key and endpoint. Encrypted point-to-point, no intermediary.

Requires a real public IP at the WAN, UDP port forwarding on the router (default 51820), and DDNS if the IP is dynamic.

```ini
# /etc/wireguard/wg0.conf (server)
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = <server-private-key>

[Peer]
PublicKey = <client-public-key>
AllowedIPs = 10.0.0.2/32
```

| Property | |
|----------|-|
| Open ports required | Yes (UDP 51820) |
| Public IP required | Yes |
| Works through CGNAT | No |
| Third-party dependency | No |
| Complexity | Medium |

Full ownership, no external dependency, very fast. Key distribution is manual unless you layer a management tool on top (e.g. wg-easy, Netbird).

---

## Port forwarding + DDNS

Forward a port on the router to the target host. Use a DDNS provider (DuckDNS, Cloudflare, etc.) to keep a hostname pointed at the dynamic IP.

Exposes a service directly to the internet. Minimum hardening for SSH:

- Key-only auth (`PasswordAuthentication no`)
- Non-standard port
- fail2ban or equivalent
- Regular review of auth logs

| Property | |
|----------|-|
| Open ports required | Yes (TCP) |
| Public IP required | Yes |
| Works through CGNAT | No |
| Third-party dependency | DDNS provider only |
| Complexity | Low–Medium |

---

## Comparison

| | Tailscale | Cloudflare Tunnel | WireGuard | Port forward |
|---|---|---|---|---|
| Open ports | No | No | Yes | Yes |
| Public IP | No | No | Yes | Yes |
| CGNAT | Works | Works | Fails | Fails |
| Traffic via third party | Metadata only | Yes | No | No |
| Self-hostable | Yes (Headscale) | No | Yes | Yes |
| Complexity | Low | Low–Med | Medium | Low–Med |

---

## Which to use

Start with **Tailscale** if you want the least friction and aren't sure whether you're behind CGNAT. Subnet routing covers the entire LAN through a single node.

Use **Cloudflare Tunnel** if you have a domain on Cloudflare and want browser-accessible SSH or HTTP without client software.

Use **WireGuard** if you have a confirmed public IP and want no third-party in the data path.

Use **port forwarding** only if you already have DDNS working and want no new software — it has the highest hardening overhead.

---

## Related

- For a hardened SSH entry point → [Bastion / jump server](/public-notes/networking/bastion/)
- For exposing internal web services via public URLs → [Tunneled reverse proxy platforms](/public-notes/networking/tunneled-reverse-proxy/)
