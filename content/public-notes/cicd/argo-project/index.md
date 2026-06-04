---
title: "Argo"
date: 2024-01-01
draft: false
showReadingTime: false
layout: single
tags: ["argo", "argocd", "argo-workflows", "argo-rollouts", "argo-events", "kargo", "kubernetes", "gitops"]
---

The Argo project is a suite of Kubernetes-native tools for running and managing workloads and deployments. Each tool solves a distinct problem and they compose well together, but they are independent — you can use any one without the others. All four are CNCF graduated or incubating projects.

## ArgoCD

GitOps continuous delivery. ArgoCD watches a Git repository and continuously reconciles the cluster state to match it — any drift is detected and corrected automatically. It is the CD half of a modern Kubernetes delivery pipeline: a CI system builds and pushes an image, ArgoCD detects the new tag and rolls it out. See the [ArgoCD](/public-notes/cicd/argo-cd/) note for a full walkthrough including App of Apps, bootstrapping, and self-management.

## Argo Workflows

A general-purpose workflow execution engine for Kubernetes. Workflows are CRDs that define DAGs or sequential step graphs — each step runs in a container, with outputs passed as artifacts or parameters to downstream steps. Used for CI pipelines, ML training jobs, data processing, and batch workloads. Where Tekton models CI-specific primitives (Tasks, Pipelines), Argo Workflows is lower-level and more flexible: any containerised workload that has dependencies between steps fits the model.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
spec:
  entrypoint: build-test
  templates:
    - name: build-test
      dag:
        tasks:
          - name: build
            template: run-step
            arguments:
              parameters: [{name: cmd, value: "make build"}]
          - name: test
            dependencies: [build]
            template: run-step
            arguments:
              parameters: [{name: cmd, value: "make test"}]
    - name: run-step
      inputs:
        parameters:
          - name: cmd
      container:
        image: golang:1.22
        command: [sh, -c]
        args: ["{{inputs.parameters.cmd}}"]
```

## Argo Rollouts

Progressive delivery for Kubernetes. Where a standard Kubernetes `Deployment` does a rolling update (replace pods gradually), Argo Rollouts adds canary and blue-green strategies with analysis gates. A canary rollout shifts a percentage of traffic to the new version, runs automated analysis (checking metrics from Prometheus, Datadog, or similar), and either promotes fully or rolls back based on the result. This makes deployments measurably safer — a bad release fails the analysis gate before it reaches 100% of traffic.

## Argo Events

Event-driven automation. Argo Events defines `EventSources` (sensors that listen for events — git pushes, S3 uploads, Kafka messages, webhooks, cron schedules) and `Sensors` (triggers that respond to those events by creating Argo Workflows, sending notifications, or calling other systems). It is the event bus that ties the rest of the Argo stack together: a git push fires an EventSource, a Sensor detects it and creates a Workflow, the Workflow builds and tests, ArgoCD picks up the new image and rolls it out.

## Kargo

A newer tool from Akuity (the company behind ArgoCD) that solves multi-stage GitOps promotion. ArgoCD is good at keeping one environment in sync with a Git ref — but promoting a release through dev → staging → production requires updating that ref in each environment and coordinating the sequence. Kargo models this as `Stages` with `FreightRequests` — a release is a piece of freight that must pass through each stage in order, with optional approval gates between them. It sits above ArgoCD in the stack and handles the promotion logic that ArgoCD deliberately leaves out.

## Resources

- [Argo project](https://argoproj.github.io/)
- [Argo Workflows documentation](https://argoproj.github.io/argo-workflows/)
- [Argo Rollouts documentation](https://argoproj.github.io/argo-rollouts/)
- [Argo Events documentation](https://argoproj.github.io/argo-events/)
- [Kargo documentation](https://docs.kargo.io/)
