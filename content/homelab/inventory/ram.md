---
title: "RAM Inventory"
date: 2026-05-13
draft: false
showReadingTime: false
layout: single
---

# Memory Types

| Component ID | Manufacturer | FRU / Model                      | Capacity | Type            | Speed   | Qty | Notes |
|--------------|--------------|----------------------------------|----------|-----------------|---------|-----|-------|
| RAM-001      | IBM          | 25R8079                          | 8GB      | DDR2 ECC FBDIMM | 667MHz  | 16  |       |
| RAM-002      | Unknown      | —                                | 4GB      | DDR2 ECC FBDIMM | 667MHz  | 6   |       |
| RAM-003      | Unknown      | —                                | ?        | ?               | —       | ?   |       |
| RAM-004      | Unknown      | —                                | ?        | ?               | —       | ?   |       |
| RAM-005      | Micron       | MT36KSF1G72PZ-1G4M1FI            | 8GB      | DDR3 ECC Reg    | 1333MHz | 6   | 2Rx4  |
| RAM-006      | Hynix        | HMT31GR7CFR4C-PB                 | 8GB      | DDR3 ECC Reg    | 1600MHz | 10  | 2Rx4  |
| RAM-007      | Micron       | MT18KSF1G72PDZ-1G6E1HG           | 8GB      | DDR3 ECC Reg    | 1600MHz | 16  | 2Rx8  |
| RAM-008      | Hynix        | HMT151R7BFR4C-H9 / HP 500203-061 | 4GB      | DDR3 ECC Reg    | 1333MHz | 27  | 1Rx4  |
| RAM-009      | HP           | 500202-061 / 501533-001          | 2GB      | DDR3 ECC Reg    | 1333MHz | 15  | 2Rx8  |
| RAM-010      | IBM          | 43X5046                          | 2GB      | DDR3 ECC Reg    | 1333MHz | 7   | 1Rx4  |

---

# Memory Allocation

| Asset ID | Hostname | Component ID      | Quantity | Total Installed RAM                 |
|----------|----------|-------------------|----------|-------------------------------------|
| SYS-001  | FREJA    | RAM-002           | 6        | 24GB                                |
| SYS-002  | TYR      | RAM-001           | 8        | 64GB                                |
| SYS-003  | TOR      | RAM-001           | 8        | 64GB                                |
| SYS-005  | ODEN     | RAM-005           | 6        | 48GB                                |
| SYS-005  | ODEN     | RAM-006           | 6        | 48GB (runs at 1333MHz; mixed speed) |
| BLD-001  | BLADE-01 | RAM-008           | 1        | 4GB                                 |
| BLD-003  | BLADE-03 | RAM-008           | 8        | 32GB                                |
| BLD-004  | BLADE-04 | RAM-008           | 2        | 8GB                                 |
| BLD-005  | BLADE-05 | RAM-008           | 2        | 8GB                                 |
| BLD-006  | BLADE-06 | RAM-008           | 2        | 8GB                                 |
| BLD-007  | BLADE-07 | RAM-008           | 2        | 8GB                                 |
| BLD-008  | BLADE-08 | RAM-007           | 2        | 16GB                                |
| BLD-009  | BLADE-09 | RAM-008           | 2        | 8GB                                 |
| BLD-010  | BLADE-10 | RAM-008           | 2        | 8GB                                 |
| BLD-011  | BLADE-11 | RAM-009           | 4        | 8GB                                 |
| BLD-012  | BLADE-12 | RAM-009           | 4        | 8GB                                 |
| BLD-013  | BLADE-13 | RAM-006           | 4        | 32GB                                |
| BLD-014  | BLADE-14 | RAM-008           | 2        | 8GB                                 |
| BLD-015  | BLADE-15 | RAM-008           | 2        | 8GB                                 |
| BLD-016  | BLADE-16 | RAM-008           | 2        | 8GB                                 |
| BLD-002  | BLADE-02 | RAM-009 + RAM-010 | 7        | 14GB (mixed; odd count)             |
