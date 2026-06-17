---
title: "Gardener on Cleura"
description: "Gardener shoot cluster reference — garden/seed/shoot model, networking on OpenStack, TCP and HTTP via Kubernetes Gateway API with Envoy Gateway."
date: 2026-06-16
draft: false
tags: ["gardener", "kubernetes", "cleura", "openstack", "networking", "gateway-api", "envoy", "tcp"]
showReadingTime: false
layout: single
---

[Gardener](https://gardener.cloud/) is a Kubernetes-as-a-Service framework that runs on Kubernetes and manages the lifecycle of other clusters declaratively. Rather than managing control planes by hand, Gardener treats clusters as a resource — defined, created, upgraded, and deleted via the Gardener API.

---

## Concepts

Gardener uses three layers:

| Layer          | What it is                                                   |
|----------------|--------------------------------------------------------------|
| Garden cluster | Runs Gardener itself — the management control plane          |
| Seed cluster   | Hosts the control planes of shoot clusters (as pods)         |
| Shoot cluster  | The cluster you actually use — nodes run on the target cloud |

The shoot cluster's API server does not run on the shoot nodes. It runs as a pod inside the seed cluster. From the outside it behaves like any other Kubernetes cluster; internally the control plane is isolated from the data plane.

Shoot clusters are defined as `Shoot` resources applied to the garden cluster:

```yaml
apiVersion: core.gardener.cloud/v1beta1
kind: Shoot
metadata:
  name: my-cluster
  namespace: garden-my-project
spec:
  cloudProfileName: openstack
  region: sto2
  provider:
    type: openstack
    workers:
      - name: worker-pool
        machine:
          type: l2.c2r4
        minimum: 1
        maximum: 3
  kubernetes:
    version: "1.30"
  networking:
    type: calico
    pods: 100.128.0.0/11
    nodes: 10.250.0.0/16
    services: 100.112.0.0/13
```

---

## Shoot cluster on Cleura

[Cleura](https://cleura.com/) is a European OpenStack provider. Gardener provisions shoot nodes as OpenStack VMs via the OpenStack machine controller.

Key integrations:

| Component         | Implementation                                |
|-------------------|-----------------------------------------------|
| Node provisioning | OpenStack VMs via Gardener machine controller |
| Load balancers    | Octavia via cloud-controller-manager          |
| Block storage     | Cinder via CSI driver                         |
| DNS               | Manual or external-dns                        |
| CNI               | Calico (default) or configurable              |

Gardener on Cleura does not provide an ingress controller or API gateway — these are brought in separately.

---

## Networking

Gardener manages the cluster network configuration as part of the shoot spec. Pod, node, and service CIDRs are defined at cluster creation and must not overlap with the OpenStack network.

On Cleura, nodes get OpenStack floating IPs for egress. Pod-to-pod traffic stays within the cluster overlay network (Calico by default). Traffic entering from outside the cluster goes through a `LoadBalancer` service — either directly for raw TCP, or via a gateway controller for HTTP.

---

## Ingress — classic vs Gateway API

The classic Kubernetes `Ingress` resource is HTTP-only, has no TCP support, and its feature set varies across implementations via non-standard annotations. The NGINX Ingress Controller — the most widely used implementation — is deprecated; NGINX now focuses on their [Gateway API implementation](https://github.com/nginxinc/nginx-gateway-fabric) instead.

The [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/) is the forward path — a set of CRDs (`Gateway`, `HTTPRoute`, `TCPRoute`, `TLSRoute`) with a standardized spec and first-class support for both HTTP and TCP.

| Resource    | Protocol        | API         | Status         |
|-------------|-----------------|-------------|----------------|
| `Ingress`   | HTTP only       | Kubernetes  | Stable, legacy |
| `HTTPRoute` | HTTP/HTTPS      | Gateway API | Stable         |
| `TCPRoute`  | Raw TCP         | Gateway API | Experimental   |
| `TLSRoute`  | TLS passthrough | Gateway API | Experimental   |

---

## Envoy Gateway

[Envoy Gateway](https://gateway.envoyproxy.io/) is the CNCF implementation of the Kubernetes Gateway API using [Envoy](https://www.envoyproxy.io/) as the data plane. It supports `HTTPRoute`, `TCPRoute`, and `TLSRoute` through a single `Gateway` resource — one entry point, both protocols.

```text
Octavia LB  ←  one LoadBalancer service per Gateway listener
    |
Envoy Gateway pod
    |
+------------------+------------------+
|                                     |
HTTPRoute → ClusterIP pods       TCPRoute → ClusterIP pods
```

Envoy Gateway is deployed into the shoot cluster and exposes a `LoadBalancer` service via Octavia, the same as any other service. The Gateway API resources then declare what routes through it.

---

## TCPRoute — declaring TCP services

`TCPRoute` attaches to a `Gateway` listener and routes raw TCP traffic to a backend service. This is how a non-HTTP workload (e.g. a game server, a database proxy, a custom protocol service) gets exposed through the Gateway API rather than a standalone `LoadBalancer` service.

```yaml
apiVersion: gateway.networking.k8s.io/v1alpha2
kind: TCPRoute
metadata:
  name: my-tcp-service
  namespace: my-app
spec:
  parentRefs:
    - name: my-gateway
      sectionName: tcp-listener
  rules:
    - backendRefs:
        - name: my-service
          port: 1234
```

The corresponding `Gateway` listener:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
  namespace: my-app
spec:
  gatewayClassName: envoy-gateway
  listeners:
    - name: tcp-listener
      protocol: TCP
      port: 1234
    - name: http-listener
      protocol: HTTP
      port: 80
```

One Gateway, both protocols declared explicitly. The `TCPRoute` API is in the experimental channel and requires opting in when installing Envoy Gateway.

---

## HTTPRoute — HTTP services

`HTTPRoute` handles HTTP and HTTPS traffic with routing by hostname, path, header, or method — without annotations.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: my-http-service
  namespace: my-app
spec:
  parentRefs:
    - name: my-gateway
      sectionName: http-listener
  hostnames:
    - my-app.example.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: my-service
          port: 8080
```

---

## LoadBalancer — direct TCP via Octavia

For cases where a `TCPRoute` is not appropriate (or the Gateway API experimental channel is not enabled), a `LoadBalancer` service provisions an Octavia LB directly:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-tcp-service
  namespace: my-app
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - port: 1234
      targetPort: 1234
      protocol: TCP
```

Annotations control Octavia behaviour — timeouts, health check parameters, internal vs external. These are provider-specific and not standardised across OpenStack deployments.

---

## Storage

Cinder block volumes are available via the CSI driver. A `PersistentVolumeClaim` provisions a Cinder volume automatically using the cluster's default storage class.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

Cinder volumes are `ReadWriteOnce` — they attach to a single node. For stateful workloads, use `StatefulSet` rather than `Deployment` to get stable volume binding across pod restarts.

---

## Provisioning a shoot cluster on Cleura

Cleura wraps Gardener behind their own REST API at `rest.cleura.cloud`. The garden cluster kubeconfig is not exposed — `gardenctl` does not work directly. Cluster lifecycle is managed through HTTP calls.

### Authentication

Every call requires a token obtained once per session:

```bash
curl -s -X POST https://rest.cleura.cloud/auth/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{"auth": {"login": "you@example.com", "password": "yourpass"}}' \
  | jq '{token: .token}'
```

Pass `X-AUTH-LOGIN` and `X-AUTH-TOKEN` headers on all subsequent calls.

### Bootstrap (once per project/region)

Before creating any clusters, the project must be bootstrapped — this wires up the OpenStack credentials that Gardener uses to provision nodes:

```bash
curl -X POST \
  https://rest.cleura.cloud/gardener/v1/public/secret/kna1/{projectId}/bootstrap \
  -H "X-AUTH-LOGIN: ..." -H "X-AUTH-TOKEN: ..."
```

Safe to call repeatedly; idempotent.

### Create a shoot cluster

```bash
curl -X POST \
  https://rest.cleura.cloud/gardener/v1/public/shoot/kna1/{projectId} \
  -H "X-AUTH-LOGIN: ..." -H "X-AUTH-TOKEN: ..." \
  -H "Content-Type: application/json" \
  -d '{
    "shoot": {
      "name": "my-cluster",
      "kubernetes": {"version": "1.31.0"},
      "provider": {
        "infrastructureConfig": {"floatingPoolName": "ext-net"},
        "workers": [{
          "name": "default",
          "machine": {
            "type": "4C-8GB-50GB",
            "image": {"name": "ubuntu", "version": "22.4.20230301"}
          },
          "minimum": 1,
          "maximum": 3,
          "volume": {"size": "50Gi"}
        }]
      }
    }
  }'
```

### Poll until ready

```bash
curl https://rest.cleura.cloud/gardener/v1/public/shoot/kna1/{projectId}/my-cluster \
  -H "X-AUTH-LOGIN: ..." -H "X-AUTH-TOKEN: ..." \
  | jq '.lastOperation | {state, description, progress}'
```

Poll until `lastOperation.state == "Succeeded"`. Takes roughly 10–15 minutes on first provision.

### Fetch kubeconfig

The Cleura docs reference two kubeconfig paths — `GET /kubeconfig` (lowercase) and `POST /Kubeconfig` (uppercase, different casing). Neither worked reliably in practice. The endpoint that actually returns a kubeconfig is:

```bash
curl -s -X POST \
  https://rest.cleura.cloud/gardener/v1/public/shoot/kna1/{projectId}/my-cluster/adminkubeconfig \
  -H "X-AUTH-LOGIN: ..." -H "X-AUTH-TOKEN: ..." \
  -H "Content-Type: application/json" \
  -d '{"config": {"expirationSeconds": 3600}}' \
  | jq -r > my-cluster-kubeconfig.yaml
```

The `expirationSeconds` field controls credential lifetime. A bug report has been filed with Cleura about the endpoint inconsistency — the `adminkubeconfig` path is not documented.

| Path               | Method | Documented | Works   |
|--------------------|--------|------------|---------|
| `/kubeconfig`      | GET    | yes        | unclear |
| `/Kubeconfig`      | POST   | yes        | unclear |
| `/adminkubeconfig` | POST   | no         | yes     |

### Script

A bash script wrapping the full workflow (list, create, wait, kubeconfig, delete) is available: [cleura-shoot.sh](/scripts/cleura-shoot.sh)

```bash
export CLEURA_LOGIN="you@example.com"
export CLEURA_PASSWORD="yourpass"

./cleura-shoot.sh list
./cleura-shoot.sh create my-cluster
./cleura-shoot.sh wait my-cluster
./cleura-shoot.sh kubeconfig my-cluster
./cleura-shoot.sh delete my-cluster
```

### IaC options

No native Terraform provider exists for Cleura's Gardener REST API. The Gardener Terraform provider (`registry.terraform.io/providers/gardener/gardener`) requires the garden cluster kubeconfig, which Cleura does not expose. Options:

| Approach                       | Notes                                                            |
|--------------------------------|------------------------------------------------------------------|
| Bash + curl                    | Minimal deps — just `curl` and `jq`                              |
| Crossplane `provider-http`     | Declarative, Kubernetes-native, reconciliation loop              |
| Custom Terraform provider      | Full `plan`/`apply` semantics — requires Go provider development |
| Pulumi custom dynamic provider | Python/TypeScript, similar effort to custom Terraform provider   |


