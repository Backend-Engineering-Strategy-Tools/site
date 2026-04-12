---
title: "Prometheus"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

Something is wrong. Pods are restarting, latency is climbing, and a request that usually takes 50ms is now taking 2 seconds. You know something happened — users are complaining — but you have no numbers, no history, and no way to know when it started or which service caused it.

The instinct is to grep the logs. And with one service on one server, that works. But once you have 20 services running across 40 pods, grepping logs to understand system behaviour does not scale. You are looking at individual events trying to infer aggregate trends — the wrong tool for the question. Logs tell you what happened in one place at one moment. Metrics tell you how the system is behaving across all of it, over time.

So you use Prometheus. It scrapes metrics from every pod, node, and cluster component on a regular interval and stores them as time series. Now you have the spike, the exact minute it started, and a number attached to every symptom.

## How it works

Prometheus is pull-based: it reaches out to your services and scrapes a `/metrics` endpoint on a schedule. Services expose metrics in a simple text format; Prometheus stores them and makes them queryable.

```
# EXPOSE from your app
http://my-service:8080/metrics

# Prometheus scrapes this every 15s and stores:
http_requests_total{method="POST", status="500"} 42
http_request_duration_seconds{quantile="0.99"} 1.847
```

Most infrastructure components (Kubernetes itself, NGINX, Postgres, Redis, JVM) either expose Prometheus metrics natively or have an exporter that does it for them.

## In Kubernetes — kube-prometheus-stack

Running Prometheus in Kubernetes manually is fiddly. The fastest path to a working Prometheus + Grafana + Alertmanager stack is the `kube-prometheus-stack` Helm chart — it installs the Prometheus Operator, Grafana, Alertmanager, node exporters, and a set of default dashboards and alert rules in one go. Add [Loki](../loki/) on top for logs.

### CRD workaround

`kube-prometheus-stack` ships with a large set of CRDs. When managed through ArgoCD, applying CRDs and the chart in the same sync can cause ordering failures. The standard workaround is `skipCrds: true` in the ArgoCD Application, with CRDs applied via a separate kustomize source in the same Application:

```yaml
- repoURL: "oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack"
  chart: kube-prometheus-stack
  targetRevision: 82.14.1
  helm:
    releaseName: kube-prometheus-stack
    valueFiles:
      - $values/cluster/development/overlay/monitoring/helm/kube-prometheus-stack.yaml
    skipCrds: true
```

This keeps the CRDs in Git and lets ArgoCD manage them, while avoiding the race condition on first install.

### ServiceMonitor

The **Prometheus Operator** (installed by the stack) manages scrape config via CRDs. The key one is `ServiceMonitor` — it tells Prometheus which services to scrape without editing Prometheus config directly:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: metrics
      interval: 30s
```

Deploy this alongside your app and Prometheus picks it up automatically.

## PromQL

Prometheus Query Language lets you slice and aggregate metrics. A few patterns worth knowing:

```promql
# Request rate over last 5 minutes
rate(http_requests_total[5m])

# 99th percentile latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Error ratio
rate(http_requests_total{status=~"5.."}[5m])
  /
rate(http_requests_total[5m])

# Memory usage per pod
container_memory_working_set_bytes{namespace="production"}
```

## Alerting

Prometheus evaluates alert rules continuously and fires them to Alertmanager, which handles routing, grouping, and silencing:

```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Error rate above 5% for {{ $labels.service }}"
```

`for: 5m` means the condition must hold for 5 minutes before firing — avoids noisy alerts on brief spikes.

## Metrics Server

Metrics Server is a separate, lightweight component that provides the real-time resource metrics (`kubectl top pods`, `kubectl top nodes`) that HPA uses to make scaling decisions. It is not Prometheus — it does not store history and is not queryable. It exists purely to feed the Kubernetes control plane.

Install via ArgoCD:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: metrics-server
  namespace: argo-cd
spec:
  project: default
  sources:
    - repoURL: "https://kubernetes-sigs.github.io/metrics-server"
      chart: metrics-server
      targetRevision: 3.13.0
      helm:
        releaseName: metrics-server
  destination:
    server: https://kubernetes.default.svc
    namespace: kube-system
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
    syncOptions:
      - CreateNamespace=true
```

Install this early — HPA does nothing without it, and `kubectl top` is the first thing you reach for when something looks wrong.

## What Prometheus is not

Prometheus stores metrics — numbers over time. It does not store logs (see [Loki](../loki/)) and it does not trace individual requests across services (see [Jaeger](../jaeger/)). Metrics tell you *that* something is wrong and *when* it started. The other two tell you *what* happened and *where*.

## Resources

- [Prometheus documentation](https://prometheus.io/docs/)
- [kube-prometheus-stack Helm chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
- [PromQL cheat sheet](https://promlabs.com/promql-cheat-sheet/)
