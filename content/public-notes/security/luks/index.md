---
title: "LUKS — Linux Disk Encryption"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["luks", "encryption", "linux", "security", "disk"]
---

LUKS (Linux Unified Key Setup) is the standard for full-disk encryption on Linux. It uses dm-crypt in the kernel to encrypt block devices transparently — the filesystem sits on top of an encrypted layer, and the encryption happens below it. The LUKS header stores the encrypted key material and metadata, supporting up to eight independent key slots (passphrases or keyfiles) that all unlock the same volume.

## Setup

```bash
# Encrypt a device (destroys existing data)
cryptsetup luksFormat /dev/sdb

# Open the encrypted device, exposing it as a plaintext mapper device
cryptsetup luksOpen /dev/sdb data-encrypted

# Format and use the plaintext device normally
mkfs.ext4 /dev/mapper/data-encrypted
mount /dev/mapper/data-encrypted /mnt/data

# Close when done
umount /mnt/data
cryptsetup luksClose data-encrypted
```

## Key slots

LUKS supports multiple passphrases or keyfiles — useful for adding a recovery key alongside an operational passphrase:

```bash
# Add a second key slot (e.g. a recovery keyfile)
cryptsetup luksAddKey /dev/sdb /path/to/recovery.key

# Remove a key slot
cryptsetup luksRemoveKey /dev/sdb

# List key slot usage
cryptsetup luksDump /dev/sdb
```

## Auto-unlock at boot

For encrypted root or data partitions that should unlock automatically on boot, add the device to `/etc/crypttab` with a keyfile path:

```
data-encrypted  /dev/sdb  /etc/keys/data.key  luks
```

Then add the plaintext device to `/etc/fstab` as normal. On servers, the keyfile is stored on a separate volume or fetched from a secrets manager (Vault, Tang/Clevis for network-bound disk encryption).

## Use in Kubernetes

Node-level disk encryption with LUKS protects data at rest on Kubernetes worker nodes — persistent volume data stored on the node's disks is encrypted before it leaves the kernel. Talos Linux enables LUKS encryption for its state and ephemeral partitions by default.

## Resources

- [cryptsetup documentation](https://gitlab.com/cryptsetup/cryptsetup/-/wikis/home)
- [dm-crypt reference](https://wiki.archlinux.org/title/dm-crypt)
