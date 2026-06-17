---
title: "Gardener on Cleura"
date: 2026-06-16
draft: false
showReadingTime: false
layout: single
tags: ["gardener", "kubernetes", "cleura", "openstack", "networking", "tcp", "ingress"]
---

Getting hands-on with [Gardener](https://gardener.cloud/) on [Cleura](https://cleura.com/) — a European OpenStack cloud — ahead of using it professionally. The focus is on the networking and traffic ingress side: how does a Gardener shoot cluster on OpenStack expose services, what does the LoadBalancer path actually look like, and when does ingress apply versus when it does not.

The test application is a [Minecraft server with Velocity proxy](/projects/minecraft/) — useful precisely because it is raw TCP rather than HTTP, which forces the full LoadBalancer path rather than an ingress shortcut.

→ [Gardener on Cleura — technical notes](/public-notes/kubernetes/gardener/)

---

## Steps

### 1 — Shoot cluster

Provision a Gardener shoot cluster on Cleura. Cleura wraps Gardener behind their own REST API — `gardenctl` and the Gardener Terraform provider require the garden cluster kubeconfig, which Cleura does not expose. Cluster lifecycle goes through their REST API instead.

→ [Provisioning via Cleura REST API](/public-notes/kubernetes/gardener/#provisioning-a-shoot-cluster-on-cleura)  
→ [Cleura docs issue #533 — IaC and gardenctl access](https://github.com/cleura/docs/issues/533)

### 2 — Envoy Gateway

Deploy [Envoy Gateway](https://gateway.envoyproxy.io/) into the shoot cluster — the CNCF implementation of the [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/). The NGINX Ingress Controller is deprecated; Gateway API is the forward path with a standardised spec for both HTTP and TCP.

Envoy Gateway exposes a single `LoadBalancer` service via Octavia. Everything routes through it.

### 3 — HTTPRoute, certificates, and BlueMap

Deploy [BlueMap](https://bluemap.bluecolored.de/) — a Minecraft mod that renders the world as a live 3D web map served over HTTP. Route it through the Gateway with a `HTTPRoute` and wire [cert-manager](https://cert-manager.io/) to provision a Let's Encrypt certificate.

A real HTTP service with a real use, not a throwaway test page. Validates the full HTTP + TLS path before touching the game server.

### 4 — Minecraft via standard LoadBalancer

Deploy [`itzg/minecraft-server`](https://github.com/itzg/docker-minecraft-server) as a StatefulSet with a plain `LoadBalancer` service for TCP 25565 — the direct Octavia path, no Gateway involved. Gets the server running quickly and confirms TCP exposure works on Cleura independently.

```text
Internet
    |
TCP 25565
    |
Octavia LB (direct LoadBalancer service)
    |
Minecraft Pod (itzg/minecraft-server)
    |
PVC (Cinder)
```

### 5 — Migrate to TCPRoute

Migrate the TCP service to a `TCPRoute` through Envoy Gateway. `TCPRoute` is in the Gateway API experimental channel — this step validates that a single Gateway handles both HTTP and raw TCP.

```text
Internet
    |
Octavia LB (one Gateway LoadBalancer)
    |
Envoy Gateway
    |
+------------------------------+------------------------------+
|                                                             |
HTTPRoute → BlueMap                          TCPRoute → Minecraft
```

### 6 — Velocity (if needed)

Add [Velocity](https://papermc.io/software/velocity) as a TCP proxy in front of the Minecraft server if multi-server routing becomes relevant — lobby, modded, survival as separate backends. Skip if a single server is enough.

→ [Minecraft project](/projects/minecraft/)

### 7 — Plugin pipeline

A colleague is building a Minecraft plugin. The goal is a [Dagger](https://dagger.io/) pipeline with GitHub Actions — the same build running locally and in CI, covering the JVM toolchain and packaging steps.

### 8 — AI

Something with NPC behaviour, a bot, or plugin-side automation. Low priority, high fun.

---

## Status

| Step                                    | Status  |
|-----------------------------------------|---------|
| 1 — Shoot cluster on Cleura             | planned |
| 2 — Envoy Gateway                       | planned |
| 3 — HTTPRoute + cert-manager + BlueMap  | planned |
| 4 — Minecraft via LoadBalancer (itzg)   | planned |
| 5 — Migrate to TCPRoute                 | planned |
| 6 — Velocity                            | planned |
| 7 — Plugin pipeline (Dagger)            | planned |
| 8 — AI                                  | planned |

---

*Building this out — notes will expand as each step lands.*
