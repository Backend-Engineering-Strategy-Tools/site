---
title: "Hardware Provisioning: PXE Booting and Tooling"
description: "Overview of bare-metal provisioning tooling — from Cobbler and Foreman to Tinkerbell and Matchbox, and where each fits in the landscape."
date: 2026-05-12
draft: false
tags: ["pxe", "bare-metal", "provisioning", "cobbler", "foreman", "ironic", "rebar"]
showReadingTime: false
layout: single
---

When moving beyond manual installs, managing hardware lifecycle through PXE (Preboot Execution Environment) becomes essential. A breakdown of common tools for automating the "power-on to OS ready" process.

---

## Common starting points

| Tool | Focus | Complexity | Best for |
|---|---|---|---|
| [Cobbler](https://cobbler.github.io/) | PXE/repo server | Low–Medium | Stable, static environments needing reliable kickstart or seed installs |
| [Foreman](https://theforeman.org/) | Full lifecycle mgmt | High | Single pane of glass for provisioning + ongoing config management (Puppet/Ansible) |
| [Digital Rebar](https://rebar.digital/) | Infrastructure-as-Code | Medium | Modern DevOps teams wanting cloud-like speed on physical gear; evolved from Crowbar |
| [Ironic](https://wiki.openstack.org/wiki/Ironic) / [Bifrost](https://docs.openstack.org/bifrost/latest/) | BMaaS / scale | High | Bare Metal as a Service at scale; Bifrost runs Ironic standalone without full OpenStack |

---

## Broader landscape

### Classic PXE / Provisioning

| Tool | Type | Strengths | Weaknesses |
|---|---|---|---|
| Cobbler | PXE provisioning server | Simple, mature, easy to understand | Old architecture, static workflows |
| Foreman | Lifecycle/provisioning platform | Powerful, enterprise-capable, large ecosystem | Heavy footprint, Rails monolith |
| Uyuni | Systems management | Enterprise lifecycle management (SUSE/Spacewalk lineage) | Less modern provisioning architecture |

### Dynamic / Policy-Driven

| Tool | Type | Strengths | Weaknesses |
|---|---|---|---|
| Razor | Policy-driven provisioning | Dynamic node discovery, elegant lifecycle model | Effectively dormant |
| Digital Rebar | Workflow provisioning platform | Architecturally modern and flexible | Partially commercialized |

### Cloud / Hyperscale Bare Metal

| Tool | Type | Strengths | Weaknesses |
|---|---|---|---|
| Ironic | OpenStack bare-metal service | Extremely scalable, API-driven | High operational complexity |
| Bifrost | Standalone Ironic deployment | Easier entry into Ironic ecosystem | Inherits Ironic complexity |
| MAAS | Bare metal cloud platform | Excellent UX, API-first, machine discovery | Larger footprint, Ubuntu-centric |

### Kubernetes-Native / Cloud-Native

| Tool | Type | Strengths | Weaknesses |
|---|---|---|---|
| Tinkerbell | Cloud-native provisioning | Modern architecture, composable workflows | Microservice complexity |
| Metal3 | Kubernetes operator | Native Kubernetes integration | Requires Kubernetes infrastructure |
| Omni | Talos cluster orchestration | Very modern UX and lifecycle management | Talos/Kubernetes specific |
| Matchbox | Minimal PXE/ignition service | Elegant, simple, iPXE-first | Narrow immutable-infra focus |

### Boot Infrastructure / PXE Utilities

| Tool | Type | Strengths | Weaknesses |
|---|---|---|---|
| iPXE | Network boot firmware | Flexible, fast, programmable (HTTP + scripting) | Requires infrastructure around it |
| netboot.xyz | Dynamic network boot menu | Extremely useful and lightweight | Not a provisioning orchestrator |

---

## Architectural Styles

| Style | Example Tools | Characteristics |
|---|---|---|
| Static config-driven | Cobbler | Profiles + templates + PXE configs |
| Policy/state-driven | Razor, Digital Rebar | Nodes discovered dynamically, assigned via policies |
| Cloud resource model | Ironic, MAAS | Bare metal treated as cloud infrastructure |
| Kubernetes-native | Tinkerbell, Metal3 | Bare metal managed via Kubernetes APIs |
| Immutable OS orchestration | Omni, Matchbox | Minimal provisioning around immutable operating systems |

---

## The Gap

There is still no widely adopted FOSS solution that is simultaneously:

- lightweight
- modern
- self-hostable
- API-first
- iPXE-native
- distro-agnostic
- easy to operate
- single-binary deployable
- workflow-capable
- not tied to Kubernetes/OpenStack

Most existing systems drift toward enterprise complexity, cloud platform assumptions, Kubernetes dependency, immutable OS specialization, or monolithic lifecycle management.

> "A modern lightweight provisioning orchestrator for reproducible bare-metal infrastructure."
