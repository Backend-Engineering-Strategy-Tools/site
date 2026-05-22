---
title: "Redfish"
description: "Redfish — the DMTF standard RESTful API for out-of-band server management. JSON over HTTPS, replacing IPMI for modern hardware."
date: 2026-05-22
draft: false
showReadingTime: false
layout: single
tags: ["redfish", "bmc", "out-of-band", "api", "bare-metal", "hardware"]
---

Redfish is a DMTF standard that defines a RESTful API for out-of-band server management. It replaces IPMI's aging binary protocol with JSON over HTTPS — same capabilities (power control, sensors, firmware, console), but with a proper API, role-based access control, and standard authentication. Supported by all major server vendors on current-generation hardware.

---

## Why Redfish over IPMI

|                 | IPMI                  | Redfish                       |
|-----------------|-----------------------|-------------------------------|
| Protocol        | Binary, UDP 623       | HTTPS (REST/JSON)             |
| Auth            | RAKP (has CVEs)       | HTTP Basic / Session tokens   |
| Encryption      | Optional (IPMI 2.0)   | Always (TLS)                  |
| Discoverability | No                    | Yes (hypermedia)              |
| Scripting       | ipmitool flags        | curl, Python, any HTTP client |
| Extensibility   | Vendor OEM extensions | Structured OEM namespaces     |
| Maturity        | Established, aging    | Modern, actively developed    |

Redfish is not universally available — older hardware (pre-2015 roughly) has IPMI only. Both coexist on many current systems; IPMI is still useful for compatibility. See [IPMI](ipmi/).

---

## Vendor implementations

| Vendor      | BMC                      | Redfish support                       |
|-------------|--------------------------|---------------------------------------|
| Dell        | iDRAC 8+                 | Full, v1.0+                           |
| HPE         | iLO 4+                   | Full (iLO 5 most complete)            |
| Supermicro  | BMC (X11+)               | Full                                  |
| Lenovo      | XClarity                 | Full                                  |
| Intel       | BMC on server boards     | Partial                               |
| OpenBMC     | Open-source BMC firmware | Full (used by Facebook, Google infra) |
| AMI MegaRAC | OEM BMC firmware         | Full                                  |

---

## API structure

Redfish uses a consistent URL hierarchy rooted at `/redfish/v1/`. Navigation is hypermedia-driven — the root returns links to subsystems, and you follow them.

```
/redfish/v1/
├── Systems/          ← compute systems (servers)
│   └── 1/
│       ├── Processors/
│       ├── Memory/
│       ├── Storage/
│       └── Actions/ComputerSystem.Reset
├── Chassis/          ← physical chassis, power, thermal
│   └── 1/
│       ├── Power/    ← PSU status, power consumption
│       └── Thermal/  ← temperatures, fan speeds
├── Managers/         ← the BMC itself
│   └── 1/
│       └── NetworkInterfaces/
└── UpdateService/    ← firmware updates
```

---

## Usage with curl

```bash
BMC="https://192.168.1.10"
USER="admin"
PASS="password"

# Get system overview
curl -sk -u "$USER:$PASS" "$BMC/redfish/v1/Systems/1" | jq .

# Power state
curl -sk -u "$USER:$PASS" "$BMC/redfish/v1/Systems/1" | jq .PowerState

# Power on
curl -sk -u "$USER:$PASS" -X POST \
  -H "Content-Type: application/json" \
  -d '{"ResetType":"On"}' \
  "$BMC/redfish/v1/Systems/1/Actions/ComputerSystem.Reset"

# Power off (graceful)
curl -sk -u "$USER:$PASS" -X POST \
  -H "Content-Type: application/json" \
  -d '{"ResetType":"GracefulShutdown"}' \
  "$BMC/redfish/v1/Systems/1/Actions/ComputerSystem.Reset"

# Force off
curl -sk -u "$USER:$PASS" -X POST \
  -H "Content-Type: application/json" \
  -d '{"ResetType":"ForceOff"}' \
  "$BMC/redfish/v1/Systems/1/Actions/ComputerSystem.Reset"

# Thermal — CPU temps, fan speeds
curl -sk -u "$USER:$PASS" "$BMC/redfish/v1/Chassis/1/Thermal" | jq '.Temperatures[] | {Name, ReadingCelsius}'
```

Reset types vary by vendor — check `AllowableValues` in the action schema:

```bash
curl -sk -u "$USER:$PASS" \
  "$BMC/redfish/v1/Systems/1" | jq '.Actions["#ComputerSystem.Reset"]["ResetType@Redfish.AllowableValues"]'
```

---

## Python — sushy

`sushy` is the reference Python library for Redfish, used by OpenStack Ironic:

```python
import sushy

client = sushy.Sushy("https://192.168.1.10", username="admin", password="password", verify=False)

system = client.get_system("/redfish/v1/Systems/1")
print(system.power_state)          # On / Off
system.reset_system(sushy.RESET_ON)
system.reset_system(sushy.RESET_FORCE_OFF)
```

---

## Session-based auth

For scripts making many requests, create a session to avoid re-authenticating on every call:

```bash
# Create session
SESSION=$(curl -sk -X POST \
  -H "Content-Type: application/json" \
  -d '{"UserName":"admin","Password":"password"}' \
  "https://192.168.1.10/redfish/v1/SessionService/Sessions" \
  -D -)

TOKEN=$(echo "$SESSION" | grep -i X-Auth-Token | awk '{print $2}' | tr -d '\r')

# Use token
curl -sk -H "X-Auth-Token: $TOKEN" \
  "https://192.168.1.10/redfish/v1/Systems/1" | jq .PowerState
```

---

## Firmware updates

Redfish standardises firmware update via `UpdateService`:

```bash
# Check current firmware
curl -sk -u "$USER:$PASS" "$BMC/redfish/v1/UpdateService/FirmwareInventory" | jq .

# Push update (multipart, vendor-specific details vary)
curl -sk -u "$USER:$PASS" -X POST \
  -H "Content-Type: application/octet-stream" \
  --data-binary @firmware.bin \
  "$BMC/redfish/v1/UpdateService/update"
```

Vendor tooling (Dell racadm, HPE iLOrest) is often more reliable than raw curl for firmware updates.

---

## Related

- [IPMI](ipmi/) — older binary protocol, still needed for pre-Redfish hardware
- [Out-of-band management overview](./)
- [Hardware provisioning](/public-notes/hardware/hardware-provisioning/) — PXE boot and bare-metal provisioning
