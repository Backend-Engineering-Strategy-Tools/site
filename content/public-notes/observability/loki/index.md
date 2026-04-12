---
title: "Loki"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

[Prometheus](../prometheus/) tells you *that* something is wrong and *when* it started. Loki tells you *what* happened — it is the log aggregation layer of the observability stack. Logs from every pod across every node are collected, indexed, and made searchable in one place. Grafana is the front end for both.

## How it works

Loki stores logs as compressed chunks, indexed only by labels (not by content). This makes it cheap to store and fast to query by label — namespace, pod name, app — but slower for full-text search than something like Elasticsearch. The trade-off is intentional: label-scoped queries cover the vast majority of real operational use, and the storage cost is dramatically lower.

**Promtail** runs as a DaemonSet on every node, tails log files from `/var/log/pods/`, attaches Kubernetes labels, and ships to Loki. Grafana queries Loki directly.

## Deployment modes

**SingleBinary** — ingestion, querying, and management all run in a single instance. Simple to deploy, minimal operational overhead. A single point of failure: if it goes down, ingestion stops and logs are lost. The right starting point for most clusters.

**SimpleScalable** — responsibilities split into separate pods, each running a minimum of two instances for HA. Ingestion, querying, and the compactor can be scaled independently. Significantly more operational overhead, but fault-tolerant and tunable under load. The right move for production once you have volume and reliability requirements.

## Getting started

The fastest path to a working stack is deploying Loki alongside `kube-prometheus-stack`, which brings up Prometheus, Grafana, and Alertmanager together. See the [Prometheus](../prometheus/) note for the kube-prometheus-stack setup and the ArgoCD CRD workaround.

Loki and Promtail are installed as a separate ArgoCD Application, using multiple Helm sources with values pulled from the cluster config repo:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: log-ingestion
  namespace: argo-cd
spec:
  project: default
  sources:

    # Loki
    - repoURL: "https://grafana.github.io/helm-charts"
      chart: loki
      targetRevision: 6.55.0
      helm:
        releaseName: loki
        valueFiles:
          - $values/cluster/testing/overlay/monitoring/helm/loki-values.yaml

    # Promtail
    - repoURL: "https://grafana.github.io/helm-charts"
      chart: promtail
      targetRevision: 6.17.1
      helm:
        releaseName: promtail
        valueFiles:
          - $values/cluster/testing/overlay/monitoring/helm/promtail-values.yaml

    # Values source — cluster config repo
    - repoURL: 'git@github.com:example-org/cluster-config.git'
      targetRevision: HEAD
      ref: values

  destination:
    server: https://kubernetes.default.svc
    namespace: monitoring
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```

Note: `targetRevision: HEAD` is fine for testing environments. Pin to a tag for staging and production.

## Promtail deprecation

Promtail is deprecated as of February 2025 and in LTS — security fixes only, no new features. Expected EOL is end of 2026.

The Grafana-recommended replacement is **[Grafana Alloy](https://grafana.com/docs/alloy/latest/)**, a more capable collector that handles metrics, logs, and traces in a single agent. The migration path is not yet settled enough for a confident recommendation — worth waiting for clear community consensus before moving. Until then, Promtail continues to work and the LTS window gives time to plan.

## Grafana integration

Add Loki as a data source in Grafana and logs become queryable alongside metrics. A useful starting point is a simple app-oriented logs dashboard — filter by namespace and pod, tail in near-real-time, correlate timestamps with Prometheus spikes.

LogQL, Loki's query language, mirrors PromQL in style:

```logql
# All error logs from a namespace
{namespace="production"} |= "error"

# Parse and filter structured logs
{app="my-api"} | json | status >= 500

# Rate of error log lines over time
rate({namespace="production"} |= "error" [5m])
```

## Resources

- [Loki documentation](https://grafana.com/docs/loki/latest/)
- [Grafana Alloy documentation](https://grafana.com/docs/alloy/latest/) — future Promtail replacement
- [loki-stack Helm chart](https://github.com/grafana/helm-charts/tree/main/charts/loki-stack)
- [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
