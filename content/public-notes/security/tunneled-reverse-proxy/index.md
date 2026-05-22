---
title: "Tunneled reverse proxy platforms"
description: "Platforms that expose private services as public HTTPS URLs through an outbound tunnel — Pangolin, ngrok, frp, and Expose. More than a tunnel: you get public links, routing, and often auth."
date: 2026-05-22
draft: false
showReadingTime: false
layout: single
tags: ["networking", "pangolin", "ngrok", "frp", "reverse-proxy", "tunneling"]
---

A step beyond raw tunnels. These platforms expose services running on a private network as public HTTPS URLs — no open ports, no public IP required. The key difference from a VPN: you don't get network-level access to the remote machine, you get a link to a specific service.

Typical flow:

```
Internet → public server (VPS) → tunnel → private network → your service
```

The private machine maintains an outbound connection to the public server. Inbound traffic arrives at the public server and is forwarded back through the tunnel to the service.

---

## Pangolin

Self-hosted platform built specifically for this use case. You run the server component on a VPS; client agents (called Newt) run on machines inside your private network and establish outbound tunnels. Services get public HTTPS URLs. Access control is built in — you can gate services behind auth without touching the service itself.

**Components**:
- **Pangolin** — the server, runs on a VPS, handles routing and auth
- **Newt** — the tunnel client, runs on private machines, connects out to Pangolin
- **Gerbil** — WireGuard-based tunnel layer (handled automatically)
- **Traefik** — reverse proxy, managed by Pangolin for routing

```bash
# On the VPS (docker-compose)
# Pangolin + Traefik + Gerbil run together

# On a private machine
docker run -e SERVER_URL=https://pangolin.yourdomain.com \
           -e TUNNEL_SECRET=... \
           fosrl/newt
```

Services then appear at subdomains: `service.yourdomain.com` — proxied through the tunnel, with optional SSO/auth in front.

| Property | |
|----------|-|
| Self-hosted | Yes — you own the VPS and the data |
| Open ports on private network | No |
| Public IP required | VPS only (not home) |
| Auth built in | Yes |
| Cost | Free, open source |
| Maturity | Newer project (2024–) |

Good fit for homelabs where you want public-facing services but don't want to expose your home IP or open ports on your router.

---

## ngrok

The original in this space. Run a single command, get a public URL. No server to manage — ngrok's infrastructure handles it.

```bash
ngrok http 8080
# → https://abc123.ngrok.io
```

The URL changes on every restart unless you're on a paid tier. Custom domains, persistent tunnels, and traffic inspection (useful for debugging webhooks) are paid features.

| Property | |
|----------|-|
| Self-hosted | No |
| Open ports on private network | No |
| Auth built in | Yes (paid) |
| Cost | Free tier limited; paid for custom domains |
| Maturity | Established, widely used |

Best for: quick testing, webhook development, demos. Not ideal for a permanent homelab setup due to the dependency and cost at scale.

---

## frp (Fast Reverse Proxy)

Lightweight, self-hosted. You run `frps` (server) on a VPS and `frpc` (client) on private machines. More DIY than Pangolin — you configure the routing yourself, no built-in auth or dashboard.

```ini
# frps.toml (on VPS)
bindPort = 7000

# frpc.toml (on private machine)
serverAddr = "your-vps-ip"
serverPort = 7000

[[proxies]]
name = "my-service"
type = "http"
localPort = 8080
customDomains = ["service.yourdomain.com"]
```

| Property | |
|----------|-|
| Self-hosted | Yes |
| Open ports on private network | No |
| Auth built in | Basic (token auth between client/server) |
| Cost | Free, open source |
| Maturity | Established, widely used in homelab |

Good fit if you want full control and are comfortable wiring things together. No UI — config files only.

---

## Expose (BeyondCode)

PHP-based self-hosted ngrok alternative. Dashboard included, custom domains, multiple tunnels.

```bash
expose share http://localhost:8080
```

Less common than frp or Pangolin, but polished for a self-hosted tool.

---

## Comparison

| | Pangolin | ngrok | frp | Expose |
|---|---|---|---|---|
| Self-hosted | Yes | No | Yes | Yes |
| Auth / access control | Yes (built-in) | Paid | No (DIY) | Basic |
| Dashboard | Yes | Yes | No | Yes |
| Custom domains | Yes | Paid | Yes | Yes |
| Complexity | Medium | Low | Medium | Medium |
| Maturity | Newer | Established | Established | Moderate |

---

## When to use which

**Pangolin** if you want a self-hosted, permanent setup with auth and public URLs for homelab services. The right choice if you're already running a VPS.

**ngrok** for quick tests, webhook development, or one-off sharing. Not for permanent services.

**frp** if you want maximum control and minimal overhead, and are comfortable configuring a reverse proxy separately.

---

## Related

- For network-level access (not service URLs) → [Tunnels](/public-notes/security/tunnels/)
- For SSH entry points → [Bastion / jump server](/public-notes/security/bastion/)
