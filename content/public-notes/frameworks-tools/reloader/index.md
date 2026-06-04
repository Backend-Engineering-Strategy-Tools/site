---
title: "Reloader"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["reloader", "kubernetes", "configmap", "secrets", "stakater"]
---

Reloader is a Kubernetes controller from Stakater that watches ConfigMaps and Secrets and automatically triggers rolling restarts of Deployments, StatefulSets, and DaemonSets when the watched resources change. Kubernetes does not do this natively — updating a ConfigMap does not restart pods that consume it, so configuration changes don't take effect until the next deploy.

## Usage

Annotate a Deployment to watch a specific ConfigMap or Secret:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  annotations:
    reloader.stakater.com/auto: "true"          # watch all referenced ConfigMaps/Secrets
    # OR be specific:
    configmap.reloader.stakater.com/reload: "my-config"
    secret.reloader.stakater.com/reload: "my-secret"
```

When the ConfigMap or Secret changes, Reloader detects it and triggers a rolling restart by updating a pod template annotation. The deployment rolls out new pods that pick up the updated configuration.

## Installation

```bash
helm repo add stakater https://stakater.github.io/stakater-charts
helm install reloader stakater/reloader -n reloader --create-namespace
```

## Why not use a hash annotation manually

The common alternative is to inject a hash of the ConfigMap into the pod template annotations via Helm or Kustomize — when the hash changes, Kubernetes rolls the deployment. This works but requires build-time tooling. Reloader handles it at runtime without any changes to the deployment pipeline.

## Resources

- [Reloader GitHub](https://github.com/stakater/Reloader)
- [Stakater charts](https://github.com/stakater/stakater-charts)
