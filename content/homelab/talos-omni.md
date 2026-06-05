---
title: "Talos Linux in the homelab via Omni"
description: "Getting Talos Linux running via PXE boot and Omni on an IBM x3550 M3 — what actually happened, in order."
date: 2026-05-14
draft: false
showReadingTime: false
layout: single
tags: ["talos", "omni", "pxe", "kubernetes", "bare-metal"]
---

Getting [Talos Linux](/public-notes/kubernetes/talos/) running in the homelab via PXE boot and [Omni](https://omni.siderolabs.com) — starting with [ODEN (SYS-005)](/homelab/inventory/systems/), an IBM System x3550 M3. The full OPNSense + iPXE configuration lives in the [reference note](/public-notes/hardware/hardware-provisioning/ipxe-opnsense/); this covers what actually happened, in order.

---

## Setup

**Hardware**: ODEN (SYS-005) — IBM x3550 M3, Broadcom BNX2 NICs (BCM5709)  
**Network**: OPNSense router on LAN; ODEN connected via one NIC (start with one — removes variables)  
**Target**: Single-node Talos cluster registered in Omni

---

## Step 1 — OPNSense DHCP and TFTP

Enable network booting on the LAN DHCP server and download the iPXE binaries to the TFTP root. Full field values in the [iPXE reference note](/public-notes/hardware/hardware-provisioning/ipxe-opnsense/).

One thing to check first: if you previously set DHCP options 66 and 67 as raw additional options, remove them. OPNSense's built-in network boot fields do the same job and having both causes conflicts.

---

## Step 2 — iPXE boot script

Write `default.ipxe` to `/usr/local/tftp/`. Include a boot menu with at minimum a Talos option and a shell fallback — the shell is genuinely useful when something fails and you need to debug from the boot prompt. Full script in the [reference note](/public-notes/hardware/hardware-provisioning/ipxe-opnsense/).

The Talos entry in the menu needs the Omni join token from your Omni console. Generate a join link in Omni; it provides the API endpoint, token, and SideroLink addresses.

---

## Step 3 — Talos kernel and initramfs

The standard Talos release binaries do not include BNX2 firmware. Since around Talos 1.6 those drivers are available as extensions but not in the mainline image. Without them, the node boots, fails to initialise the NIC, and produces `can't load firmware bnx2` errors — everything else looks fine until you notice the node never gets an IP and never appears in Omni.

Fix: generate a custom image at [factory.talos.dev](https://factory.talos.dev) with the `siderolabs/bnx2` extension included, then download the PXE kernel and initramfs from the factory URL. Commands in the [reference note](/public-notes/hardware/hardware-provisioning/ipxe-opnsense/).

---

## Step 4 — First boot

Go into BIOS and set the boot device to PXE. On the M3, UEFI boot with `ipxe.efi` fails silently — the image is too large for the NIC's PXE memory buffer. Switch to legacy/BIOS mode and use `undionly.kpxe` instead.

The machine takes a while to POST and boot. This is normal for old enterprise hardware. It is also why demos typically use virtual machines.

---

## Step 5 — Static IP

After the BNX2 fix the node boots Talos successfully but still does not appear in Omni. The DHCP assignment for the node is not being picked up during early boot. Workaround: add a static IP via kernel params in the iPXE script:

```ipxe
ip=192.168.1.171::192.168.1.1:255.255.255.0::eth0:off
```

Add this to the `kernel` line in the Talos iPXE entry. The format is `ip=<client-ip>::<gateway>:<netmask>::<iface>:off`.

---

## Step 6 — Omni registration

With a working NIC and an IP, the node contacts the Omni API using the join token. It appears in the Omni console as an unallocated machine. Create a cluster, assign the machine, and let Omni configure it. The initial cluster bootstrap takes a few minutes.

---

## Step 7 — Fix the BIOS boot order

After the cluster is up, change the BIOS boot order so the disk is first. If PXE remains the primary boot device, every reboot drops the machine back to the iPXE menu instead of booting the installed Talos. Discovered on first reboot. Worth noting it here so you don't make the same trip to the garage.

---

## Upgrade

Omni makes single-node upgrades straightforward: open the cluster in the Omni console, select a new Talos version, apply. The node reboots once. Single-node means the cluster has downtime during the reboot; that is expected. Nothing else to do.

---

## Result

Single-node Kubernetes cluster running on ODEN, managed via Omni. `kubectl` and `talosctl` access via the Omni CLI. Next experiment: [Rook + Ceph](/homelab/rook-ceph/) for persistent storage.
