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

# Switch Ports

| Asset ID | Hostname   | Port Type  | Count | SFP Cages | Uplink | Notes                |
|----------|------------|------------|-------|-----------|--------|----------------------|
| SYS-012  | BIFROST-01 | SFP Fiber  | 28    | 28        | ?      | All-SFP switch       |
| SYS-013  | BIFROST-02 | SFP Fiber  | 28    | 28        | ?      | All-SFP switch       |
| SYS-014  | MODI       | RJ45 + SFP | 24+4  | 4         | ?      | 24× GbE PoE + 4× SFP |
| SYS-015  | MAGNI      | RJ45       | 24    | ?         | ?      | 24× GbE managed      |
| SYS-016  | VALI       | RJ45       | 24    | ?         | ?      | Fanless; 24× GbE     |

