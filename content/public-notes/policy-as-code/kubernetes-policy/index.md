---
title: "Kubernetes Policy"
draft: false
date: 2026-06-08
showReadingTime: false
layout: single
tags: ["kubernetes", "policy-as-code", "kyverno", "gatekeeper", "opa", "cel", "admission-control"]
---

Kubernetes has three distinct policy enforcement mechanisms. They sit at the same point in the request lifecycle — the admission controller — but differ in language, capability, and operational complexity.

| | Kyverno | Gatekeeper (OPA) | ValidatingAdmissionPolicy |
|---|---|---|---|
| Language | YAML/JMESPath | Rego | CEL |
| Native to K8s | No (CRD) | No (CRD) | Yes (built-in) |
| Validate | Yes | Yes | Yes |
| Mutate | Yes | Limited | Yes (1.32+) |
| Generate | Yes | No | No |
| Image verify | Yes | No | No |
| GA since | — | — | K8s 1.30 |
| Good for | Full-featured, K8s-native feel | Rego-first teams, policy-as-data | Simple rules, no extra install |

## ValidatingAdmissionPolicy (VAP)

Added in Kubernetes 1.26, **GA in 1.30**. Policies are built into the API server — no admission controller to deploy or maintain. Policy is written in **CEL** (Common Expression Language), a simple expression language also used in Kubernetes' `x-kubernetes-validations` CRD validation.

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: "require-run-as-non-root"
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
      - apiGroups: ["apps"]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["deployments"]
  validations:
    - expression: >
        object.spec.template.spec.securityContext.runAsNonRoot == true
      message: "Pods must run as non-root"
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: "require-run-as-non-root-binding"
spec:
  policyName: "require-run-as-non-root"
  validationActions: [Deny]
  matchResources:
    namespaceSelector:
      matchLabels:
        enforce-policy: "true"
```

The `ValidatingAdmissionPolicyBinding` scopes where a policy applies — cluster-wide, specific namespaces, or by label selector.

### CEL basics

CEL expressions have access to `object` (the incoming resource), `oldObject` (for updates), `request` (metadata, user, etc.), and `params` (a referenced ConfigMap or CRD for parameterisation).

```
# Simple field check
object.spec.replicas <= 10

# Nested optional field (use ?. for optional traversal)
object.spec.template.spec.?securityContext.?runAsNonRoot == optional.of(true)

# List comprehension — all containers must have limits
object.spec.template.spec.containers.all(c,
  has(c.resources) && has(c.resources.limits)
)

# String operations
object.metadata.name.startsWith("prod-")
```

### MutatingAdmissionPolicy

Added in Kubernetes 1.32 (alpha). Brings CEL-based mutation — set defaults, inject labels, patch fields — without Kyverno or a webhook. Still early; not production-ready yet.

## Gatekeeper

OPA running as a Kubernetes admission controller. Policies are written in Rego and stored as `ConstraintTemplate` CRDs. The separation between template (the Rego logic) and constraint (the enforcement configuration + parameters) is the key design pattern.

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items: {type: string}
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels

        violation[{"msg": msg}] {
            provided := {label | input.review.object.metadata.labels[label]}
            required := {label | label := input.parameters.labels[_]}
            missing := required - provided
            count(missing) > 0
            msg := sprintf("missing required labels: %v", [missing])
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-team-label
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Namespace"]
  parameters:
    labels: ["team", "environment"]
```

Gatekeeper also supports **audit mode** — it continuously evaluates existing resources against policies and surfaces violations without blocking. Useful for measuring compliance against policies you're not yet ready to enforce.

### Gatekeeper vs Kyverno

Kyverno is better if your team does not know Rego and wants policies that look like Kubernetes manifests. Gatekeeper is better if you are already invested in OPA/Rego and want a single policy language across K8s and non-K8s surfaces (via Conftest).

The K8s-native VAP is the right default for simple validation rules on new clusters — no extra install, but it does not cover mutation (until 1.32+), generation, or image verification.

## Resources

- [Gatekeeper documentation](https://open-policy-agent.github.io/gatekeeper/)
- [Gatekeeper library](https://github.com/open-policy-agent/gatekeeper-library) — ready-made ConstraintTemplates
- [ValidatingAdmissionPolicy docs](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)
- [CEL in Kubernetes](https://kubernetes.io/docs/reference/using-api/cel/)
- [Kyverno](/public-notes/kubernetes/kyverno/) — separate note
