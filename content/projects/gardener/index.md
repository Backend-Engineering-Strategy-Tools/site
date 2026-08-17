---
title: "Gardener on Cleura"
date: 2026-06-16
draft: false
showReadingTime: false
layout: single
tags: ["gardener", "kubernetes", "cleura", "openstack", "networking", "tcp", "ingress", "dns", "externaldns", "designate"]
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

### 2 — Minecraft via standard LoadBalancer

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

Manifests: [stateful_set.yaml](/scripts/mc/stateful_set.yaml) · [service.yaml](/scripts/mc/service.yaml)

Apply directly from this repo:

```bash
kubectl apply -k "https://github.com/Backend-Engineering-Strategy-Tools/site//static/scripts/mc?ref=main"
```

Check the rollout and grab the external IP:

```bash
kubectl get all -l app=mc-example

kubectl get svc mc-example \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}:{.spec.ports[0].port}'
```

### 2.5 — Migrate to Helm chart

Swap the raw manifests for the [`itzg/minecraft-server-charts`](https://github.com/itzg/minecraft-server-charts) Helm chart — actively maintained, covers server type, persistence, RCON, backups, and extra ports (BlueMap, Dynmap). The raw YAML stays useful as a reference for the underlying shape.

Manifests: [values.yaml](/scripts/mc-helm/values.yaml)

```bash
helm repo add minecraft-server-charts https://itzg.github.io/minecraft-server-charts/
helm upgrade --install mc minecraft-server-charts/minecraft \
  -f https://backend-engineering-strategy-tools.github.io/site/scripts/mc-helm/values.yaml
```

Check the rollout and grab the external IP:

```bash
kubectl get all -l app.kubernetes.io/instance=mc
```

```bash
kubectl get svc mc-example -o jsonpath='{.status.loadBalancer.ingress[0].ip}:{.spec.ports[0].port}'
```

### 2.6 — Second instance: Bedrock play via Geyser/Floodgate

A second, independent Helm release — `TYPE=PAPER` instead of vanilla, so it can carry [Geyser](https://geysermc.org/) (protocol translation) and [Floodgate](https://github.com/GeyserMC/Floodgate) (lets Xbox-Live-authenticated Bedrock accounts join without a Java account) as plugins. Runs alongside the vanilla instance from step 2, not in place of it — separate release name, separate PVC, own Octavia LoadBalancer for the extra Bedrock UDP port (19132) plus the usual Java TCP port (25565).

Manifests: [values-bedrock.yaml](/scripts/mc-helm/values-bedrock.yaml)

```bash
helm upgrade --install mc-bedrock minecraft-server-charts/minecraft \
  -f https://backend-engineering-strategy-tools.github.io/site/scripts/mc-helm/values-bedrock.yaml
```

```bash
kubectl get svc -l app.kubernetes.io/instance=mc-bedrock \
  -o jsonpath='{range .items[*]}{.metadata.name}{" -> "}{.status.loadBalancer.ingress[0].ip}{"\n"}{end}'
```

### 3 — Envoy Gateway

Deploy [Envoy Gateway](https://gateway.envoyproxy.io/) into the shoot cluster — the CNCF implementation of the [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/). The NGINX Ingress Controller is deprecated; Gateway API is the forward path with a standardised spec for both HTTP and TCP.

Envoy Gateway exposes a single `LoadBalancer` service via Octavia. Everything routes through it.

### 3.5 — ExternalDNS + Designate

Once the Gateway has a LoadBalancer IP from Octavia, it needs a DNS name. [ExternalDNS](https://kubernetes-sigs.github.io/external-dns/) watches `Service` and `Gateway` resources and writes DNS records automatically — no manual record management as IPs change.

On OpenStack/Cleura, the DNS service is [Designate](https://docs.openstack.org/designate/) — the OpenStack equivalent of Route 53. ExternalDNS has a Designate provider. The setup mirrors the Route 53 pattern: a hosted zone in Designate, ExternalDNS with credentials to write records, and annotation-driven control over which services get DNS entries.

→ [DNS & DNSSEC reference](/public-notes/networking/dns-dnssec/) — Route 53 and DNS fundamentals; same concepts apply to Designate  
→ [mjli.org — DNS & DNSSEC Lab](/projects/mjli-org/) — working through the DNS/ExternalDNS groundwork on AWS

### 4 — HTTPRoute, certificates, and BlueMap

Deploy [BlueMap](https://bluemap.bluecolored.de/) — a Minecraft mod that renders the world as a live 3D web map served over HTTP. Route it through the Gateway with a `HTTPRoute` and wire [cert-manager](https://cert-manager.io/) to provision a Let's Encrypt certificate.

A real HTTP service with a real use, not a throwaway test page. Validates the full HTTP + TLS path before touching the game server.

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

## IaC gap

Cleura does not expose the garden cluster kubeconfig. That one limitation closes off the entire Gardener tooling ecosystem: `gardenctl` requires it, the [Gardener Terraform provider](https://registry.terraform.io/providers/gardener/gardener) requires it, and any Crossplane provider built on the Gardener API would require it too. There is no HCL path here.

What remains is Cleura's own REST API — which is fine for interactive use but falls short the moment you want to drive cluster lifecycle from a pipeline. A bash script wrapping `curl` and `jq` works, and that is what [cleura-shoot.sh](/scripts/cleura-shoot.sh) does, but it is a workaround rather than a solution. No state, no plan, no diff — just imperative API calls.

Options if this needs to graduate beyond a script:

- **Crossplane `provider-http`** — can wrap the REST API declaratively, but has no native polling or deletion hooks, so the reconciliation story is awkward
- **Custom Terraform provider** — full `plan`/`apply` semantics, but requires writing a Go provider from scratch
- **Pulumi dynamic provider** — similar effort, Python or TypeScript

A feature request for gardenctl access or a native IaC provider has been filed with Cleura (→ [cleura/docs#533](https://github.com/cleura/docs/issues/533)). Until something changes there, the bash script is as good as it gets.

---

## Status

| Step                                    | Status  |
|-----------------------------------------|---------|
| 1 — Shoot cluster on Cleura             | done    |
| 2 — Minecraft via LoadBalancer (itzg)   | done    |
| 2.5 — Migrate to Helm chart             | planned |
| 2.6 — Second instance (Geyser/Floodgate)| done    |
| 3 — Envoy Gateway                       | planned |
| 3.5 — ExternalDNS + Designate           | planned |
| 4 — HTTPRoute + cert-manager + BlueMap  | planned |
| 5 — Migrate to TCPRoute                 | planned |
| 6 — Velocity                            | planned |
| 7 — Plugin pipeline (Dagger)            | planned |
| 8 — AI                                  | planned |

---

*Building this out — notes will expand as each step lands.*
