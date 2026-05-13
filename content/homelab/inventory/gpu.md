---
title: "GPU Inventory"
date: 2026-05-13
draft: false
showReadingTime: false
layout: single
---

# GPU Catalog

| Component ID | Manufacturer | Model      | Quantity | VRAM | Interface | Notes                  |
|--------------|--------------|------------|----------|------|-----------|------------------------|
| GPU-001      | NVIDIA/Dell  | Quadro 600 | 3        | 1 GB | PCIe      |                        |
| GPU-002      | EVGA         | GTX 770    | 1        | 2 GB | PCIe      | Requires 6+8 pin power |

---

# GPU Placement

| Asset ID | Hostname | Component ID | Slot / Location | Role | Notes |
|----------|----------|--------------|-----------------|------|-------|

# GPU Overviews

Here are some brief overviews of the GPUs in the inventory, highlighting their typical uses and characteristics.

### NVIDIA Quadro 600 (e.g., GPU-001)
*96 CUDA cores · 1GB GDDR3 · low-profile · 40W TDP*

The NVIDIA Quadro 600 is an entry-level professional graphics card from the Fermi generation (circa 2010-2011). Designed primarily for CAD, DCC (Digital Content Creation), and basic scientific visualization, it is not optimized for gaming workloads. Equipped with 1GB of VRAM and typically presented in a low-profile form factor, these cards are well-suited for providing display output in servers that lack integrated graphics, or for light compute tasks that can utilize NVIDIA's CUDA architecture, though performance will be limited by their vintage.

### EVGA GTX 770 (e.g., GPU-002) — [NVIDIA specs](https://www.nvidia.com/en-us/geforce/graphics-cards/geforce-gtx-770/specifications/)
*1536 CUDA cores · 2GB GDDR5 256-bit · 3.2 TFLOPS · 230W TDP*

The NVIDIA GeForce GTX 770, frequently available in variants such as the EVGA GTX 770, was a high-end gaming graphics card released in 2013, based on the Kepler architecture. Featuring 2GB (or 4GB) of GDDR5 VRAM, it delivered strong performance for its release era. In a homelab setting, a GTX 770 can be repurposed for tasks like video transcoding, entry-level machine learning experiments, or providing robust graphical output for a dedicated workstation attached to a server. Its requirement for external power connectors (typically 6+8 pin) signifies its higher power consumption profile.