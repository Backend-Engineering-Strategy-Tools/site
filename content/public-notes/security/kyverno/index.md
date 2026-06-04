---
title: "Kyverno"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["kyverno", "kubernetes", "policy", "security", "admission-control"]
---

Kyverno is a policy engine for Kubernetes. It runs as an admission controller and intercepts every resource creation or update, applying rules that validate, mutate, or generate resources. Policies are written as Kubernetes CRDs in YAML — no Rego, no separate language to learn. If you can write a Kubernetes manifest, you can write a Kyverno policy.

## Three rule types

**Validate** — reject resources that don't meet requirements:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  rules:
    - name: check-team-label
      match:
        any:
          - resources:
              kinds: [Deployment]
      validate:
        message: "Deployments must have a 'team' label."
        pattern:
          metadata:
            labels:
              team: "?*"
```

**Mutate** — automatically add or modify fields on admission:

```yaml
- name: add-default-resources
  match:
    any:
      - resources:
          kinds: [Pod]
  mutate:
    patchStrategicMerge:
      spec:
        containers:
          - (name): "*"
            resources:
              requests:
                +(memory): "64Mi"
                +(cpu): "250m"
```

**Generate** — create related resources automatically. A common use: generate a `NetworkPolicy` every time a new namespace is created.

## Enforcement vs audit

Policies run in `enforce` mode (block non-compliant resources) or `audit` mode (allow but report violations). Audit mode is the right starting point — understand your existing state before enforcing.

## Common policies

The [Kyverno policy library](https://kyverno.io/policies/) has ready-made policies for common requirements: disallow privileged containers, require image tags to not be `latest`, enforce resource limits, restrict hostPath mounts. Most teams start from the library and customise.

## Resources

- [Kyverno documentation](https://kyverno.io/docs/)
- [Kyverno policy library](https://kyverno.io/policies/)
