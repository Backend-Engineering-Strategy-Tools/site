---
title: "Cables & Transceivers Inventory"
date: 2026-05-13
draft: false
showReadingTime: false
layout: single
tags: ["homelab", "inventory", "hardware", "networking", "storage"]
---

# SAS Cables

| Component ID | Type               | Connectors          | Length | Qty | Notes                                                          |
|--------------|--------------------|---------------------|--------|-----|----------------------------------------------------------------|
| CBL-SAS-001  | Internal Mini-SAS  | SFF-8087 → SFF-8087 | ?      | ?   |                                                                |
| CBL-SAS-002  | Int → Ext Mini-SAS | SFF-8087 → SFF-8088 | ?      | ?   | Needed for internal cards (CTRL-002/003) to reach DAS          |
| CBL-SAS-003  | Ext SAS            | SFF-8470 → SFF-8088 | ?      | ?   | CTRL-006 → MIMIR                                               |

---

# Ethernet Cables

| Component ID | Type       | Speed | Length | Qty | Notes |
|--------------|------------|-------|--------|-----|-------|
| CBL-ETH-001  | Cat5e/Cat6 | 1GbE  | ?      | ?   |       |

---

# SFP / SFP+ Transceivers

| Component ID | Type  | Speed  | Wavelength | Reach | Qty | Where used                                      |
|--------------|-------|--------|------------|-------|-----|-------------------------------------------------|
| SFP-001      | SFP   | 1GbE   | ?          | ?     | ?   | BIFROST-01/02 (28 cages each); MODI (4 cages)        |
| SFP-002      | XFP   | 10GbE  | ?          | ?     | ?   | ASGARD switch ports 20-21 (2× XFP per module × 2)   |

---

# Adapters

| Component ID | Description         | From     | To       | Qty | Notes                        |
|--------------|---------------------|----------|----------|-----|------------------------------|
| ADP-001      | SFF-8470 → SFF-8088 | SFF-8470 | SFF-8088 | ?   | Passive; alternative to CBL-SAS-003 if cabling via adapter |
