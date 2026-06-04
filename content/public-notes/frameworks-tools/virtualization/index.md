---
title: "Virtualization — KVM and KubeVirt"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["kvm", "kubevirt", "virtualization", "linux", "kubernetes", "qemu"]
---

KVM is the Linux kernel's native hypervisor. KubeVirt extends Kubernetes to run virtual machines using KVM under the hood. They are the same virtualization layer at different levels of abstraction — KVM on bare metal, KubeVirt in a Kubernetes cluster.

## KVM

Kernel-based Virtual Machine. KVM turns the Linux kernel into a hypervisor using hardware virtualization extensions (Intel VT-x, AMD-V). Virtual machines run as regular Linux processes backed by QEMU for device emulation. Managed via `libvirt` and its CLI tools (`virsh`, `virt-install`) or the `virt-manager` GUI.

```bash
# Create a VM from an ISO
virt-install \
  --name ubuntu-vm \
  --ram 4096 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/ubuntu.qcow2,size=40 \
  --cdrom /tmp/ubuntu.iso \
  --os-variant ubuntu22.04

# List running VMs
virsh list

# Start/stop
virsh start ubuntu-vm
virsh shutdown ubuntu-vm

# Connect to console
virsh console ubuntu-vm
```

KVM gives near-native performance for CPU-bound workloads. Network and disk I/O use virtio drivers for efficient paravirtualised I/O. Live migration moves a running VM between hosts without downtime if shared storage is available.

## KubeVirt

KubeVirt adds `VirtualMachine` and `VirtualMachineInstance` CRDs to Kubernetes. VMs are defined as Kubernetes resources, scheduled by the Kubernetes scheduler, and managed alongside containers. Under the hood, each VM runs as a pod containing a QEMU-KVM process.

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: ubuntu-vm
spec:
  running: true
  template:
    spec:
      domain:
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
        resources:
          requests:
            memory: 4Gi
            cpu: "2"
      volumes:
        - name: rootdisk
          containerDisk:
            image: kubevirt/fedora-cloud-container-disk-demo
```

The `virtctl` CLI complements `kubectl` for VM-specific operations:

```bash
virtctl start ubuntu-vm
virtctl stop ubuntu-vm
virtctl console ubuntu-vm    # serial console
virtctl ssh ubuntu-vm        # SSH via the Kubernetes API
virtctl migrate ubuntu-vm    # live migrate to another node
```

## CDI — Containerized Data Importer

KubeVirt is typically paired with CDI, which imports VM disk images from URLs, container registries, or PVCs into `DataVolume` resources that VMs can boot from. CDI handles the data flow; the VM definition just references the DataVolume.

## Why VMs in Kubernetes

Some workloads can't be containerised — legacy applications expecting a full OS, Windows workloads, software with kernel module requirements. KubeVirt lets those workloads live in the same cluster as containers, managed with the same tooling, subject to the same scheduling and networking policies.

## Resources

- [KVM documentation](https://www.linux-kvm.org/page/Documents)
- [KubeVirt documentation](https://kubevirt.io/user-guide/)
- [CDI documentation](https://github.com/kubevirt/containerized-data-importer)
