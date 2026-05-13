---
title: "Controller Inventory"
date: 2026-05-13
draft: false
showReadingTime: false
layout: single
---

# Controller Catalog

| Component ID | Manufacturer | Model            | Type | Interface | Notes                 |
|--------------|--------------|------------------|------|-----------|-----------------------|
| CTRL-001     | LSI          | ???              | RAID | PCIe      | Hardware RAID         |
| CTRL-002     | LSI          | 9211-8i          | RAID | PCIe      | Hardware RAID         |
| CTRL-003     | LSI          | 9211-8i          | HBA  | PCIe      | IT mode (passthrough) |
| CTRL-004     | Dell         | PERC H710        | RAID | PCIe      | Hardware RAID         |
| CTRL-005     | HP           | Smart Array P410 | RAID | PCIe      | Legacy controller     |

---

# Controller Placement

| Asset ID | Hostname | Component ID    | Slot / Location | Role                  | Notes |
|----------|----------|-----------------|-----------------|-----------------------|-------|
| SYS-001  | FREJA    | CTRL-001        | Enclosure       | RAID controller       |       |
| SYS-002  | TYR      | CTRL-002        | Enclosure       | RAID controller       |       |
| SYS-003  | TOR      | CTRL-003        | Enclosure       | HBA passthrough       |       |
| SYS-004  | MD1200   | (no controller) | Enclosure       | Disk shelf controller |       |

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

The HP Smart Array P410 is a legacy RAID controller designed for older generations of HP ProLiant servers. It offered hardware RAID capabilities, supporting RAID levels 0, 1, 5, and 10. Although still functional, its performance and feature set are considered dated compared to contemporary controllers, making it suitable for less intensive storage tasks or environments requiring compatibility with older hardware.
