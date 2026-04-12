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

## In Kubernetes — the Prometheus Operator

Running Prometheus in Kubernetes manually is fiddly. The **Prometheus Operator** (part of the `kube-prometheus-stack` Helm chart) manages it via CRDs. The key one is `ServiceMonitor` — it tells Prometheus which services to scrape without editing Prometheus config directly:

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

## What Prometheus is not

Prometheus stores metrics — numbers over time. It does not store logs (see [Loki](../loki/)) and it does not trace individual requests across services (see [Jaeger](../jaeger/)). Metrics tell you *that* something is wrong and *when* it started. The other two tell you *what* happened and *where*.

## Resources

- [Prometheus documentation](https://prometheus.io/docs/)
- [kube-prometheus-stack Helm chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
- [PromQL cheat sheet](https://promlabs.com/promql-cheat-sheet/)
