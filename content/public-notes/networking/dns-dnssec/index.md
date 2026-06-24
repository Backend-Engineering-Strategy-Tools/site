---
title: "DNS & DNSSEC"
description: "DNS fundamentals and DNSSEC chain of trust — record types, zones, delegation, signing keys, and how the chain of trust is established."
date: 2026-06-22
draft: false
showReadingTime: false
layout: single
tags: ["dns", "dnssec", "networking"]
---

DNS maps names to addresses. DNSSEC adds a chain of cryptographic signatures so resolvers can verify that responses haven't been tampered with.

---

## DNS fundamentals

### Record types

| Type | Purpose |
|------|---------|
| `A` | Maps a name to an IPv4 address |
| `AAAA` | Maps a name to an IPv6 address |
| `CNAME` | Alias — maps a name to another name (cannot be used at the zone apex) |
| `NS` | Name servers authoritative for the zone |
| `SOA` | Zone metadata — primary NS, email, serial, TTL values |
| `TXT` | Arbitrary text — used for domain verification, SPF, DKIM |
| `MX` | Mail server for the domain |
| `DS` | Delegation Signer — links a child zone's DNSSEC keys to the parent zone |
| `DNSKEY` | Public keys used for DNSSEC signing in the zone |

### Zones and delegation

A DNS zone is the authoritative data for a domain. When you register a domain, the TLD zone (`.com`, `.org`, etc.) gets an `NS` record pointing to your name servers. From that point your name servers are authoritative for the domain — they answer queries for anything in that zone.

Subdomains can be delegated: adding `NS` records for `sub.example.com` pointing at different name servers creates a child zone, and queries for that subtree are delegated to those servers.

### TTL and propagation

Every record has a TTL (seconds). Resolvers cache responses for the TTL duration. A change to a DNS record takes up to the previous TTL to propagate globally — resolvers keep serving the cached old value until it expires.

Keep TTL low (60–300s) before making changes. Once stable, raise it (3600+) to reduce resolver load and query cost.

---

## DNSSEC

### Chain of trust

DNSSEC establishes a chain of cryptographic signatures from the DNS root down to your zone:

```
Root zone (.)
    |  DS record for .org
    ↓
.org TLD zone
    |  DS record for example.org
    ↓
example.org zone
    |  DNSKEY + RRSIG on every response
    ↓
Validated response
```

Each level signs the public key of the level below it. A resolver that trusts the root's public key (distributed as a built-in trust anchor) can validate any signed zone by following the chain.

### Key types

**KSK (Key Signing Key)** — signs the `DNSKEY` record set itself. The KSK's fingerprint is what goes into the DS record in the parent zone. Typically backed by an HSM or cloud KMS; rotated infrequently.

**ZSK (Zone Signing Key)** — signs all other records in the zone (A, AAAA, MX, etc.). Rotated more frequently than the KSK. Most managed DNS providers handle ZSK rotation automatically.

### Record types added by DNSSEC

| Type | Purpose |
|------|---------|
| `DNSKEY` | Public signing keys for the zone (KSK and ZSK) |
| `RRSIG` | Signature over a record set — proves it was signed by the zone's key |
| `DS` | Hash of the child zone's KSK — goes in the parent zone |
| `NSEC` / `NSEC3` | Authenticated denial of existence — proves a name doesn't exist |

### Enabling DNSSEC on a zone

General flow, regardless of provider:

1. **Generate KSK** — DNS provider creates the key pair, typically backed by HSM or cloud KMS
2. **Zone signing begins** — provider adds `DNSKEY` and `RRSIG` records; all responses are now signed
3. **Get the DS record** — provider gives you the DS data (key tag, algorithm, digest type, digest)
4. **Submit DS to the parent** — add it at your registrar; registrar submits to the TLD registry
5. **Wait for propagation** — DS changes at the registry take minutes to hours; the chain is live once the TLD sees the DS record

If registrar and DNS provider are the same service, steps 3–4 stay within one console.

### Validation

```bash
# Check DNSKEY records are present
dig example.com DNSKEY

# Check DS record is visible at the TLD
dig example.com DS @a.gtld-servers.net

# Full chain validation — look for AD (Authenticated Data) flag
dig +dnssec example.com A
```

Online tools: [dnssec-analyzer.verisignlabs.com](https://dnssec-analyzer.verisignlabs.com), [dnsviz.net](https://dnsviz.net)

---

## Related

- [mjli.org — DNS & DNSSEC Lab](/projects/mjli-org/) — working through this in practice on AWS with Route 53
- [Dynamic DNS (DDNS)](/public-notes/networking/ddns/) — keeping a hostname pointed at a dynamic IP
- [BGP](/public-notes/networking/bgp/) — routing context for how DNS fits into the broader network stack
