---
title: "Security Scanning & Monitoring"
date: 2024-01-01
draft: false
showReadingTime: false
layout: single
tags: ["security", "clair", "osquery", "snort", "scanning", "ids", "monitoring"]
---

Security tooling broadly splits into three concerns: what vulnerabilities exist in your software before it runs (image scanning), what is actually happening on your systems while they run (endpoint monitoring), and what is moving across your network (intrusion detection). Clair, osquery, and SNORT each cover one of these.

## Clair

A static analysis tool for container image vulnerability scanning, from the Quay project (Red Hat). Clair maintains a database of CVEs from multiple sources (NVD, Red Hat, Debian, Alpine, Ubuntu) and matches them against the packages installed in a container image layer by layer. Integrated into a container registry, it scans every image on push and blocks or flags images with known vulnerabilities above a configurable severity threshold. The result is a vulnerability report tied to the image digest — not the running container, but the image itself before it's ever deployed.

## osquery

Facebook's open source endpoint monitoring tool. osquery exposes the operating system as a relational database — processes, users, network connections, installed packages, kernel modules, scheduled tasks, browser extensions — all queryable with SQL. This makes ad-hoc security investigation fast (a single query answers "which processes are listening on unexpected ports?") and continuous monitoring straightforward (schedule queries, collect results centrally, alert on anomalies). osquery runs on Linux, macOS, and Windows. Used standalone it is a powerful investigation tool; integrated with a SIEM or fleet management layer (Fleet, Kolide) it becomes a continuous compliance and detection platform.

```sql
-- Processes with open network connections
SELECT p.name, p.pid, l.address, l.port
FROM processes p
JOIN listening_ports l ON p.pid = l.pid
WHERE l.port NOT IN (22, 80, 443);
```

## SNORT

A network intrusion detection and prevention system (IDS/IPS). SNORT inspects network traffic in real time against a ruleset — signatures for known attack patterns, protocol anomalies, port scans, exploit attempts. In IDS mode it logs and alerts; in IPS mode it can drop matching packets inline. SNORT rules are expressive and the community ruleset (Snort Community Rules, Emerging Threats) covers a wide range of threats. Placed at a network chokepoint — in front of a server, at the edge of a network segment — it gives visibility into what traffic is actually reaching your systems and can detect lateral movement, exfiltration attempts, and known exploits in transit.

## Resources

- [Clair documentation](https://quay.github.io/clair/)
- [osquery documentation](https://osquery.readthedocs.io/)
- [SNORT documentation](https://www.snort.org/documents)
- [Emerging Threats ruleset](https://rules.emergingthreats.net/)
