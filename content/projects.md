---
title: "Projects"
date: 2026-03-16
draft: false
showReadingTime: false
---

The [GitHub org](https://github.com/Backend-Engineering-Strategy-Tools) is a curated space — a cleaner surface over a longer personal GitHub history. Work in progress, professional tools, and side projects worth sharing.

---

## Touchscreen HUD Build

A small batch of fanless Atom-based machines with touchscreens — picked up as a hardware experiment, now being packaged up to hand out to colleagues at nerd night.

The goal: a fully reproducible setup. Boot from a Debian preseed image, drivers configured, sensible defaults in place, and a demo running out of the box. Each machine goes out with a link back to the repo so anyone who wants to dig in or rebuild from scratch can do so.

**Repos**

- [touchdemo](https://github.com/Backend-Engineering-Strategy-Tools/touchdemo) — demo application running on the devices *(work in progress)*
- [debian-preseed-demo](https://github.com/Backend-Engineering-Strategy-Tools/debian-preseed-demo) — automated Debian install via preseed *(in progress)*

**Still to figure out**

- Power adapter specs and sourcing
- Preseed configuration — touch input, display drivers, auto-login
- First-boot experience and documentation

---

## Kubernetes Across the Stack *(draft)*

A documented comparison of running Kubernetes across every major hosting model — cloud managed, self-managed on cloud, private cloud, and bare metal at home. The goal is a honest, practical reference for each environment: what it costs you in time and money, where the rough edges are, and how the networking story differs between them.

The thread running through all of it is [Talos Linux](https://www.talos.dev/) — an immutable, API-driven OS built specifically for Kubernetes. No SSH, no shell, no config drift. The same OS everywhere means the operational model stays consistent regardless of what is running underneath.

| Environment                               | Approach                                      |              |
|-------------------------------------------|-----------------------------------------------|--------------|
| OpenStack — [Cleura](https://cleura.com/) | Talos & Terraform                             | draft exists |
| OpenStack — [Cleura](https://cleura.com/) | Talos, with Omni                              | maybe ?      |
| OpenStack — [ElastX](https://elastx.se/)  | Talos & Terraform                             | draft exists |
| OpenStack — [ElastX](https://elastx.se/)  | Talos, with Omni                              | maybe ?      |
| Homelab — bare metal                      | Talos + Pixieboot + Omni                      | draft exists |
| Homelab — bare metal                      | Talos + Pixieboot without Omni                | maybe ?      |
| Homelab — OpenStack                       | OpenStack on bare metal, Talos running on top | *(stretch)*  |
| Homelab — OpenStack                       | Talos on bare metal, OpenStack inside cluster | *(stretch)*  |
| AWS                                       | Talos on EC2                                  | *(stretch)*  |
| Azure                                      | Talos on VMs                                  | *(stretch)*  |
| GCP                                        | Talos on Compute Engine                       | *(stretch)*  |

**Stretch goals**

AWS, Azure, GCP — same Talos approach, different underlying infrastructure. Interesting eventually, but not the priority.

**Omni**

[Omni](https://omni.siderolabs.com/) is Sidero's managed control plane for Talos clusters — worth documenting both with and without it. Without Omni gives you the full picture of what Talos management looks like manually; with Omni shows what the managed layer buys you.

**Homelab provisioning**

Nodes provisioned via Pixieboot — no USB sticks, no manual installations. A node powers on, boots from the network, and registers. The goal is a fully reproducible cluster from scratch with minimal human steps.

**Scope**

- Cluster provisioning and bootstrap for each environment
- Networking — CNI choices, ingress, cross-cluster connectivity
- Storage — what you get managed vs what you have to bring yourself
- Operational differences — upgrades, node management, observability
- Cost and trade-off summary across environments

**Making it usable**

Getting a cluster running is the easy part. Making it usable is where environments diverge. Each environment needs an answer for ingress, DNS, and storage — and the answer varies significantly depending on what the underlying platform provides.

On managed cloud you can lean on load balancers and block storage from the provider. On OpenStack you have those options if the provider exposes them. On bare metal at home you are on your own — MetalLB or similar for load balancer IPs, a local DNS solution, and either local storage or something like Rook/Ceph. Same Kubernetes, very different operational story underneath.

*Notes exist in various states — pulling them together, testing, and documenting properly is the work.*

---

## Minecraft Server *(draft)*

Building and running a Minecraft server with the kids — hosted in the [homelab](/homelab/) on bare metal rather than paying for a managed service. Part infrastructure project, part excuse to learn together.

The longer-term goal is a proper setup: automated backups, world persistence across restarts, maybe some automation around starting and stopping the server on demand.

*Notes and repo to follow.*

---

*More to come.*
