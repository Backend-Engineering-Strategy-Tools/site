---
title: "CPU Inventory"
date: 2026-05-13
draft: false
showReadingTime: false
layout: single
---

# CPU Catalog

| Component ID | Manufacturer | Model              | Cores | Threads | Base Clock | Socket  | TDP  | Qty | Notes                              |
|--------------|--------------|--------------------|-------|---------|------------|---------|------|-----|------------------------------------|
| CPU-001      | Intel        | Xeon E5430         | 4     | 4       | 2.66GHz    | LGA771  | 80W  | 4   | Harpertown 45nm; no HT             |
| CPU-002      | Intel        | Xeon E5520         | 4     | 8       | 2.26GHz    | LGA1366 | 80W  | 2   | Nehalem-EP; HT enabled; fits M3    |
| CPU-003      | Intel        | Xeon E5504         | 4     | 4       | 2.00GHz    | LGA1366 | 80W  | 1   | Nehalem-EP; no HT; fits M3         |
| CPU-004      | Intel        | Core 2 Quad Q6600  | 4     | 4       | 2.40GHz    | LGA775  | 95W  | 1   | Kentsfield; desktop; no server fit |
| CPU-005      | Intel        | Xeon E5410         | 4     | 4       | 2.33GHz    | LGA771  | 80W  | 1   | Harpertown 45nm; no HT; fits M1    |

---

# CPU Placement

| Asset ID | Hostname | Component ID | Quantity | Notes                        |
|----------|----------|--------------|----------|------------------------------|
| SYS-001  | FREJA    | ???          | 1        | Single socket; LGA771 (M1)   |
| SYS-002  | TYR      | ???          | 2        | Dual socket; LGA771 (M1)     |
| SYS-003  | TOR      | ???          | 2        | Dual socket; LGA771 (M1)     |
| SYS-005  | ODEN     | ???          | 2        | Dual socket; LGA1366 (M3)    |
| SYS-006  | LOKE     | ???          | 2        | Dual socket; LGA1366 (M3)    |
| SYS-009  | HEIMDAL  | CPU-001      | 2        | Dual socket; LGA771          |
