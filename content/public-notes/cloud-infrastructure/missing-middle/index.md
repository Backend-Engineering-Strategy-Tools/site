---
title: "The Missing Middle: A Modern Bare-Metal Provisioner"
date: 2026-05-12
draft: true
tags: ["bare-metal", "provisioning", "pxe", "project"]
showReadingTime: false
layout: single
---

## Vision

Build a modern FOSS provisioning platform that bridges the gap between simplistic PXE scripting and heavyweight cloud provisioning stacks.

Target users:
- homelabs
- SMB infrastructure
- edge deployments
- AI/GPU clusters
- lightweight Kubernetes environments
- reproducible bare-metal labs

---

## Core Design Principles

| Principle                     | Description                                  |
|-------------------------------|----------------------------------------------|
| iPXE-first                    | HTTP-based dynamic booting                   |
| API-first                     | All provisioning driven via APIs             |
| Stateless boot orchestration  | Dynamic script generation                    |
| Policy-driven                 | Runtime classification of machines           |
| Event-driven                  | Machine lifecycle transitions                |
| Minimal operational footprint | Single binary deployment                     |
| Optional DHCP management      | Coexist with existing networks               |
| Immutable-friendly            | Support cloud-init / ignition workflows      |
| Extensible                    | Hooks/events instead of giant plugin systems |

---

## Proposed Architecture

```text
               Web UI / REST API
                        │
                        ▼
             Provisioning Core Engine
       ┌────────────────────────────────┐
       │ Node discovery/state machine   │
       │ Policy engine                  │
       │ Inventory                      │
       │ Template rendering             │
       │ Event bus                      │
       └────────────────────────────────┘
            │         │           │
            ▼         ▼           ▼
         DHCP      iPXE/HTTP   Metadata API
       (optional)   Boot        cloud-init
```

---

## Core Components

### 1. Discovery Engine

Responsibilities:
- detect unknown nodes
- collect hardware metadata
- manage lifecycle states

Example states:

```text
NEW → DISCOVERED → CLASSIFIED → INSTALLING → ACTIVE
```

### 2. Policy Engine

Example:

```yaml
match:
  manufacturer: Dell
  ram_gb: ">=128"

action:
  image: ubuntu-24.04
  role: k8s-worker
```

### 3. Boot Orchestrator

Dynamic iPXE generation:

```ipxe
#!ipxe

kernel http://srv/images/vmlinuz \
  initrd=initrd.img \
  ip=dhcp \
  cloud-config-url=http://srv/meta/node123

initrd http://srv/images/initrd.img
boot
```

### 4. Metadata Service

Generates:
- cloud-init
- ignition
- autoinstall
- SSH keys
- network config
- cluster bootstrap data

### 5. Artifact Store

Serves kernels, initrds, rootfs images, installers, ISO artifacts.  
Prefer HTTP and OCI/S3 compatible storage.

---

## Suggested Tech Stack

| Layer     | Suggested Tech            |
|-----------|---------------------------|
| Language  | Go or Rust                |
| API       | REST/gRPC                 |
| DB        | SQLite/Postgres           |
| Boot      | iPXE                      |
| Templates | Go templates / Jinja-like |
| Eventing  | NATS or internal bus      |
| Storage   | Local FS / S3             |
| UI        | React/Vue optional        |
| Auth      | OIDC-compatible           |

---

## Non-Goals

Avoid:
- full OpenStack integration
- embedded configuration management
- giant plugin ecosystems
- Kubernetes dependency
- distro-specific lock-in
- enterprise-only complexity

---

## Potential Killer Features

- Reproducible bare-metal cluster deployments
- Fast Talos/K3s/Proxmox bootstrap
- Simple edge cluster provisioning
- Dynamic hardware classification
- GitOps-style provisioning definitions
- API-driven ephemeral labs
- "PXE as code"

---

## Positioning

> "Modern bare-metal provisioning without OpenStack."

Or:

> "Terraform-style workflows for PXE and bare metal."
