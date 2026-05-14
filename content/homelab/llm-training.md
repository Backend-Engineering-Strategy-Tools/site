---
title: "LLM Training on Bare Metal"
date: 2026-05-14
draft: true
showReadingTime: false
layout: single
tags: ["llm", "openstack", "slurm", "bare-metal", "pxe", "gpu", "training"]
---

Batch LLM training jobs on the lab hardware. The idea is to treat the blades as a proper compute cluster — PXE provisioned, OpenStack-managed, Slurm-scheduled — rather than manually SSHing into nodes to kick off runs.

---

## Goal

Run reproducible fine-tuning and training jobs on the [blade nodes](/homelab/inventory/systems/) (BLADE-01 through BLADE-16 in ASGARD) using a workflow that resembles how production ML clusters actually operate. OpenStack handles compute/network/storage abstraction; Slurm handles job scheduling and GPU allocation.

The models will be small. The point is the infrastructure, not the output.

The specific motivation here is to run all three systems together: OpenStack, Slurm, and a Kubernetes cluster (Talos on [ODEN](/homelab/inventory/systems/)). Each of these is interesting on its own; getting them to coexist and hand off work to each other is the experiment. A simpler approach — just `sbatch` directly on bare metal — would produce a trained model faster, but that's not the question being asked.

---

## Stack

| Layer | Technology | Role |
|---|---|---|
| Provisioning | PXE + iPXE | Boot nodes from bare metal |
| IaaS | [OpenStack](/public-notes/cloud-infrastructure/openstack/) | Compute, network, storage abstraction |
| Scheduling | [Slurm](/public-notes/cloud-infrastructure/slurm/) | Job queue, GPU allocation, preemption |
| Training | PyTorch + Hugging Face | Actual training workload |
| Storage | Ceph / NFS | Shared model weights and datasets |

---

## Hardware

The BL460c Gen8 blades are CPU-only — no discrete GPU. Training will be CPU-distributed or, if the GTX 770 gets placed in [ODEN (SYS-005)](/homelab/inventory/systems/), single-node GPU-assisted.

| Asset | Role | Notes |
|---|---|---|
| BLADE-01 – BLADE-16 | Slurm compute nodes | Dual Xeon, no GPU |
| [ODEN (SYS-005)](/homelab/inventory/systems/) | GPU node candidate | PCIe x16 riser, GTX 770 target |
| [MIMIR (SYS-004)](/homelab/inventory/systems/) | Storage | Dell PowerVault MD1200, 12× SAS/SATA |

Realistically: fine-tuning a small quantized model (3B) on the GTX 770's 2GB VRAM will be very constrained. CPU training on the blades is the more practical path for now.

---

## Open Decisions

- OpenStack flavor design for GPU passthrough to a Slurm node
- Slurm partition layout: separate CPU and GPU partitions, or single heterogeneous partition
- Training framework: PyTorch DDP across blade nodes, or LoRA fine-tuning on single GPU
- Dataset and model storage: Ceph (already planned for the lab) or simple NFS share

---

## Next Steps

1. Get OpenStack running on the blades (see [OpenStack](/public-notes/cloud-infrastructure/openstack/) note)
2. Install Slurm across blade nodes
3. Place GTX 770 in ODEN, verify GPU passthrough under OpenStack
4. Run a minimal `sbatch` job — even a hello-world that reports GPU availability
5. Fine-tune a small model (e.g., Phi-3 mini, TinyLlama) with LoRA

---

*Planning phase. None of this is running yet.*
