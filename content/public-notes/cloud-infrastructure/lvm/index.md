---
title: "LVM — Logical Volume Manager"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["lvm", "storage", "linux", "block-storage"]
---

LVM adds a virtualisation layer between physical disks and filesystems. Instead of formatting a disk partition directly, you assemble physical volumes into a volume group and carve logical volumes out of the pool. This makes resizing, snapshots, and spanning volumes across multiple disks straightforward operations rather than destructive partition table surgery.

## Layers

| Layer                | Description                                                                     |
|----------------------|---------------------------------------------------------------------------------|
| Physical Volume (PV) | A disk or partition initialised for LVM use (`pvcreate`)                        |
| Volume Group (VG)    | A pool of storage assembled from one or more PVs                                |
| Logical Volume (LV)  | A virtual partition carved from a VG, formatted and mounted like a regular disk |

```bash
# Initialise two disks as PVs
pvcreate /dev/sdb /dev/sdc

# Create a VG from both
vgcreate data-vg /dev/sdb /dev/sdc

# Create an LV using all available space
lvcreate -l 100%FREE -n data-lv data-vg

# Format and mount
mkfs.ext4 /dev/data-vg/data-lv
mount /dev/data-vg/data-lv /mnt/data
```

## Resizing

The practical benefit over raw partitions: extend a logical volume online without unmounting:

```bash
# Extend the LV by 50GB
lvextend -L +50G /dev/data-vg/data-lv

# Grow the filesystem to fill the new space
resize2fs /dev/data-vg/data-lv
```

## Snapshots

LVM supports copy-on-write snapshots. A snapshot captures the LV state at a point in time and stores only the blocks that change afterwards:

```bash
lvcreate -L 10G -s -n data-snap /dev/data-vg/data-lv
```

Used for consistent backups of live filesystems — snapshot, back up the snapshot, remove it. Rook/Ceph and cloud providers use similar snapshot semantics at the storage layer.

## Resources

- [LVM2 documentation](https://sourceware.org/lvm2/)
- [Red Hat LVM administration guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/configuring_and_managing_logical_volumes/)
