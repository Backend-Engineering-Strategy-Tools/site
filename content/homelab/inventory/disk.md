---
title: "Disk Inventory"
date: 2026-05-13
draft: false
showReadingTime: false
layout: single
---

# Storage Media

| Component ID | Manufacturer | Model                           | Capacity | RPM      | Interface | Quantity | Notes |
|--------------|--------------|---------------------------------|----------|----------|-----------|----------|-------|
| HDD-001      | Unknown      | Enterprise SAS HDD              | 73GB     | 7200 RPM | SAS 3Gbps | 6        | (?)   |
| HDD-002      | Unknown      | Enterprise SAS HDD              | 146GB    | 7200 RPM | SAS 3Gbps | 22       | (?)   |
| HDD-003      | Seagate      | Constellation ES.3 ST1000NM0043 | 1TB      | 7200 RPM | SAS 6Gbps | 20       | (?)   |
| HDD-004      | Unknown      | Enterprise SSD                  | 120GB    | —        | SATA/SAS  | 6        | (?)   |

---

# Storage Assignments

| System ID | Hostname | Component ID | Quantity | Total Installed Storage | Notes        |
|-----------|----------|--------------|----------|-------------------------|--------------|
| SYS-001   | FREJA    | HDD-004      | 1        |                         | single drive |
| SYS-002   | TYR      | HDD-002      | 8        |                         | raid 10      |
| SYS-003   | TOR      | HDD-002      | 8        |                         | HBA          |
| SYS-004   | MD1200   | HDD-003      | 15       | 15 TB                   |              |

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