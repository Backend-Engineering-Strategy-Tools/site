---
title: "Blade Inventory"
date: 2026-05-14
draft: false
showReadingTime: false
layout: single
---

# Blade Configurations (ASGARD — HP C7000)

All blades are HP BL460c Gen8. Manufacturer and model omitted from table — see [systems inventory](../systems) for roster.

| Asset ID | Slot | CPU    | RAM                         | Disk                                 | LOM     | SAS Ctrl              | Mezz 1 (bays 3/4) | Mezz 2 (bays 5/6) |
|----------|------|--------|-----------------------------|--------------------------------------|---------|-----------------------|-------------------|-------------------|
| BLD-001  | 1    | 2× (?) | 4GB — 1× RAM-008            | 2× HDD-011 (146GB, 15K)              | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-002  | 2    | 2× (?) | 14GB — 7× RAM-009/010 mixed | —                                    | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-003  | 3    | 2× (?) | 32GB — 8× RAM-008           | 2× HDD-012 (300GB, 10K)              | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-004  | 4    | 2× (?) | 8GB — 2× RAM-008            | —                                    | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-005  | 5    | 2× (?) | 8GB — 2× RAM-008            | 1× HDD-011 + 1× HDD-012              | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-006  | 6    | 2× (?) | 8GB — 2× RAM-008            | 2× HDD-012 (300GB, 10K)              | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-007  | 7    | 2× (?) | 8GB — 2× RAM-008            | 1× HDD-013 + 1× HDD-014 (900GB each) | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-008  | 8    | 2× (?) | 16GB — 2× RAM-007           | 2× HDD-012 (300GB, 10K)              | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-009  | 9    | 2× (?) | 8GB — 2× RAM-008            | —                                    | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-010  | 10   | 2× (?) | 8GB — 2× RAM-008            | 2× HDD-012 (300GB, 10K)              | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-011  | 11   | 2× (?) | 8GB — 4× RAM-009            | 2× HDD-012 (300GB, 10K)              | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-012  | 12   | 2× (?) | 8GB — 4× RAM-009            | 2× HDD-012 (300GB, 10K)              | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-013  | 13   | 2× (?) | 32GB — 4× RAM-006           | —                                    | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-014  | 14   | 2× (?) | 8GB — 2× RAM-008            | —                                    | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-015  | 15   | 2× (?) | 8GB — 2× RAM-008            | 2× HDD-012 (300GB, 10K)              | NIC-004 | separate card, no P/N | —                 | —                 |
| BLD-016  | 16   | 2× (?) | 8GB — 2× RAM-008            | —                                    | NIC-004 | separate card, no P/N | —                 | —                 |

---

# Blade Enclosure Modules (ASGARD — HP C7000)

| Bay Type     | Module                         | Part No                 | Qty | Status    | Notes                                                                                    |
|--------------|--------------------------------|-------------------------|-----|-----------|------------------------------------------------------------------------------------------|
| Interconnect | HP 1:10Gb Ethernet BL-c Switch | 438476-001              | 2   | Installed | Bays 1-2; Int: ports 1-16 blade downlinks; Ext: 1× CX4 10GbE, 2× XFP 10GbE, 4× RJ45 1GbE |
| Interconnect | —                              | —                       | —   | Empty     | Bays 3-4: mezzanine slot 1 fabric — Ethernet, FC, SAS, or IB                             |
| Interconnect | —                              | —                       | —   | Empty     | Bays 5-6: mezzanine slot 2 fabric — Ethernet, FC, SAS, or IB                             |
| Interconnect | —                              | —                       | —   | Empty     | Bays 7-8: mezzanine slot 2 fabric (double-wide IB uses bays 5+7)                         |
| OA           | HP Onboard Administrator       | 4K09B5 / P/N 407296-001 | 2   | Installed | Redundant pair; with VGA                                                                 |
| OA           | HP Onboard Administrator       | 4K08A6 / P/N 459526-001 | 1   | Spare     | No VGA; different revision                                                               |
| Power Supply | HP BladeSystem c7000 PSU       | ?                       | 6   | Installed | Full (6/6)                                                                               |
| Fan          | HP BladeSystem c7000 Fan       | ?                       | 10  | Installed | Full (10/10)                                                                             |

---

# System Overviews

### HP BladeSystem C7000 — [QuickSpecs](https://www.hpe.com/psnow/doc/c04128339)
*10U · up to 16 half-height blades · shared power/cooling/networking via backplane · Onboard Administrator*

The C7000 is a substantial 10U blade enclosure designed to host up to 16 server blades, along with storage blades and integrated networking/management modules. It provides a consolidated infrastructure for power, cooling, and network connectivity, significantly simplifying cable management and enabling high-density computing environments. These systems were foundational for many enterprise virtualization platforms.

### HP BL460c Gen8 — [QuickSpecs](https://www.hpe.com/psnow/doc/c04123239)
*Half-height blade · 2× LGA2011 (E5-2600 v1/v2) · up to 192GB DDR3 ECC Reg · 2× SFF SAS bays · FlexibleLOM + 2 mezzanine slots*

The BL460c Gen8 is a half-height server blade for the c-Class BladeSystem enclosure. Each blade supports two Intel Xeon E5-2600 v1 or v2 series processors and up to 24 DDR3 ECC Registered DIMMs across 24 slots. Local storage is limited to two 2.5" SFF SAS/SATA bays managed by an embedded Smart Array P220i controller. Networking is handled through the FlexibleLOM slot (populated with the HP FlexFabric 554FLB in ASGARD), which connects to the enclosure's interconnect bays via the backplane. Two additional mezzanine slots allow expansion with Fibre Channel, SAS, or InfiniBand HBAs.

---

### ASGARD Interconnect Bay Architecture — [c7000 Interconnect Components](https://andovercg.com/datasheets/hpe-bladesystem-c-class-interconnect-components.pdf) · [Wikipedia](https://en.wikipedia.org/wiki/HPE_BladeSystem)
*8 interconnect bays (4 pairs) · each pair ties to a specific fabric/mezzanine slot on all blades*

The c7000 rear has 8 single-wide interconnect bays arranged as 4 matched pairs. Both bays in a pair must carry the same module type — they connect to the same blade mezzanine slot and form a redundant fabric. Up to 4 simultaneous fabrics are supported.

| Bay pair | Blade connection  | Currently                         | Could hold                                                         |
|----------|-------------------|-----------------------------------|--------------------------------------------------------------------|
| 1 / 2    | LOM (onboard NIC) | HP 1:10Gb Ethernet BL-c Switch ×2 | Ethernet switch or pass-thru                                       |
| 3 / 4    | Mezzanine slot 1  | **Empty**                         | Ethernet, Fibre Channel (4/8Gb FC switch), SAS switch, InfiniBand  |
| 5 / 6    | Mezzanine slot 2  | **Empty**                         | Same options as 3/4                                                |
| 7 / 8    | Mezzanine slot 2  | **Empty**                         | Same; or second half of a double-wide InfiniBand module (bays 5+7) |

**Note:** to use FC, SAS, or InfiniBand bays the blades themselves also need matching mezzanine cards installed. BL460c Gen8 blades have 2 mezzanine slots available.

Common modules seen in homelab use (none currently owned):
- **Fibre Channel**: HP 4Gb/8Gb BLc FC switch (e.g. AJ821A for 8Gb)
- **SAS**: HP SAS BLc Switch — gives blades shared SAS fabric access to DAS like MIMIR
- **InfiniBand**: HP DDR/QDR IB switch — requires matching IB mezzanine card in each blade

---

### HP BladeSystem Onboard Administrator (OA) — [User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00112728en_us&docLocale=en_US)
*P/N 407296-001 (installed ×2, with VGA) · P/N 459526-001 (spare ×1, no VGA) · Fits OA bays (separate from interconnect bays)*

The OA is the management brain of the c7000 enclosure. It provides a web GUI, SSH/CLI, and SNMP interface for managing all blades, power supplies, fans, and interconnect modules. Two OA modules run as a redundant active/standby pair — if the primary fails, the standby takes over without interruption.

**External connectors (407296-001 / with VGA):**
- 1× RJ-45 management Ethernet (dedicated OOB network)
- 1× USB (for local keyboard)
- 1× DB-9 serial console
- 1× VGA (local video output for console access)

**459526-001 (spare, no VGA):** earlier/different revision — same management functions, management Ethernet + USB + serial, but no VGA port for local console.

---

### HP 1:10Gb Ethernet BL-c Switch — [User Guide](https://www.manualslib.com/manual/419870/Hp-438031-B21-1-10gb-Ethernet-Bl-C-Switch.html) · [QuickSpecs](https://www.hpe.com/psnow/doc/c04282599)
*P/N 438476-001 (spare/FRU) / 438031-B21 (orderable) · c-Class BladeSystem interconnect module · 16 blade downlinks + 7 uplinks*

Managed Gigabit/10GbE blade switch in a single interconnect bay. Each module connects to all 16 blade bays via the enclosure backplane. ASGARD has two installed (in adjacent bays 1 and 2), linked via the port 17 X-Connect.

**Port map:**

| Port(s) | Connector | Speed | Role                                                          |
|---------|-----------|-------|---------------------------------------------------------------|
| 1–16    | Backplane | 1GbE  | Blade downlinks (1 per blade bay)                             |
| 17      | Internal  | 10GbE | X-Connect crosslink to adjacent bay switch                    |
| 19      | SFF-8470  | 10GbE | CX4 copper uplink (Ethernet — not SAS despite same connector) |
| 20–21   | XFP       | 10GbE | Fiber/DAC uplinks (XFP cages; older/larger than SFP+)         |
| 22–25   | RJ-45     | 1GbE  | Copper uplinks                                                |
