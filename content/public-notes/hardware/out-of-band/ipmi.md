---
title: "IPMI"
description: "IPMI (Intelligent Platform Management Interface) — out-of-band server management via the BMC. Power control, sensors, serial console, and ipmitool usage."
date: 2026-05-22
draft: false
showReadingTime: false
layout: single
tags: ["ipmi", "bmc", "out-of-band", "bare-metal", "homelab", "hardware"]
---

IPMI (Intelligent Platform Management Interface) is a hardware-level management standard built into most server-class hardware. It runs on a dedicated processor on the motherboard — the **BMC (Baseboard Management Controller)** — independently of the host OS. The BMC has its own NIC, its own firmware, and its own IP address. You can power a server on or off, read sensor data, and access a serial console even if the host is completely dead.

Current version is IPMI 2.0, which added encryption and stronger authentication over 1.5.

---

## BMC implementations by vendor

IPMI is the standard; each vendor ships their own BMC firmware on top of it:

| Vendor         | BMC / OOB product                                | Notes                                                                          |
|----------------|--------------------------------------------------|--------------------------------------------------------------------------------|
| Dell           | iDRAC (Integrated Dell Remote Access Controller) | iDRAC 6/7/8/9; newer versions add Redfish                                      |
| HP / HPE       | iLO (Integrated Lights-Out)                      | iLO 2/3/4/5; iLO 4+ adds Redfish                                               |
| Sun / Oracle   | ILOM (Integrated Lights-Out Manager)             | Sun Fire series (X4150, X4450, etc.)                                           |
| Supermicro     | IPMI / BMC                                       | Web UI + IPMI; newer boards also Redfish                                       |
| Lenovo / IBM   | XClarity / IMM                                   | IMM2 on older systems                                                          |
| HP BladeSystem | Onboard Administrator (OA)                       | Enclosure-level management (C7000, C3000) — separate from individual blade iLO |

Most also expose a web UI and some form of virtual KVM (keyboard/video/mouse over network) in addition to IPMI over LAN.

---

## Network setup

The BMC NIC is usually shared with a host NIC (shared/failover mode) or dedicated (preferred for management). Configure via BIOS/UEFI or the vendor's setup utility before the OS boots.

Assign a static IP — a BMC on DHCP is workable but inconvenient. Keep BMCs on a dedicated management VLAN if possible; they have historically had security issues and shouldn't be exposed to general traffic.

---

## ipmitool

The standard CLI for IPMI over LAN. Available in most Linux package repos.

```bash
# Power control
ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pass> power status
ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pass> power on
ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pass> power off
ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pass> power cycle
ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pass> power reset

# Sensor readings (temperatures, voltages, fan speeds)
ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pass> sensor list

# System Event Log
ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pass> sel list
ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pass> sel clear

# Serial over LAN (SoL) — console access without KVM
ipmitool -I lanplus -H <bmc-ip> -U <user> -P <pass> sol activate
# Exit SoL: ~.
```

Use `-I lanplus` (IPMI 2.0 with encryption) rather than `-I lan` (IPMI 1.5, unencrypted) where supported.

---

## Serial over LAN (SoL)

SoL forwards the server's serial port over the IPMI connection — giving you a text console to the host without a KVM or physical access. Requires the host OS to have serial console enabled:

```bash
# Add to GRUB_CMDLINE_LINUX in /etc/default/grub
console=tty0 console=ttyS1,115200n8

# Enable serial getty
systemctl enable serial-getty@ttyS1.service
```

Baud rate must match what's configured in the BIOS/BMC (typically 115200).

---

## Security

IPMI has a poor security history:

- IPMI 1.5 sends credentials in cleartext
- IPMI 2.0 has had multiple authentication bypass vulnerabilities (RAKP, cipher 0)
- The BMC itself runs independent firmware that may have unpatched CVEs
- Default credentials (`admin`/`admin`, `ADMIN`/`ADMIN`) are common and widely known

Minimum steps:
- Change default credentials immediately
- Use IPMI 2.0 (`lanplus`) only
- Disable cipher suite 0: `ipmitool -I lanplus ... lan set 1 cipher_privs XxxxxxxxxxxxxxxX`
- Isolate BMC network from internet and untrusted hosts — management VLAN with no external exposure
- Keep BMC firmware updated

---

## Related

- [Redfish](redfish/) — the modern REST API replacement for IPMI
- [Out-of-band management overview](./)
- [Hardware provisioning](/public-notes/hardware/hardware-provisioning/) — PXE boot and bare-metal provisioning
