---
title: "Disk Inventory"
date: 2026-05-13
draft: false
showReadingTime: false
layout: single
---

# Storage Media

| Component ID | Manufacturer    | Model                                                | Capacity | RPM      | Interface            | Quantity | Notes                                   |
|--------------|-----------------|------------------------------------------------------|----------|----------|----------------------|----------|-----------------------------------------|
| HDD-001      | IBM / Fujitsu   | MBB2073RC                                            | 73.4GB   | 10K RPM  | SAS 3Gbps            | 6        | 2.5" SFF; enterprise                    |
| HDD-002      | IBM / Seagate   | ST9146802SS (FRU 43X0825)                            | 146.8GB  | 10K RPM  | SAS 6Gbps            | 22       | 2.5" SFF hot-swap; IBM P/N 42D0248      |
| HDD-003      | Seagate         | Constellation ES.3 ST1000NM0043                      | 1TB      | 7200 RPM | SAS 6Gbps            | 20       |                                         |
| HDD-004      | Kingston        | SSDNow V300 SV300S37A/120G                           | 120GB    | —        | SATA                 | 7        | Consumer SSD; used as boot drives       |
| HDD-005      | Samsung         | 970 EVO                                              | 500GB    | —        | NVMe M.2 PCIe 3.0 x4 | 1        | In PCIe x16 riser (FRU 43V7066) in ODEN |
| HDD-006      | Western Digital | WD Blue WD10EZEX                                     | 1TB      | 7200 RPM | SATA 64MB cache      | 4        | Consumer-grade; mfg. 2015-11            |
| HDD-007      | Seagate         | ST500LM000                                           | 500GB    | 5400 RPM | SATA                 | 1        | SSHD; 8GB NAND cache; laptop-grade      |
| HDD-008      | Hitachi         | HTS542525K9SA00                                      | 250GB    | 5400 RPM | SATA                 | 1        | Laptop-grade                            |
| HDD-009      | Samsung         | HD300LD                                              | 300GB    | 7200 RPM | PATA (IDE)           | 1        | Desktop; 8MB cache; legacy interface    |
| HDD-010      | Seagate         | Barracuda 7200.7 ST380013AS                          | 80GB     | 7200 RPM | SATA                 | 1        | Desktop; legacy                         |
| HDD-011      | HP / Seagate    | EH0146FARWD (518216-002 / GPN 652599-002)            | 146GB    | 15K RPM  | SAS 6Gbps            | 3        | 2.5" SFF; enterprise; BL460c Gen8 pulls |
| HDD-012      | HP              | EG0300FBVFL (641552-001 / GPN 652566-001)            | 300GB    | 10K RPM  | SAS 6Gbps            | 15       | 2.5" SFF; enterprise; BL460c Gen8 pulls |
| HDD-013      | HGST            | Ultrastar C10K900 HUC109090CSS600 (EMC 118033034-02) | 900GB    | 10K RPM  | SAS 6Gbps            | 1        | 2.5" SFF; enterprise                    |
| HDD-014      | Toshiba         | AL13SEB900 (HDEBC00NAA51)                            | 900GB    | 10K RPM  | SAS 6Gbps            | 1        | 2.5" SFF; enterprise                    |

---

# Storage Assignments

| System ID | Hostname | Component ID | Quantity | Total Installed Storage | Notes         |
|-----------|----------|--------------|----------|-------------------------|---------------|
| SYS-001   | FREJA    | HDD-004      | 1        |                         | single drive  |
| SYS-002   | TYR      | HDD-002      | 8        |                         | raid 10       |
| SYS-003   | TOR      | HDD-002      | 8        |                         | HBA           |
| SYS-004   | MD1200   | HDD-003      | 15       | 15 TB                   | SAS HBA not installed; shelf unconnected |
| SYS-005   | ODEN     | HDD-004      | 4        | 480GB                   |               |
| SYS-005   | ODEN     | HDD-005      | 1        | 500GB                   | M.2 via riser |
| SYS-009   | HEIMDAL  | HDD-001      | 3        | 219GB                   |               |
| BLD-001   | BLADE-01 | HDD-011      | 2        | 292GB                   |               |
| BLD-003   | BLADE-03 | HDD-012      | 2        | 600GB                   |               |
| BLD-005   | BLADE-05 | HDD-011      | 1        | 146GB                   | mixed config  |
| BLD-005   | BLADE-05 | HDD-012      | 1        | 300GB                   | mixed config  |
| BLD-006   | BLADE-06 | HDD-012      | 2        | 600GB                   |               |
| BLD-007   | BLADE-07 | HDD-013      | 1        | 900GB                   | mixed config  |
| BLD-007   | BLADE-07 | HDD-014      | 1        | 900GB                   | mixed config  |
| BLD-008   | BLADE-08 | HDD-012      | 2        | 600GB                   |               |
| BLD-010   | BLADE-10 | HDD-012      | 2        | 600GB                   |               |
| BLD-011   | BLADE-11 | HDD-012      | 2        | 600GB                   |               |
| BLD-012   | BLADE-12 | HDD-012      | 2        | 600GB                   |               |
| BLD-015   | BLADE-15 | HDD-012      | 2        | 600GB                   |               |

---

# Storage Media Overviews

Here are some brief overviews of the storage media types in the inventory, highlighting their characteristics and typical applications.

### Enterprise SAS HDDs (e.g., HDD-001, HDD-002)
*73GB / 146GB · 7200 RPM · SAS 3Gbps · make/model unidentified*

These hard disk drives are engineered for high reliability and continuous operation within server environments. SAS (Serial Attached SCSI) interfaces provide superior performance, enhanced reliability, and enterprise-specific features compared to consumer-grade SATA drives. SAS HDDs of this generation (e.g., 73GB or 146GB at 7200 RPM with SAS 3Gbps) were common in servers from the late 2000s. Despite their modest capacities by today's standards, their robust construction and enterprise-grade design make them suitable for homelab applications where durability is prioritized, such as for boot drives or less critical data storage.

### Seagate Constellation ES.3 ST1000NM0043 (e.g., HDD-003) — [datasheet](https://www.seagate.com/www-content/product-content/constellation-fam/constellation-es/constellation-es-3/en-us/docs/constellation-es-3-data-sheet-ds1769-1-1210us.pdf)
*1TB · 7200 RPM · SAS 6Gbps · 128MB cache · 1.4M hr MTBF · AES-256 SED*

The Seagate Constellation ES.3 series represents enterprise-class hard drives designed for high-capacity, 24/7 operation in data centers. The ST1000NM0043 is a 1TB model, featuring a 7200 RPM spindle speed and a SAS 6Gbps interface. These drives offer an excellent balance of capacity, performance, and enterprise-level reliability, making them ideal for bulk storage in homelab NAS or storage arrays where data integrity and longevity are critical.

### Enterprise SSD (e.g., HDD-004)
*120GB · SATA/SAS · make/model unidentified*

Enterprise Solid State Drives (SSDs) are built to withstand demanding server workloads, providing significantly higher endurance, consistent performance, and often integrated power loss protection features that surpass those of consumer SSDs. A 120GB enterprise SSD, whether with a SATA or SAS interface, would typically be deployed as an operating system boot drive, for caching solutions, or for hosting small, performance-sensitive applications within a server environment. Their speed and inherent reliability, even with smaller capacities, can considerably enhance overall system responsiveness.