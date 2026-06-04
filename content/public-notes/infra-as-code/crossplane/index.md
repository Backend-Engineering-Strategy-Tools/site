---
title: "Crossplane"
date: 2026-06-03
draft: false
showReadingMode: false
layout: single
tags: ["crossplane", "kubernetes", "iac", "cloud-native", "operator"]
---

Crossplane is Kubernetes-native infrastructure management. Where Terraform runs as a CLI tool that applies changes and exits, Crossplane runs as a controller inside a Kubernetes cluster and continuously reconciles infrastructure — the same control loop model as Kubernetes itself.

Cloud resources become Kubernetes objects. You `kubectl apply` an RDS instance the same way you apply a Deployment. Crossplane's controllers watch those objects and make the API calls to converge actual infrastructure to the desired state.

---

## Core concepts

**Providers** extend Crossplane with CRDs for a specific cloud. `provider-aws` adds Kubernetes resources for every AWS service — S3 buckets, RDS instances, VPCs. Apply a provider, get hundreds of new resource types.

**Managed Resources (MRs)** are the individual cloud resources:

```yaml
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  name: my-assets
spec:
  forProvider:
    region: eu-central-1
    tags:
      Environment: prod
```

Crossplane creates this bucket and keeps it in sync. If someone deletes it outside of Crossplane, the controller recreates it.

**Composite Resources (XRs)** are the powerful part. You define your own CRDs — a `Platform` or `DatabaseCluster` — that compose multiple managed resources. A developer applies a `DatabaseCluster` and gets an RDS instance, a subnet group, a parameter group, and security groups, all wired together, without needing to know any of the details.

**XRDs (Composite Resource Definitions)** define the schema for composite resources — what fields the developer sees, what defaults apply.

**Compositions** define how a composite resource maps to managed resources — the implementation behind the abstraction.

---

## The platform engineering model

Crossplane's real value is as a platform layer. A platform team owns the Compositions — they define what a "compliant database" or "standard app environment" looks like. Dev teams consume the simplified abstractions without touching the underlying cloud resources.

Self-service infrastructure with guardrails baked in.

---

## vs Terraform

Crossplane and Terraform are not direct alternatives — they solve the problem differently.

Terraform is a CLI tool: run plan, review, apply, exit. State is a file. Good for human-in-the-loop workflows and one-off provisioning.

Crossplane is a control plane: always running, always reconciling. Better for continuous enforcement and self-service platforms. More complex to set up and operate.

In practice: Terraform for provisioning foundational infrastructure (clusters, networks, accounts). Crossplane for what runs on top of the cluster — letting application teams provision their own databases, queues, and object storage through Kubernetes-native APIs.

---

## Upbound

The commercial platform behind Crossplane. Managed control plane hosting, a marketplace of providers and compositions, and tooling for building and publishing your own platform APIs. Worth evaluating if you are building a serious internal platform.

---

## Learning curve

Steep. You need to understand Kubernetes controllers, CRDs, and the Crossplane composition model before you can be productive. The payoff is a genuinely powerful platform abstraction — but it is not a beginner tool.

A good framing: Crossplane is a **digital twin of your infrastructure**. The cluster holds the desired state of everything — cloud resources, application configuration, other tools — and continuously reconciles reality to match it.

Genuinely cool and worth learning if you have a cluster. The provider model has expanded well beyond cloud infrastructure — from v2 onwards Crossplane can manage applications, not just infra. There are also providers for Ansible and Terraform/OpenTofu, which means Crossplane can be the orchestration layer that drives other IaC tools. One control plane to rule them all.

The prerequisite is the cluster itself. If you already run Kubernetes, Crossplane is a natural extension of the same model you already operate. If you do not, it is not the tool to start with.
