---
title: "PXE Booting with OPNSense + iPXE"
description: "How to configure OPNsense as a PXE boot server — DHCP network boot options, TFTP setup, and an iPXE boot menu for Talos and other targets."
date: 2026-05-14
draft: false
tags: ["pxe", "ipxe", "opnsense", "tftp", "talos", "bare-metal"]
showReadingTime: false
---

How to configure OPNSense as a PXE boot server using its built-in DHCP and TFTP services, and how to write an iPXE boot menu that can chainload Talos Linux (or anything else).

---

## OPNSense DHCP — Network Boot Fields

`Services → ISC DHCPv4 → [LAN] → Network Booting`

| Field                          | Value                                |
|--------------------------------|--------------------------------------|
| Enable network booting         | ✓                                    |
| Next-server IP                 | `192.168.1.1` (OPNSense LAN address) |
| Default BIOS filename          | `undionly.kpxe`                      |
| x86 UEFI (32-bit) filename     | `ipxe.efi`                           |
| x64 UEFI/EBC (64-bit) filename | `ipxe.efi`                           |
| iPXE boot filename             | `default.ipxe`                       |

The DHCP server serves the correct boot file based on client architecture. BIOS clients get `undionly.kpxe`; UEFI clients get `ipxe.efi`. Both then chainload `default.ipxe`.

---

## TFTP — Downloading the Boot Files

OPNSense runs a TFTP server rooted at `/usr/local/tftp`. SSH in and fetch the iPXE binaries:

```sh
fetch -o /usr/local/tftp/undionly.kpxe https://boot.ipxe.org/undionly.kpxe
fetch -o /usr/local/tftp/ipxe.efi       https://boot.ipxe.org/ipxe.efi
```

---

## iPXE Boot Script

Save as `/usr/local/tftp/default.ipxe`. This example has a boot menu with options for netboot.xyz, a Talos Omni boot, and a debug shell.

```ipxe
#!ipxe

dhcp
set menu-timeout 5000

:start
menu PXE Boot Menu
item --gap -- ----------------------------
item netboot       Boot netboot.xyz
item talos         Boot Talos (Omni)
item shell         iPXE Shell
item --gap -- ----------------------------
choose target && goto ${target}

:netboot
chain http://boot.netboot.xyz || goto failed
goto start

:talos
echo Booting Talos via Omni...

set api   https://<your-omni-instance>.omni.siderolabs.io
set token <join-token>
set event [<siderolink-ipv6>]:8090
set log   tcp://[<siderolink-ipv6>]:8092

kernel tftp://${next-server}/talos/vmlinuz-omni \
  ima_template=ima-ng \
  ima_appraise=fix \
  ima_hash=sha512 \
  selinux=1 \
  consoleblank=0 \
  nvme_core.io_timeout=4294967295 \
  initrd=initramfs.xz \
  init_on_alloc=1 \
  slab_nomerge \
  pti=on \
  console=tty0 \
  console=ttyS0 \
  printk.devkmsg=on \
  talos.platform=metal \
  siderolink.api=${api}?jointoken=${token} \
  talos.events.sink=${event} \
  talos.logging.kernel=${log}

initrd tftp://${next-server}/talos/initramfs-omni.xz
boot || goto failed

:shell
shell

:failed
echo Boot failed, press Enter to continue...
read fake
goto start
```

The `api`, `token`, `event`, and `log` values come from the Omni console when you generate a join link.

---

## Talos Kernel and Initramfs — Image Factory

The standard Talos release binaries do not include firmware for all hardware. Since Talos 1.6, several older NIC drivers (including Broadcom BNX2 / BCM5709) were removed from the mainline image and made available as extensions via the image factory.

Generate a custom image at [factory.talos.dev](https://factory.talos.dev) with the extensions you need (e.g. `siderolabs/bnx2`), then download the PXE artifacts:

```sh
mkdir -p /usr/local/tftp/talos

fetch -o /usr/local/tftp/talos/vmlinuz-omni \
  "https://pxe.factory.talos.dev/image/<IMAGE_ID>/v1.10.1/kernel-amd64"

fetch -o /usr/local/tftp/talos/initramfs-omni.xz \
  "https://pxe.factory.talos.dev/image/<IMAGE_ID>/v1.10.1/initramfs-amd64.xz"
```

Replace `<IMAGE_ID>` with the schematic ID from the image factory, and adjust the version tag as needed.

---

## Gotchas

**UEFI boot and NIC memory limits** — `ipxe.efi` can be too large to fit in the NIC's PXE memory buffer on some older hardware. If the UEFI chain fails silently, switch to BIOS/legacy mode and use `undionly.kpxe` instead.

**DHCP options 66/67 conflict** — If you have previously set DHCP options 66 (next-server) and 67 (boot file) as raw additional options, remove them. OPNSense's built-in network boot fields handle this; having both causes conflicts.

**BIOS boot order after first boot** — Talos writes its own bootloader on first boot. If the BIOS is set to PXE as the primary device, the machine will fall back to the PXE menu on every subsequent reboot. Set disk as the primary boot device once the cluster is up.
