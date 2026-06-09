---
title: "Conftest"
draft: false
date: 2026-06-08
showReadingTime: false
layout: single
tags: ["conftest", "opa", "rego", "policy-as-code", "cicd"]
---

Conftest is a CLI tool that runs OPA policies against structured config files — Kubernetes manifests, Terraform plans, Helm output, Dockerfiles, GitHub Actions workflows, anything that can be parsed. It is the CI/CD enforcement layer on top of Rego.

Write a policy once in Rego, run `conftest test` in your pipeline, fail the build if violations are found.

## Install

```bash
brew install conftest
```

## Basic usage

```bash
# Test a Kubernetes manifest
conftest test deployment.yaml

# Test all YAML in a directory
conftest test k8s/

# Test a Terraform plan (JSON output)
terraform show -json tfplan > tfplan.json
conftest test tfplan.json --parser json

# Test Helm-rendered output
helm template my-app ./chart | conftest test -
```

By default Conftest looks for policies in `./policy/`. Change with `--policy`.

## Policy structure

Policies are Rego files in the `policy/` directory. Conftest checks for `deny`, `warn`, and `violation` rules.

```rego
# policy/k8s.rego
package main

# deny blocks the pipeline
deny contains msg if {
    input.kind == "Deployment"
    not input.spec.template.spec.securityContext.runAsNonRoot
    msg := sprintf("Deployment %v must set runAsNonRoot", [input.metadata.name])
}

# warn prints a warning but does not fail
warn contains msg if {
    input.kind == "Deployment"
    not input.metadata.labels["app.kubernetes.io/version"]
    msg := sprintf("Deployment %v is missing version label", [input.metadata.name])
}
```

```
$ conftest test deployment.yaml
FAIL - deployment.yaml - main - Deployment nginx must set runAsNonRoot
WARN - deployment.yaml - main - Deployment nginx is missing version label

2 tests, 0 passed, 1 warning, 1 failure
```

## Namespaces

Use `--namespace` to scope which Rego package Conftest evaluates. Useful when you have per-resource-type policies in separate packages.

```bash
conftest test deployment.yaml --namespace kubernetes.deployments
```

## Multiple parsers

Conftest supports many input formats. Common ones:

| Flag | Parses |
|---|---|
| `--parser yaml` | YAML (default for `.yaml`/`.yml`) |
| `--parser json` | JSON, Terraform plan |
| `--parser hcl2` | Terraform HCL |
| `--parser dockerfile` | Dockerfiles |
| `--parser toml` | TOML |

## Sharing policies

Policies can be distributed as OCI artifacts and pulled with `conftest pull`.

```bash
conftest pull ghcr.io/myorg/policies:latest
conftest test deployment.yaml
```

The [Conftest policy hub](https://www.conftest.dev/sharing/) documents the format. Useful for sharing a common policy library across repos without copy-pasting Rego.

## In CI

```yaml
# GitHub Actions example
- name: Policy check
  run: |
    conftest test k8s/ --policy policy/
```

Exits non-zero on `deny` violations. `warn` violations print but do not fail the build — useful for phased enforcement (warn first, deny later).

## Resources

- [Conftest documentation](https://www.conftest.dev/)
- [Conftest GitHub](https://github.com/open-policy-agent/conftest)
- [Example policies](https://github.com/open-policy-agent/conftest/tree/master/examples)
