---
title: "Jaeger"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["jaeger", "tracing", "observability", "opentelemetry", "distributed-tracing"]
---

Metrics tell you something is wrong. Logs tell you what happened on one service. Distributed tracing tells you what happened across all the services involved in a single request — where the time went, which service called which, and where a failure or latency spike originated.

Jaeger is an open source distributed tracing system originally from Uber, now a CNCF graduated project. It collects trace data from instrumented services, stores it, and provides a UI for querying and visualising traces. A trace is a tree of spans — each span represents one operation (an HTTP request, a database query, a cache lookup), with start time, duration, and metadata. Jaeger assembles the spans from all services involved in a request into a single trace and lets you follow a request from the frontend through every microservice it touched.

## How it works

Services emit spans using the OpenTelemetry SDK (the modern standard) or the legacy Jaeger client libraries. Spans are sent to a Jaeger Collector, stored in a backend (Elasticsearch, Cassandra, or in-memory for development), and queried via the Jaeger UI or API.

The typical deployment in Kubernetes uses the Jaeger Operator:

```bash
kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/latest/download/jaeger-operator.yaml
```

A minimal all-in-one instance (suitable for development):

```yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger
spec:
  strategy: allInOne
```

For production, use the `production` strategy with a separate Collector, Query, and storage backend.

## OpenTelemetry

Jaeger is increasingly used as a backend rather than as the instrumentation library. OpenTelemetry (OTel) is the standard for instrumenting applications — language SDKs, auto-instrumentation agents, and a Collector that receives, processes, and exports telemetry. OTel exports traces to Jaeger (or Tempo, Zipkin, or any OTLP-compatible backend) via the OTLP protocol. The practical consequence: instrument once with OTel, route to whichever backend fits.

## In the observability stack

Jaeger covers the tracing pillar alongside [Prometheus](/public-notes/observability/prometheus/) (metrics) and [Loki](/public-notes/observability/loki/) (logs). [Grafana](/public-notes/observability/grafana/) can query Jaeger directly — a trace ID in a log line becomes a clickable link that opens the trace in Grafana's trace explorer, connecting all three pillars in a single investigation workflow. Grafana Tempo is an alternative tracing backend that integrates more tightly with the Grafana stack, but Jaeger remains the standalone tracing solution with the longest track record.

## Resources

- [Jaeger documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [Jaeger Operator](https://github.com/jaegertracing/jaeger-operator)
