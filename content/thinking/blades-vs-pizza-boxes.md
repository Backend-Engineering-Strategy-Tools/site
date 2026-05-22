---
title: "Blades vs pizza boxes: when enclosure overhead kills the math"
description: "The C7000 enclosure costs 200–400W before a single blade boots. Here's when that's worth it and when it isn't."
date: 2026-05-20
draft: true
showReadingTime: false
layout: single
tags: ["homelab", "hardware", "power", "blades", "infrastructure"]
---

I'm setting up a blade cluster in the homelab — a HP C7000 enclosure with 16× BL460c Gen8 blades. Before committing to it as the permanent compute platform, I did the power math. The conclusion surprised me more than it should have.

The enclosure has fixed overhead regardless of population: 10 fans, dual Onboard Administrator modules, two interconnect switches, backplane management. That costs 200–400W before a single blade powers on. Add one blade and you're at 350–550W. Add three and you're at 500–800W.

Compare that to two 1U pizza boxes: an older M3-class rack server running Talos runs at 100–150W. A second node brings you to 200–300W total. You get two nodes for less than the cost of the enclosure alone.

The math only flips at scale. Once you're running 8+ blades simultaneously, the enclosure overhead amortises. At 16 populated slots doing real work, the per-node power cost is competitive. Below that threshold, you're paying enclosure tax for capacity you're not using.

---

**What this means in practice**

For a permanent always-on cluster, 1U rack servers beat blades below 8 nodes. The enclosure is overhead you can't shed.

For an experiment cluster — boot 8–16 nodes, run a Slurm job or OpenStack deployment, power it off — the blade system earns its place. The C7000 Onboard Administrator lets you configure boot order per slot, so switching roles (Kubernetes worker → Slurm compute → Ceph OSD) is a BIOS change and a PXE entry, not a reinstall. That operational flexibility has real value for a lab where you're testing multiple platforms.

So the split I landed on: pizza boxes for the permanent cluster (always on, predictable cost), blades for experiments (fire up, learn, power off). Two separate purposes, two separate platforms. Not consolidating them onto the blades until the blades are stable and trusted — in particular, the OPNsense router stays on its dedicated 1U box until then. You don't consolidate the thing that makes everything else reachable onto experimental infrastructure.

---

**The number that forced the decision**

200–400W idle for an empty enclosure. That's €20–40/month before a single workload runs, at Swedish electricity prices. The question "is it worth running the blades permanently?" became a lot easier to answer once that number was on paper.

Write it down. Obvious in hindsight, easy to skip in practice.
