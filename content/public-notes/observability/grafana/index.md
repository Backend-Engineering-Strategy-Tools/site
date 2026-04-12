---
title: "Grafana"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

Prometheus shows you the spike. It tells you memory climbed at 14:32, error rate crossed 5% at 14:35, and latency hit 2 seconds at 14:37. But raw PromQL results are numbers in a table. You cannot see the shape of an incident in a table. You cannot hand a table to a product manager and explain what happened.

So you use Grafana. It connects to Prometheus (and Loki, and a dozen other data sources) and turns those numbers into dashboards. You see the spike, the timeline, the correlation between services — all on one screen.

## Data sources

Grafana is a visualisation layer, not a storage layer. It queries data sources and renders the results. In a Kubernetes observability stack, the typical setup:

| Data source | What it provides |
|---|---|
| Prometheus | Metrics — CPU, memory, request rates, error rates, latency |
| Loki | Logs — searchable, filterable, correlated with metrics by time |
| Jaeger / Tempo | Traces — individual request journeys across services |

Adding a data source is a few fields in the UI or a ConfigMap if you manage Grafana as code.

## Dashboards

A dashboard is a collection of panels. Each panel runs a query against a data source and renders the result as a graph, gauge, stat, table, or heatmap.

The fastest way to get useful dashboards is [grafana.com/grafana/dashboards](https://grafana.com/grafana/dashboards/) — a library of community dashboards for almost every common component. Import by ID:

- **1860** — Node Exporter Full (host metrics: CPU, memory, disk, network)
- **6417** — Kubernetes cluster overview
- **7362** — MySQL overview
- **9628** — Postgres overview

Import these on day one and you have coverage before writing a single PromQL query.

## Variables

Dashboard variables make panels reusable across namespaces, clusters, or services. A variable populated from a Prometheus label query:

```
label_values(kube_pod_info{namespace=~".+"}, namespace)
```

Now every panel can use `$namespace` in its query, and a dropdown at the top of the dashboard filters the whole view.

## Alerting

Grafana has its own alert engine that evaluates queries on a schedule and routes alerts through contact points (Slack, PagerDuty, email). For Kubernetes setups already using Alertmanager, it is usually cleaner to define alert rules in Prometheus and use Grafana purely for visualisation — one place for alert rules, not two.

## Managing Grafana as code

Dashboards built in the UI are fragile — they live in a database and disappear if you rebuild the stack. Two better approaches:

**Grafana provisioning** — mount dashboard JSON files via ConfigMap. Grafana loads them on startup and they survive restarts.

**Grafonnet / Jsonnet** — generate dashboard JSON programmatically. Verbose but version-controllable and reviewable in pull requests.

## The observability trio

Grafana is the front end for the full observability stack:

- **Prometheus** — something is wrong, here are the numbers
- **Loki** — here are the log lines from that time window
- **Jaeger** — here is the exact request that failed and where it slowed down

Each answers a different question. Grafana is where you look at all three in one place.

## Resources

- [Grafana documentation](https://grafana.com/docs/grafana/latest/)
- [Grafana dashboard library](https://grafana.com/grafana/dashboards/)
- [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) — installs Prometheus + Grafana together
