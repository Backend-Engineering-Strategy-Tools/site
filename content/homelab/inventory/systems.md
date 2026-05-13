---
title: "System Inventory"
date: 2026-05-13
draft: false
showReadingTime: false
layout: single
---

# Systems

| Asset ID | Hostname    | Manufacturer | Model                  | Form Factor | Notes                          |
|----------|-------------|--------------|------------------------|-------------|--------------------------------|
| SYS-001  | FREJA       | IBM          | System x3550 Type 7978 | 1U          | Rack server (S/N: KDHPPNN)     |
| SYS-002  | TYR         | IBM          | System x3650 Type 7979 | 2U          | Rack server                    |
| SYS-003  | TOR         | IBM          | System x3650 Type 7979 | 2U          | Rack server                    |
| SYS-004  | MIMIR       | Dell         | PowerVault MD1200      | 2U          | Disk shelf                     |
| SYS-005  | ODEN        | IBM          | System x3650 Type 7979 | 2U          | Rack server                    |
| SYS-006  | HEIMDAL     | IBM          | System x3650 Type 7979 | 2U          | Rack server                    |
| SYS-007  | ASGARD      | HP           | BladeSystem C7000      | 10U         | Blade enclosure (Hosts 1-16)   |
| SYS-008  | BALDER      | HP           | ProLiant DL320 G5p     | 1U          | Dual 250GB SATA                |
| SYS-009  | LOKI        | Sun          | Sun Fire X4150         | 1U          | Labeled: OPENSENSE             |
| SYS-010  | LOKE        | IBM          | System x3550 M2        | 1U          | Newer gen IBM                  |
| SYS-011  | GUNGNIR     | ZyXEL        | ZyWALL 110             | 1U          | Security Gateway / Firewall    |
| SYS-012  | BIFROST-01  | Edge-Core    | ECS4510-28F            | 1U          | 28-Port SFP Fiber Switch       |
| SYS-013  | BIFROST-02  | Edge-Core    | ECS4510-28F            | 1U          | 28-Port SFP Fiber Switch       |
| SYS-014  | MODI        | HP           | V1910-24G-PoE          | 1U          | 365W PoE Switch (JE007A)       |
| SYS-015  | MAGNI       | Cisco        | Catalyst 2960G         | 1U          | 24-Port Managed Gig Switch     |
| SYS-016  | HOENIR      | HP           | ProCurve 1800-24G      | 1U          | Fanless/Silent Switch (J9028A) |
| SYS-017  | HUGINN      | Avocent      | KVM Switch             | 1U          | Rackmount KVM                  |
| SYS-018  | SURTR-01    | APC          | Back-UPS CS 650        | Desktop     | UPS Unit 1                     |
| SYS-019  | SURTR-02    | APC          | Back-UPS CS 650        | Desktop     | UPS Unit 2                     |

---

# Blade Nodes (Inside ASGARD)

| Asset ID | Hostname     | Manufacturer | Model         | Slot | Notes                        |
|----------|--------------|--------------|---------------|------|------------------------------|
| BLD-001  | BLADE-01     | HP           | BL460c Gen8   | 1    | 15K SAS Drives               |
| BLD-002  | BLADE-02     | HP           | BL460c Gen8   | 2    |                              |
| BLD-003  | BLADE-03     | HP           | BL460c Gen8   | 3    |                              |
| BLD-004  | BLADE-04     | HP           | BL460c Gen8   | 4    |                              |
| BLD-005  | BLADE-05     | HP           | BL460c Gen8   | 5    |                              |
| BLD-006  | BLADE-06     | HP           | BL460c Gen8   | 6    |                              |
| BLD-007  | BLADE-07     | HP           | BL460c Gen8   | 7    |                              |
| BLD-008  | BLADE-08     | HP           | BL460c Gen8   | 8    |                              |
| BLD-009  | BLADE-09     | HP           | BL460c Gen8   | 9    |                              |
| BLD-010  | BLADE-10     | HP           | BL460c Gen8   | 10   |                              |
| BLD-011  | BLADE-11     | HP           | BL460c Gen8   | 11   |                              |
| BLD-012  | BLADE-12     | HP           | BL460c Gen8   | 12   |                              |
| BLD-013  | BLADE-13     | HP           | BL460c Gen8   | 13   |                              |
| BLD-014  | BLADE-14     | HP           | BL460c Gen8   | 14   |                              |
| BLD-015  | BLADE-15     | HP           | BL460c Gen8   | 15   |                              |
| BLD-016  | BLADE-16     | HP           | BL460c Gen8   | 16   |                              |

---

# System Overviews

Here are some brief overviews of selected systems to provide context and highlight their typical roles or notable features.

### IBM System x3550 Type 7978 / x3650 Type 7979 Series — [x3550 overview](https://www.ibm.com/support/pages/overview-ibm-system-x3550-type-7978) · [x3650 overview](https://www.ibm.com/support/pages/overview-ibm-system-x3650-type-1914-7979)
*1U (x3550) / 2U (x3650) · dual Xeon (Harpertown/Nehalem) · DDR2 ECC FBDIMM up to 32GB · SAS/SATA*

These were enterprise-grade rack servers, popular in the late 2000s, powered by Intel Xeon processors (e.g., Nehalem, Westmere generations). The x3550 is a compact 1U server, ideal for general-purpose computing, while the x3650 is a 2U model offering greater expansion capabilities for storage or PCIe cards. They served as reliable workhorses for various data center applications, including virtualization and database hosting.

### HP BladeSystem C7000 — [QuickSpecs](https://www.hpe.com/psnow/doc/c04128339) · [BL460c Gen8 QuickSpecs](https://www.hpe.com/psnow/doc/c04123239)
*10U · up to 16 half-height blades · shared power/cooling/networking via backplane · Onboard Administrator*

The C7000 is a substantial 10U blade enclosure designed to host up to 16 server blades, along with storage blades and integrated networking/management modules. It provides a consolidated infrastructure for power, cooling, and network connectivity, significantly simplifying cable management and enabling high-density computing environments. These systems were foundational for many enterprise virtualization platforms.

### Sun Fire X4150 (SYS-009, LOKI)
*1U · dual Xeon (Harpertown) · 16 DIMM slots · 4 network interface*

A 1U rackmount server from Sun Microsystems, the Sun Fire X4150 typically featured Intel Xeon processors. Sun's x86 server line was recognized for its build quality and integration, often running Solaris or Linux. I use it as a dedicated firewall / network appliance (OpenSense), utilizing its robust hardware for network security and routing tasks.

### Dell PowerVault MD1200 (SYS-004, MIMIR) — [specs](https://www.dell.com/support/kbdoc/en-us/000124452/dell-powervault-md1200-md1220-direct-attached-storage)
*2U DAS · 12× LFF (3.5") hot-swap SAS/SATA bays · 6Gb/s SAS · up to 24TB raw*

The PowerVault MD1200 is a direct-attached storage (DAS) enclosure, designed to expand the storage capacity of compatible servers (such as Dell PowerEdge servers or others equipped with suitable SAS HBAs). This 2U unit can accommodate up to 12 LFF (3.5-inch) SAS/SATA drives, providing an expandable and cost-effective solution for adding raw storage to a homelab environment.

### ZyXEL ZyWALL 110 (SYS-011, GUNGNIR)
*2× GbE WAN · 4× GbE LAN · VPN gateway · IPS/IDS*

The ZyWALL 110 is a professional-grade security gateway and VPN firewall. It delivers comprehensive network security features, including intrusion prevention, content filtering, and strong VPN capabilities. This appliance is well-suited for establishing a secure perimeter for a homelab network or segmenting different network environments for enhanced control and protection. However since I don't have any license for it is currently not used.
