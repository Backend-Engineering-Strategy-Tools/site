---
title: "Bastion / jump server"
description: "Using a Linux machine as a hardened entry point into a private network — SSH jump hosts, ProxyJump, agent forwarding, and hardening basics."
date: 2026-05-22
draft: false
showReadingTime: false
layout: single
tags: ["ssh", "bastion", "jump-server", "networking", "security"]
---

A bastion host (jump server) is a single, hardened machine exposed to the outside that acts as the entry point into a private network. You SSH into the bastion, then hop from there to internal hosts — or configure your SSH client to do it transparently in one step.

The pattern is simple: minimise the network attack surface to one well-monitored machine, harden that machine specifically, and keep everything else off the public internet.

---

## Basic jump: manual two-hop

```bash
# Step 1: SSH into the bastion
ssh user@bastion.example.com

# Step 2: from bastion, SSH into internal host
ssh user@192.168.1.100
```

Works, but requires your private key to be on the bastion — which you want to avoid.

---

## ProxyJump (recommended)

`ProxyJump` tells SSH to tunnel through the bastion transparently. Your key never leaves your local machine.

```bash
# One-liner
ssh -J user@bastion.example.com user@192.168.1.100

# Or in ~/.ssh/config
Host internal
    HostName 192.168.1.100
    User user
    ProxyJump bastion

Host bastion
    HostName bastion.example.com
    User user
    IdentityFile ~/.ssh/id_ed25519
```

After this, `ssh internal` works as a single command with no key on the bastion.

---

## Agent forwarding vs ProxyJump

**Agent forwarding** (`-A`, `ForwardAgent yes`) forwards your SSH agent socket through the bastion so you can authenticate onward with your local key. Older approach — it works but the agent socket is briefly accessible on the bastion host, which is a lateral movement risk if the bastion is compromised.

**ProxyJump** is strictly better for the common case: the connection to the internal host is established from your machine through an SSH tunnel, not from the bastion itself. No agent socket on the bastion.

Use ProxyJump unless you specifically need agent forwarding for something else.

---

## Hardening basics

A bastion is only useful if it's actually hardened. Minimum:

```bash
# /etc/ssh/sshd_config
PasswordAuthentication no
PermitRootLogin no
AuthorizedKeysFile .ssh/authorized_keys
AllowUsers jumpuser
```

- Key-only authentication — no passwords
- Dedicated user with no shell access to the bastion itself (optional: `ForceCommand` to restrict what they can do)
- Non-standard port reduces log noise, not actual security
- fail2ban or equivalent for rate-limiting auth attempts
- Minimal installed software — the bastion should do one thing
- Regular log review (`/var/log/auth.log`)

---

## Restricting to jump-only

If you want users to be able to jump through the bastion but not get a shell on it:

```bash
# In authorized_keys, prefix the key with:
restrict,port-forwarding ssh-ed25519 AAAA...
```

Or use `AllowTcpForwarding yes` with `ForceCommand /usr/sbin/nologin` — though the interaction between these options is subtle; test carefully.

---

## Related

- For making the bastion reachable from outside without a public IP → [Tunnels](/public-notes/networking/tunnels/)
- For exposing internal web services via public URLs → [Tunneled reverse proxy platforms](/public-notes/networking/tunneled-reverse-proxy/)
