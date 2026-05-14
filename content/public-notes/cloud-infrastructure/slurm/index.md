---
title: "Slurm"
description: "Slurm reference — workload manager and job scheduler for HPC and ML training, optimising for maximum GPU utilisation over uptime."
date: 2026-05-14
draft: false
tags: ["slurm", "hpc", "scheduler", "bare-metal", "ml", "training"]
showReadingTime: false
layout: single
---

Slurm (Simple Linux Utility for Resource Management) is a workload manager and job scheduler. It originated in HPC but is now the standard scheduler for ML training clusters — most cloud GPU clusters (AWS, GCP, Azure HPC) run Slurm under the hood.

https://slurm.schedmd.com/

---

## Core Concepts

**Node** — a compute host registered with Slurm. Can have CPU, GPU, and memory resources defined.

**Partition** — a logical group of nodes (like a queue). You can have separate partitions for GPU and CPU nodes, or different priority tiers.

**Job** — a workload submitted to the queue. Slurm allocates resources, places the job, and tracks it to completion.

**Allocation** — the reserved resources (nodes, CPUs, GPUs, memory) for a running job.

---

## Key Commands

```bash
sbatch job.sh          # submit a batch job script
squeue                 # view the job queue
sacct -j <jobid>       # job accounting / history
sinfo                  # view partition and node state
scancel <jobid>        # cancel a job
srun --pty bash        # interactive allocation
```

A minimal batch script:

```bash
#!/bin/bash
#SBATCH --job-name=train
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --time=02:00:00

python train.py
```

---

## Slurm vs Kubernetes for Training

The fundamental difference is what each system optimises for:

**Kubernetes** optimises for uptime. It keeps services running, reschedules failed pods, and manages long-lived workloads. That's the right model for inference serving, APIs, and anything that needs to stay up.

**Slurm** optimises for utilisation. It packs jobs onto nodes as tightly as possible, queues work when resources are busy, and gets out of the way when a job finishes. That's the right model for batch training — you want every GPU busy, not reserved for availability.

| | Slurm | Kubernetes |
|---|---|---|
| Optimises for | Maximum utilisation | Uptime and availability |
| Scheduling model | Job queue, batch-first | Long-running services + batch (via operators) |
| GPU allocation | Native, fine-grained | Requires GPU operator + device plugin |
| Multi-node training | First-class (MPI, `srun`) | Possible via KubeFlow, PyTorchJob |
| Preemption | Built-in | Requires configuration |
| Operational overhead | Low on bare metal | Higher — requires cluster management |
| Ecosystem | HPC, academia, major cloud HPC | ML platforms, cloud-native |

**The short version:** use Slurm for pure batch training on bare metal. Use Kubernetes when you're mixing training with inference serving or need container-native workflows throughout — or when the cluster already exists.
