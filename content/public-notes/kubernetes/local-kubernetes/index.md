---
title: "Local Kubernetes"
date: 2024-01-01
draft: false
showReadingTime: false
layout: single
tags: ["kubernetes", "k3s", "k3d", "kind", "minikube", "microk8s", "local-dev"]
---

Running Kubernetes locally is useful for development, testing, and CI — a real cluster without the cloud bill. The options differ mainly in weight, startup speed, and whether they target local dev, CI pipelines, or lightweight production use.

## MiniKube

The original local Kubernetes, maintained by the Kubernetes project itself. Runs a single-node cluster inside a VM (VirtualBox, HyperKit) or a Docker container. The reference implementation — if something works in Kubernetes, it works in MiniKube. Slower to start than the container-based options, heavier on resources, but the most faithful representation of a real cluster. Good for getting started and for testing things that need VM-level isolation.

## Kind

Kubernetes IN Docker — each cluster node runs as a Docker container, no VM required. Fast startup (seconds), low overhead, and multi-node clusters are easy to spin up. The standard choice for running Kubernetes in CI pipelines: create a cluster, run tests, tear it down. The Kubernetes project itself uses Kind for conformance testing. Not designed for running workloads long-term, but excellent for ephemeral test environments.

## K3S

Lightweight Kubernetes from Rancher (now SUSE), packaged as a single binary under 100MB. It strips out cloud-provider integrations, in-tree storage drivers, and alpha features — the result is a fully conformant Kubernetes that runs on hardware where full K8s won't. Used in production for edge deployments, IoT, and resource-constrained environments. Also a good choice when you want a real persistent cluster locally without the overhead of MiniKube.

## K3D

K3S running inside Docker containers — the same relationship Kind has to standard Kubernetes. Fast, lightweight, multi-node clusters in Docker. The advantage over Kind is that K3S starts faster and uses less memory per node. Good choice for local dev and CI when you want the lightweight K3S runtime rather than full upstream Kubernetes.

## MicroK8S

Canonical's take on local Kubernetes, distributed as a snap package on Ubuntu. Single-command install, add-ons (DNS, storage, ingress, observability) enabled with `microk8s enable <addon>`. Opinionated and tightly integrated with the Ubuntu/Canonical ecosystem. The right choice if you're on Ubuntu and want a low-friction local cluster with batteries included — less so outside that ecosystem.

## Which to use

|              | Best for                                      |
|--------------|-----------------------------------------------|
| **MiniKube** | Getting started, testing with VM isolation    |
| **Kind**     | CI pipelines, ephemeral test clusters         |
| **K3S**      | Persistent local cluster, edge/IoT production |
| **K3D**      | Fast local dev and CI with K3S runtime        |
| **MicroK8S** | Ubuntu users wanting a managed local cluster  |

## Resources

- [MiniKube documentation](https://minikube.sigs.k8s.io/docs/)
- [Kind documentation](https://kind.sigs.k8s.io/)
- [K3S documentation](https://docs.k3s.io/)
- [K3D documentation](https://k3d.io/)
- [MicroK8S documentation](https://microk8s.io/docs)
