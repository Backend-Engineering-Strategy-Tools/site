---
title: "Controller Inventory"
date: 2026-05-13
draft: false
showReadingTime: false
layout: single
---

# Controller Catalog

| Component ID | Manufacturer | Model                         | Type | PCIe Slot   | Connectors         | Qty | IT Mode      | Notes                                                                                |
|--------------|--------------|-------------------------------|------|-------------|--------------------|-----|--------------|--------------------------------------------------------------------------------------|
| CTRL-001     | IBM / LSI    | ServeRAID MR10i               | RAID | PCIe x8     | 2× SFF-8087 (int.) | 1   | not possible | Cache module FRU 25R8079 attached; SAS1078 chip                                      |
| CTRL-002     | LSI          | 9211-8i                       | RAID | PCIe 2.0 x8 | 2× SFF-8087 (int.) | 1   | eligible     |                                                                                      |
| CTRL-003     | LSI          | 9211-8i                       | HBA  | PCIe 2.0 x8 | 2× SFF-8087 (int.) | 1   | ✓ flashed    | IT mode (passthrough)                                                                |
| CTRL-004     | Dell         | PERC H710                     | RAID | PCIe 2.0 x8 | 2× SFF-8087 (int.) | 1   | ? verify     | Hardware RAID, may already be flashed for HBA                                        |
| CTRL-005     | HP           | Smart Array P410              | RAID | PCIe 2.0 x8 | 2× SFF-8087 (int.) | 1   | not possible |                                                                                      |
| CTRL-006     | IBM / LSI    | ServeRAID-8e (FRU 39R8852)    | HBA  | PCIe 1.0 x8 | 2× SFF-8470 (ext.) | 2   | n/a          | External SAS; needs SFF-8470→SFF-8088 cable for MD1200                               |
| CTRL-007     | IBM / LSI    | SAS3082E-R (FRU 44E8690)      | HBA  | PCIe x8     | 2× SFF-8087 (int.) | 1   | n/a          | Internal SAS; 3Gb/s                                                                  |
| CTRL-008     | LSI          | MegaRAID SAS 8708EM2          | RAID | PCIe x8     | 2× SFF-8087 (int.) | 1   | not possible | iBBU06 attached                                                                      |
| CTRL-009     | IBM / LSI    | ServeRAID M1015 (FRU 46C8937) | RAID | PCIe 2.0 x8 | 2× SFF-8087 (int.) | 2   | ? verify     | LSI 9220-8i OEM; IT-flashable (same path as 9211-8i), may already be flashed for HBA |

---

# Controller Placement

| Asset ID | Hostname | Component ID    | Slot / Location | Role                  | Notes |
|----------|----------|-----------------|-----------------|-----------------------|-------|
| SYS-001  | FREJA    | CTRL-001        | Enclosure       | RAID controller       |       |
| SYS-002  | TYR      | CTRL-002        | Enclosure       | RAID controller       |       |
| SYS-003  | TOR      | CTRL-003        | Enclosure       | HBA passthrough       |       |
| SYS-004  | MD1200   | (no controller) | Enclosure       | Disk shelf controller |       |
| SYS-005  | ODEN     | CTRL-009        | Enclosure       | RAID controller       |       |
| SYS-006  | LOKE     | CTRL-009        | Enclosure       | RAID controller       |       |

---

# Controller Overviews

Here are some brief overviews of selected storage controllers, highlighting their typical uses and characteristics.

### LSI 9211-8i (e.g., CTRL-002, CTRL-003) — [IT mode flashing guide](https://www.stewright.me/tutorial-flash-lsi-9211-8i-with-it-firmware-for-truenas/)
*8-port SAS/SATA · 6Gb/s per port · PCIe 2.0 x8 · CTRL-003 flashed to IT (passthrough) mode*

The LSI SAS 9211-8i is a highly popular host bus adapter (HBA) in homelab and enthusiast communities. While capable of functioning as a basic RAID controller, it is most frequently flashed to "IT (Initiator Target) mode" to operate purely as an HBA. This passthrough mode is essential for software-defined storage solutions like ZFS (TrueNAS/OpenZFS) or unRAID, enabling the operating system to have direct control over individual drives.

### Dell PERC H710 (e.g., CTRL-004) — [spec sheet](https://www.dell.com/learn/us/en/04/shared-content~data-sheets/documents~dell-perc-h710-spec-sheet.pdf)
*8-port SAS/SATA · 6Gb/s · PCIe 2.0 · 512MB battery-backed cache · RAID 0/1/5/6/10/50/60*

The Dell PERC H710 is an enterprise-grade RAID controller commonly found in Dell PowerEdge servers. It supports a comprehensive range of RAID levels (0, 1, 5, 6, 10, 50, 60), providing robust data protection and optimized performance for server storage. These controllers typically incorporate battery-backed cache (BBWC) or flash-backed cache (FBWC) to enhance write performance and ensure data integrity during unexpected power events.

### HP Smart Array P410 (e.g., CTRL-005)
*8-port SAS · 3Gb/s · PCIe · RAID 0/1/5/10*

The HP Smart Array P410 is a legacy RAID controller designed for older generations of HPE ProLiant servers. It offered hardware RAID capabilities, supporting RAID levels 0, 1, 5, and 10. Although still functional, its performance and feature set are considered dated compared to contemporary controllers, making it suitable for less intensive storage tasks or environments requiring compatibility with older hardware.

### IBM ServeRAID-8e / LSI SAS3444E (CTRL-006 ×2)
*4-port external SAS · 3Gb/s · PCIe 1.0 x8 · 2× SFF-8470 (SAS-A, SAS-B)*

The ServeRAID-8e is an IBM OEM of the LSI SAS3444E, purpose-built for connecting external SAS enclosures and DAS units. Unlike the internal-only cards in this inventory, its SFF-8470 ports face the rear bracket, making it the right card to pull when you need to link a host to the MD1200. **Note:** the MD1200 uses SFF-8088 ports, so a SFF-8470 → SFF-8088 cable is required. Pull one of these when adding a host that needs direct DAS connectivity and lacks a native external SAS port.

### IBM/LSI SAS3082E-R (CTRL-007)
*8-port SAS/SATA · 3Gb/s · PCIe x8 · 2× SFF-8087 (int.)*

The SAS3082E-R is an IBM OEM internal SAS HBA providing eight SAS/SATA ports via two SFF-8087 connectors. Like the 9211-8i it operates as a passthrough HBA, making it suitable for ZFS/TrueNAS builds where the OS needs direct drive access. Pull this card when you need to expand internal port count in a host and the 9211-8i units are already allocated — the 3Gb/s bandwidth is the limiting factor versus the 9211-8i's 6Gb/s, so prefer the 9211-8i for performance-sensitive pools.

### LSI MegaRAID SAS 8708EM2 (CTRL-008) + iBBU06
*8-port SAS/SATA · 3Gb/s · PCIe x8 · 2× SFF-8087 (int.) · RAID 0/1/5/6/10/50/60 · battery-backed cache*

The MegaRAID SAS 8708EM2 is a hardware RAID controller with an iBBU06 battery backup unit attached, which protects the write cache during power loss. Pull this card when you need hardware RAID with a battery-backed cache — typically for workloads like virtual machine storage or databases where write performance and data integrity under power failure both matter. For ZFS or software-defined storage, prefer the 9211-8i or SAS3082E-R in HBA/passthrough mode instead, as hardware RAID sits between ZFS and the drives and undermines its integrity guarantees.
