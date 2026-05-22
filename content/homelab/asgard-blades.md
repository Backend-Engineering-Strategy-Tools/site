---
title: "ASGARD — the blade cluster"
description: "16× BL460c Gen8 blades in a C7000 as a reprovisionable compute pool — power trade-offs, role profiles, and what to kit them with from existing stock."
date: 2026-05-15
draft: false
showReadingTime: false
layout: single
tags: ["blades", "talos", "slurm", "openstack", "kubernetes", "bare-metal"]
---

[ASGARD (SYS-007)](/homelab/inventory/systems/) is the HP BladeSystem C7000 with 16× BL460c Gen8 blades. The reason to use it is profile switching: boot a blade as a Slurm compute node, run the experiment, reimage it as a Talos worker, run the next one. The same iPXE boot menu already set up for [ODEN](/homelab/talos-omni/) works here — the C7000 Onboard Administrator lets you configure boot order per blade slot, so switching roles is a BIOS setting and a PXE entry, not a reinstall.

---

## Power reality

Before committing to blades as the permanent always-on platform, it's worth being honest about the enclosure overhead. The C7000 has fixed costs regardless of how many blades are populated: 10 fans, dual OA modules, 2 interconnect switches, backplane management. It doesn't scale down gracefully.

| Setup | Approx power |
|-------|-------------|
| C7000 enclosure alone (no blades) | 200–400W |
| C7000 + 1 blade | 350–550W |
| C7000 + 3 blades | 500–800W |
| ODEN alone (1U M3, Talos) | 100–150W |
| HEIMDAL alone (Sun X4150, router) | 150–200W |
| ODEN + HEIMDAL | 250–350W |

Two pizza boxes beat three blades in the enclosure on power. The overhead only amortises at 8+ populated slots. For a permanent minimal setup, the 1U rack servers win. For experiments where you want to run 8–16 nodes at once, ASGARD earns its place.

---

## What each role actually needs

| Role | RAM | Disk | Network | Limiting factor |
|------|-----|------|---------|-----------------|
| Talos / K8s worker | 32–64GB | 1× OSD disk | 1GbE fine | RAM — current blades too thin |
| OpenStack compute | 32–64GB | local ephemeral | 1GbE fine | RAM |
| OpenStack control | 32GB+ | small | 1GbE fine | RAM |
| Slurm compute | as much as possible | fast scratch | 1GbE mediocre | network |
| Ceph OSD | 16–32GB | more / bigger disks | 1GbE | disk count |

The network note matters for Slurm: blade LOM connects to the enclosure switch backplane at **1GbE**, not 10GbE. The switch has 10GbE uplinks going out, but blade-to-blade traffic inside the enclosure goes through the switch at 1GbE. For Talos and OpenStack this is fine. For MPI jobs exchanging large datasets between Slurm nodes it's a real bottleneck — HPC wants InfiniBand, which the empty interconnect bays 5–8 could take (plus matching mezzanine cards in each blade), but that's a separate cost. For learning Slurm, 1GbE is workable.

---

## Current blade state

Most blades are underpowered for any of the roles above. CPUs are also unknown across all 16 slots — the OA web GUI reports CPU model and core count per blade and should be checked first. The E5-2600 v1 range runs from E5-2603 (4c, 80W) to E5-2690 (8c/16t, 135W), which matters significantly for role assignment.

| Slot | RAM | Disk |
|------|-----|------|
| BLD-001 | 4GB | 2× 146GB SAS |
| BLD-002 | 14GB (mixed, odd count) | — |
| BLD-003 | 32GB | 2× 300GB SAS |
| BLD-004 | 8GB | — |
| BLD-005 | 8GB | 1× 146GB + 1× 300GB SAS |
| BLD-006 | 8GB | 2× 300GB SAS |
| BLD-007 | 8GB | 2× 900GB SAS |
| BLD-008 | 16GB | 2× 300GB SAS |
| BLD-009 | 8GB | — |
| BLD-010 | 8GB | 2× 300GB SAS |
| BLD-011 | 8GB | 2× 300GB SAS |
| BLD-012 | 8GB | 2× 300GB SAS |
| BLD-013 | 32GB | — |
| BLD-014 | 8GB | — |
| BLD-015 | 8GB | 2× 300GB SAS |
| BLD-016 | 8GB | — |

BLD-003 and BLD-013 are already at 32GB and are natural candidates for control-plane or master roles once CPUs are confirmed.

---

## Suggested configuration from existing stock

Available spare hardware:
- 14× RAM-007 (8GB DDR3 1600MHz ECC Reg) — unassigned
- 2× HDD-004 (120GB SATA SSD) — spare
- 6× HDD-002 (146GB 10K SAS) — spare
- Embedded P220i on each blade (can be set to JBOD/passthrough for Ceph)

**"Fat" nodes × 2** — Talos control plane, OpenStack control, Slurm master:
Add 4× RAM-007 to each blade. From a base of 8–16GB that gives ~40GB. Candidates: BLD-006 and BLD-010, both have 2× 300GB SAS for local storage. Costs 8 of 14 spare sticks. Install a spare 120GB SSD as boot disk in each.

**"Medium" nodes × 3** — Talos workers, OpenStack compute, Slurm compute:
Add 2× RAM-007 to each → 24GB from the 8GB base. Candidates: BLD-008 (already 16GB, gets to 32GB), BLD-011, BLD-012. All three have 300GB SAS for scratch or Ceph OSDs. Costs the remaining 6 spare sticks.

**Rest** — thin compute, storage expansion, or powered off:
Leave at current RAM. BLD-007's 900GB SAS pair is better used elsewhere (see below). BLD-003 and BLD-013 at 32GB can step up to fat-node role once CPUs are confirmed.

That leaves 5 blades properly kitted and 11 available for experiments or idle.

BL460c Gen8 DIMM rule: populate per-CPU symmetrically — pairs or quads per memory channel — for best throughput. Don't mix odd counts.

---

## Storage — what moves where

**Pull the 900GB SAS drives from BLD-007 now.** HDD-013 (HGST 900GB) and HDD-014 (Toshiba 900GB) are the two largest drives in the blade pool and they're sitting in a blade that may end up as a thin compute worker. Move them into ODEN or LOKE as permanent Ceph OSDs. This immediately gives the always-on cluster substantially more storage than the current 120GB SSDs.

**MIMIR** (SYS-004, 15× 1TB SAS) is the Ceph expansion story for later. To connect it: install CTRL-006 (ServeRAID-8e, have 2 unplaced) into a server with a free PCIe slot, then cable it with a SFF-8470 → SFF-8088 cable (not currently owned, inexpensive). TOR is the natural host — it already has CTRL-003 in HBA mode and free PCIe slots. Not urgent, but the hardware is almost all there.

| What | Goes to | When |
|------|---------|------|
| 900GB SAS ×2 from BLD-007 | ODEN or LOKE, permanent Ceph OSDs | Now |
| 120GB SSD ×2 spare | BLD fat node boot disks | Before Talos on blades |
| 300GB SAS in blades | Local scratch or blade Ceph OSDs | During ASGARD experiments |
| MIMIR 15× 1TB SAS | TOR via CTRL-006, Ceph expansion | Later (needs cable) |

---

## Three things to do before blades can boot anything

1. **Identify CPUs.** Connect to the OA management port, open the web GUI, check CPU model per slot. Ten minutes. Everything else depends on this.

2. **Network uplink.** The blade switches in bays 1 and 2 have 4× RJ45 1GbE uplinks (ports 22–25). Run a patch cable from one to any available switch — MODI, MAGNI, whatever's reachable from the cable box. That's enough for blades to reach DHCP and iPXE.

3. **RAM redistribution.** Pull the 14 spare RAM-007 sticks and install into the chosen fat and medium nodes per the profile above.

---

## The permanent vs experiment split

```
Always on (~300–400W total):
  HEIMDAL      → OPNsense router, Sun X4150, ~150–200W
  ODEN         → Talos, Minecraft + small services, ~100–150W
  LOKE         → 2nd Talos node (needs RAM-007 × 8 + SSD boot), ~100–150W

Experiments (fire up, learn, power off):
  ASGARD       → 3–16 blades for Slurm / OpenStack / larger Talos cluster
  TYR+TOR+FREJA → Proxmox cluster (M1 DDR2, temporary)
```

Once the Proxmox experiment wraps, TYR, TOR, and FREJA can be powered down permanently. If ASGARD blades eventually become the long-term compute platform, OPNsense can move to a VM on a blade at that point — but not before the blades are stable and trusted. Don't consolidate the router onto experimental infrastructure.
