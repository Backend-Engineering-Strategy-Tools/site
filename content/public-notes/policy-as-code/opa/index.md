---
title: "OPA & Rego"
draft: false
date: 2026-06-08
showReadingTime: false
layout: single
tags: ["opa", "rego", "policy-as-code", "cncf"]
---

OPA (Open Policy Agent) is a general-purpose policy engine. It takes structured input (JSON), evaluates it against a policy written in Rego, and returns a decision. It does not care what the input represents — Kubernetes resources, Terraform plans, HTTP requests, CI artifacts — anything you can express as JSON.

Rego is the query language OPA uses to express policy. It is declarative and logic-based (Datalog-inspired), which is a different mental model from imperative code. The learning curve is real but the payoff is policies that are testable, composable, and auditable.

## Install

```bash
brew install opa
```

Or download a binary from [github.com/open-policy-agent/opa/releases](https://github.com/open-policy-agent/opa/releases). No dependencies.

## Standalone eval

The fastest way to learn Rego is the REPL and the `eval` command — no Kubernetes, no Conftest, just OPA and a policy file.

```bash
# Interactive REPL
opa run

# Eval a query against a policy file and input
opa eval \
  --data policy.rego \
  --input input.json \
  "data.mypackage.allow"

# Run tests
opa test ./policies/

# Run tests with coverage
opa test --coverage ./policies/

# Check syntax without evaluating
opa check policy.rego
```

### REPL basics

```
> data                         # inspect all loaded data
> input                        # inspect current input
> x := {"a": 1}; x.a == 1    # inline assignment and check
> :help
```

## Rego basics

A policy file is a package with rules. Rules are boolean expressions — they are `true` when all conditions in the body hold.

```rego
package mypackage

# default value when no rule fires
default allow := false

# allow if both conditions hold
allow if {
    input.user == "admin"
    input.action == "read"
}
```

### Sets and comprehensions

```rego
package mypackage

# set of violations — empty set means compliant
violations contains msg if {
    input.containers[_].image == "latest"
    msg := "image tag must not be latest"
}

# all images
images := {img | img := input.containers[_].image}
```

### Iteration

Rego iterates implicitly. `input.containers[_]` means "for any element in containers". Use `[i]` if you need the index.

```rego
# any container missing a CPU limit is a violation
violations contains msg if {
    container := input.containers[_]
    not container.resources.limits.cpu
    msg := sprintf("container %v has no CPU limit", [container.name])
}
```

### Testing

OPA has a built-in test runner. Test files are Rego files with rules prefixed `test_`.

```rego
package mypackage_test

import data.mypackage

test_allow_admin if {
    mypackage.allow with input as {"user": "admin", "action": "read"}
}

test_deny_non_admin if {
    not mypackage.allow with input as {"user": "bob", "action": "read"}
}
```

```bash
opa test ./
# PASS: 2/2
```

## Input and data

OPA separates **input** (the thing being evaluated — changes per request) from **data** (context that does not change — lookup tables, allowlists, base policy).

```bash
# data is loaded with --data, can be JSON or Rego
opa eval --data policy.rego --data allowlist.json --input request.json "data.authz.allow"
```

## OPA as a server

OPA can run as a sidecar or standalone HTTP server. POST JSON to `/v1/data/<package>/<rule>` to get a decision.

```bash
opa run --server --addr :8181 policy.rego

curl -X POST http://localhost:8181/v1/data/mypackage/allow \
  -H "Content-Type: application/json" \
  -d '{"input": {"user": "admin", "action": "read"}}'
# {"result": true}
```

This is how Gatekeeper and Conftest use OPA under the hood.

## Rego playground

The [Rego Playground](https://play.openpolicyagent.org/) is the fastest way to experiment without installing anything. Paste a policy and input, evaluate, iterate.

## Resources

- [OPA documentation](https://www.openpolicyagent.org/docs/latest/)
- [Rego Playground](https://play.openpolicyagent.org/)
- [Rego cheat sheet](https://www.openpolicyagent.org/docs/latest/policy-cheatsheet/)
- [OPA GitHub](https://github.com/open-policy-agent/opa)
- [Styra Academy](https://academy.styra.com/) — free Rego courses (Styra built OPA)
