---
title: "Policy as Code — Overview"
draft: false
date: 2026-06-09
showReadingTime: false
layout: single
tags: ["policy-as-code", "opa", "rego", "kyverno", "conftest", "platform-engineering"]
---

Encoding compliance, security, and operational rules as version-controlled, testable code — evaluated at the point where things are created or changed rather than audited after the fact.

The alternative is manual review and reactive alerts. Policy as code shifts that left: rules are explicit, reviewable, and enforced automatically.

## Enforcement points

The same policy intent can be applied at three different points in the lifecycle:

**CI/CD gate** — evaluate before anything reaches the cluster. Fail the pipeline on violations. Tools: Conftest, Checkov, Trivy IaC. Lowest blast radius, fastest feedback loop.

**Cluster admission** — intercept every `kubectl apply` at the API server. No non-compliant resource can be created or updated. Tools: Kyverno, Gatekeeper (OPA), K8s-native ValidatingAdmissionPolicy.

**Runtime / drift detection** — continuously evaluate live state against policy and surface violations. Catches things that predate the policy, or that arrived outside normal pipelines. Tools: OPA, AWS Config, Kyverno audit mode.

Most teams layer these: CI catches the obvious mistakes early and cheap, admission control enforces hard requirements at the cluster boundary, audit mode gives visibility into what is already out of compliance.

## How the tools relate

OPA is the common engine underneath Gatekeeper and Conftest. Rego is its policy language — learn it once and it applies across both. Kyverno is a separate engine that replaces Rego with Kubernetes-native YAML; lower barrier to entry, but the policy language does not transfer outside K8s. The K8s-native ValidatingAdmissionPolicy uses CEL, a simpler expression language built into the API server — no extra install, but limited to validation and basic mutation.

```
Policy intent
    ├── CI/CD gate       → Conftest (Rego) / Checkov / Trivy IaC
    ├── K8s admission    → Kyverno (YAML) / Gatekeeper (Rego) / VAP (CEL)
    └── Runtime          → OPA server / Kyverno audit / AWS Config
```

## To explore

- **Rego standalone** — eval policies against arbitrary JSON input using `opa eval` and the REPL, without Kubernetes. Good way to learn the language in isolation before wiring it into a pipeline or cluster. See the [OPA & Rego](/public-notes/policy-as-code/opa/) note.
