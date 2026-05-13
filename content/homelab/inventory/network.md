---
title: "Network Inventory"
date: 2026-05-13
draft: false
showReadingTime: false
layout: single
---

# NIC Catalog

| Component ID | Manufacturer | Model / FRU                               | Ports | Speed | Interface | Notes                                                 |
|--------------|--------------|-------------------------------------------|-------|-------|-----------|-------------------------------------------------------|
| NIC-001      | IBM          | Onboard (x3550 M3 mobo)                   | 2     | 1GbE  | RJ45      | Integrated; present on all x3550 M3                   |
| NIC-002      | IBM          | Dual-port GbE Daughter Card (FRU 43V6927) | 2     | 1GbE  | RJ45      | Add-in daughter card slot                             |
| NIC-003      | Sun / Intel  | Onboard quad GbE (Sun Fire X4150)         | 4     | 1GbE  | RJ45      | Integrated; all 4 ports on rear                       |
| NIC-004      | HP / Emulex  | FlexFabric 554FLB (647584-001)            | 2     | 10GbE | SFP+ FLB  | FlexibleLOM slot; FCoE + Flex-10 capable; BL460c Gen8 |

---

# NIC Placement

| Asset ID | Hostname | Component ID      | Total Data Ports | Mgmt Port | Notes                     |
|----------|----------|-------------------|------------------|-----------|---------------------------|
| SYS-005  | ODEN     | NIC-001           | 2× GbE           | 1× IMM    |                           |
| SYS-006  | LOKE     | NIC-001 + NIC-002 | 4× GbE           | 1× IMM    | Daughter card FRU 43V6927 |
| SYS-009  | HEIMDAL  | NIC-003           | 4× GbE           | 1× mgmt   | OPNsense firewall         |

---

# Network Addresses

| Asset ID | Hostname | Interface | Role | IP Address | MAC Address | Notes |
|----------|----------|-----------|------|------------|-------------|-------|
| SYS-005  | ODEN     | eth0      | data |            |             |       |
| SYS-005  | ODEN     | eth1      | data |            |             |       |
| SYS-005  | ODEN     | mgmt      | IMM  |            |             |       |
| SYS-006  | LOKE     | eth0      | data |            |             |       |
| SYS-006  | LOKE     | eth1      | data |            |             |       |
| SYS-006  | LOKE     | eth2      | data |            |             |       |
| SYS-006  | LOKE     | eth3      | data |            |             |       |
| SYS-006  | LOKE     | mgmt      | IMM  |            |             |       |

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

# Switch Ports

| Asset ID | Hostname   | Port Type  | Count | SFP Cages | Uplink | Notes                |
|----------|------------|------------|-------|-----------|--------|----------------------|
| SYS-012  | BIFROST-01 | SFP Fiber  | 28    | 28        | ?      | All-SFP switch       |
| SYS-013  | BIFROST-02 | SFP Fiber  | 28    | 28        | ?      | All-SFP switch       |
| SYS-014  | MODI       | RJ45 + SFP | 24+4  | 4         | ?      | 24× GbE PoE + 4× SFP |
| SYS-015  | MAGNI      | RJ45       | 24    | ?         | ?      | 24× GbE managed      |
| SYS-016  | VALI       | RJ45       | 24    | ?         | ?      | Fanless; 24× GbE     |

---

# Module Overviews

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
