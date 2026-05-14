---
title: "Talos Linux + Omni"
description: "Talos Linux reference — immutable, API-managed OS for Kubernetes, with notes on Omni cluster management and the Image Factory."
date: 2026-05-14
draft: false
tags: ["talos", "omni", "kubernetes", "immutable", "bare-metal"]
showReadingTime: false
layout: single
---

Talos Linux is an immutable, minimal operating system designed specifically for running Kubernetes. There is no shell, no SSH, no package manager. The entire OS is read-only and managed via a gRPC API (`talosctl`). Node configuration is declarative YAML applied over the API; changes that require a reboot take effect on the next boot.

The tradeoff is rigidity for operational simplicity. You cannot log into a Talos node and fix something by hand. In return, nodes are deterministic, reproducible, and there is no configuration drift.

---

## Comparison to other installs

| Method | OS | Config | Mutable |
|---|---|---|---|
| kubeadm | Ubuntu / RHEL / etc | Manual + scripts | Yes |
| k3s | Any Linux | Minimal | Yes |
| Talos | Talos Linux | Declarative API | No |

k3s and kubeadm give you more flexibility and a familiar Linux environment. Talos is the right choice when you want the cluster nodes to behave like appliances — provisioned, never touched.

---

## Omni

[Omni](https://omni.siderolabs.com) is a cluster management platform by Sidero Labs built on top of Talos. It handles:

- Node registration (nodes boot and phone home to the Omni API)
- Cluster creation and machine assignment
- Kubernetes upgrades (one action in the UI)
- `talosctl` and `kubeconfig` access via the Omni CLI

Nodes register via a join token embedded in the kernel command line at PXE boot time. The cluster runs on your hardware; Omni only manages the control plane.

**Hobby tier**: 10 nodes, non-commercial use, free. Sidero Labs also offers a self-hosted version.

---

## Image Factory

[factory.talos.dev](https://factory.talos.dev) generates custom Talos images with hardware extensions included. Notable extensions:

- `siderolabs/bnx2` — Broadcom NetXtreme II (BCM5708/BCM5709) NIC firmware, required on some enterprise hardware (IBM x3550 M3, HP Gen 6/7 blades)
- `siderolabs/intel-ucode` — Intel microcode updates
- `siderolabs/nvidia-*` — NVIDIA GPU support

The factory produces both ISO and PXE artifacts (kernel + initramfs). See the [OPNSense + iPXE reference](/public-notes/cloud-infrastructure/hardware-provisioning/ipxe-opnsense/) for how to serve these over TFTP.

---

## Supporting Sidero Labs

Talos and Omni are built by [Sidero Labs](https://github.com/siderolabs) — good people doing good work. I sponsor them via [GitHub Sponsors](https://github.com/sponsors/siderolabs) at the fanboi tier.

---

## Relevant links

- [Talos Linux docs](https://www.talos.dev/latest/)
- [Omni docs](https://omni.siderolabs.com/docs)
- [Image factory](https://factory.talos.dev)
- [Sidero Labs GitHub](https://github.com/siderolabs)
- [Sponsor Sidero Labs](https://github.com/sponsors/siderolabs)
