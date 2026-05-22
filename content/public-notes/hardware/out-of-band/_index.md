---
title: "Out-of-Band Management"
description: "Out-of-band server management — accessing and controlling hardware independently of the host OS, via the BMC. Covers IPMI, Redfish, and vendor implementations."
date: 2026-05-22
draft: true
showReadingTime: false
layout: single
tags: ["ipmi", "redfish", "bmc", "out-of-band", "hardware", "homelab"]
---

Out-of-band (OOB) management means controlling a server independently of its operating system — via a dedicated processor on the motherboard called the **BMC (Baseboard Management Controller)**. The BMC has its own NIC, its own firmware, and its own IP. You can power a server on, read temperatures, and access a console whether or not the host OS is running, hung, or even installed.

Used for: bare-metal provisioning, remote recovery, hardware monitoring, firmware updates, automated power management.

---

## Standards

Two main protocols, one old and one new:

| | IPMI | Redfish |
|---|---|---|
| Protocol | Binary, UDP 623 | HTTPS / JSON (REST) |
| Era | 1998– | 2015– |
| Scripting | ipmitool | curl, Python, any HTTP client |
| Security | Weak (known CVEs) | TLS + token auth |
| Availability | Universal | Modern hardware (roughly post-2015) |

- [IPMI](ipmi/) — the established standard; ipmitool, SoL, sensor readings, security considerations
- [Redfish](redfish/) — the modern replacement; REST API, curl and Python examples, firmware updates

---

## Vendor implementations

Most vendors ship their own BMC firmware on top of these standards:

| Vendor | Product | Supports |
|--------|---------|---------|
| Dell | iDRAC | IPMI + Redfish (iDRAC 8+) |
| HP / HPE | iLO | IPMI + Redfish (iLO 4+) |
| Sun / Oracle | ILOM | IPMI 2.0, web UI |
| Supermicro | BMC | IPMI + Redfish (X11+) |
| Lenovo | XClarity / IMM | IPMI + Redfish |
| HP BladeSystem | Onboard Administrator | Enclosure-level; individual blades use iLO |

---

## Related

- [Hardware provisioning](/public-notes/hardware/hardware-provisioning/) — PXE boot, bare-metal provisioning tools
