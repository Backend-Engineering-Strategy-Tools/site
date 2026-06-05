---
title: "Istio"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["istio", "service-mesh", "kubernetes", "envoy", "mtls", "observability"]
---

Istio is a service mesh for Kubernetes. It injects a sidecar proxy (Envoy) into every pod, and all traffic between pods flows through these proxies rather than directly between containers. This gives the mesh control over traffic routing, security, and observability without any changes to application code.

## What it solves

In a large microservice deployment, every service needs to handle retries, timeouts, circuit breaking, mutual TLS, and metrics collection — or skip them and accept the risk. Without a mesh, each team implements this differently, or not at all. Istio moves these concerns out of the application and into the infrastructure layer, where they are configured once and applied uniformly.

## Traffic management

Istio's `VirtualService` and `DestinationRule` CRDs give fine-grained control over how traffic is routed:

```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
    - reviews
  http:
    - match:
        - headers:
            end-user:
              exact: test-user
      route:
        - destination:
            host: reviews
            subset: v2
    - route:
        - destination:
            host: reviews
            subset: v1
```

This routes a specific user to `v2` of a service while everyone else gets `v1` — canary testing without a load balancer rule or code change.

## mTLS

Istio issues and rotates certificates for every workload and enforces mutual TLS between services automatically. Services authenticate each other's identity, not just encrypt the connection. A `PeerAuthentication` policy can enforce strict mTLS across a namespace, ensuring no plaintext traffic is accepted.

## Observability

Because all traffic flows through Envoy sidecars, Istio generates L7 metrics (request rate, error rate, latency percentiles), distributed traces, and access logs for every service-to-service call — without instrumentation in the services themselves. This integrates with [Prometheus](/public-notes/observability/prometheus/), [Grafana](/public-notes/observability/grafana/), and [Jaeger](/public-notes/observability/jaeger/).

## Cost

Istio adds latency (two extra proxy hops per call) and resource overhead (a sidecar per pod). For clusters with tens of services, the operational benefit is clear. For small clusters or teams early in a microservices journey, the complexity may outweigh the gains.

## Resources

- [Istio documentation](https://istio.io/latest/docs/)
- [Istio concepts](https://istio.io/latest/docs/concepts/)
