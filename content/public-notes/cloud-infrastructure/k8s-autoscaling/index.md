---
title: "Kubernetes Autoscaling"
date: 2024-01-01
draft: false
showReadingTime: false
layout: single
tags: ["kubernetes", "karpenter", "keda", "autoscaling", "scaling"]
---

Kubernetes has built-in autoscaling at two levels: the Horizontal Pod Autoscaler scales the number of pod replicas based on CPU or memory, and the Cluster Autoscaler adds or removes nodes when pods can't be scheduled. KEDA and Karpenter extend these primitives — KEDA pushing workload scaling further, Karpenter replacing the node provisioner entirely.

## KEDA

Kubernetes Event-Driven Autoscaling. KEDA extends the HPA to scale workloads based on external event sources — Kafka consumer lag, queue depth in SQS or RabbitMQ, HTTP request rate, database query results, cron schedules. The built-in HPA only knows about CPU and memory; KEDA adds a long list of scalers for external systems. The important capability it adds is scale-to-zero: a consumer that has no messages to process can scale down to zero pods and scale back up when work arrives. This makes it well-suited for event-driven workloads and batch processing where idle replicas waste resources.

## Karpenter

A node provisioner that replaces the Cluster Autoscaler, originally from AWS and now a CNCF project with support for other clouds. Where the Cluster Autoscaler works by adjusting existing Auto Scaling Groups, Karpenter provisions EC2 instances (or equivalent) directly based on the actual resource requirements of pending pods — choosing the right instance type, size, and purchase option (on-demand vs spot) in real time. This makes provisioning significantly faster and more cost-efficient: the cluster gets exactly the nodes the pending workload needs, not the nearest pre-configured node group. Karpenter also handles consolidation — continuously evaluating whether running workloads could be packed onto fewer nodes and replacing over-provisioned nodes accordingly.

## Resources

- [KEDA documentation](https://keda.sh/docs/)
- [KEDA scalers](https://keda.sh/docs/scalers/)
- [Karpenter documentation](https://karpenter.sh/docs/)
- [Karpenter concepts](https://karpenter.sh/docs/concepts/)
