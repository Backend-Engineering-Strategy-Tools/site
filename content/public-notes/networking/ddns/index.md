---
title: "Dynamic DNS (DDNS)"
description: "Keeping a hostname pointed at a dynamic IP — how DDNS works, provider options, and integration with OPNsense and Linux update clients."
date: 2026-05-22
draft: false
showReadingTime: false
layout: single
tags: ["networking", "ddns", "dns", "opnsense", "homelab"]
---

Most home internet connections have a dynamic IP — the ISP can reassign it at any time. Dynamic DNS (DDNS) keeps a DNS hostname pointed at whatever IP you currently have, by running a small client that detects changes and updates the DNS record automatically.

Relevant when using [port forwarding or WireGuard](/public-notes/networking/tunnels/) to reach a private network from outside — you need a stable hostname to connect to.

---

## How it works

1. You register a hostname with a DDNS provider (e.g. `myhome.duckdns.org`)
2. An update client runs on your router or a machine on your network
3. The client periodically checks your public IP (or watches for changes) and calls the provider's API to update the DNS record
4. DNS TTL is kept short (60–300s) so changes propagate quickly

---

## Providers

| Provider | Cost | Domain | Notes |
|----------|------|--------|-------|
| [DuckDNS](https://www.duckdns.org) | Free | `*.duckdns.org` | Simple, no account required beyond OAuth login |
| Cloudflare | Free (if you own a domain) | Your own domain | Best option if you already use Cloudflare for DNS |
| No-IP | Free (limited) | `*.ddns.net` etc. | Requires manual renewal every 30 days on free tier |
| Dynu | Free | `*.dynu.net` etc. | More generous free tier than No-IP |
| Afraid.org | Free | Shared subdomains | Long-running community service |

**Cloudflare** is the best option if you own a domain — you get a real subdomain (`home.yourdomain.com`), the API is reliable, and the client support is universal.

**DuckDNS** is the easiest if you don't own a domain — no configuration beyond a token.

---

## OPNsense

OPNsense has a built-in DDNS client under **Services → Dynamic DNS**. Supports Cloudflare, DuckDNS, No-IP, Route53, and others out of the box.

Configuration for Cloudflare:
- Service: `Cloudflare`
- Hostname: `home` (the subdomain to update)
- Domain: `yourdomain.com`
- Username: your Cloudflare account email
- Password: Cloudflare API token with `Zone:DNS:Edit` permission for the domain
- Check IP: leave default (uses OPNsense's WAN interface)

OPNsense updates the record whenever the WAN IP changes, detected via interface monitoring.

---

## Linux update clients

If the router doesn't have a built-in client (or you want updates from a specific host):

**ddclient** — the standard, supports most providers:

```bash
apt install ddclient

# /etc/ddclient.conf (Cloudflare example)
protocol=cloudflare
zone=yourdomain.com
login=your@email.com
password=<api-token>
ttl=1
home.yourdomain.com
```

**inadyn** — lighter alternative, similar provider support:

```bash
apt install inadyn

# /etc/inadyn.conf
provider cloudflare.com {
    username = your@email.com
    password = <api-token>
    hostname = home.yourdomain.com
    ttl = 1
    proxied = false
}
```

---

## Limitations

DDNS does not help if your ISP uses CGNAT — if your router's WAN IP is a private address (10.x, 100.64.x, 192.168.x), port forwarding and DDNS will not work. See [Tunnels](/public-notes/networking/tunnels/) for options that work without a public IP.

DNS propagation delay means there's a brief window after an IP change where connections will fail. Keep TTL at 60–300s to minimise this.
