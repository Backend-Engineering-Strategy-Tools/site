---
title: "IaC Scanning"
draft: false
date: 2026-06-08
showReadingTime: false
layout: single
tags: ["checkov", "trivy", "tfsec", "policy-as-code", "security", "infra-as-code"]
---

Static analysis for infrastructure code. Scan Terraform, Helm, Kubernetes manifests, Dockerfiles, and CloudFormation before they are applied. The goal is catching misconfigurations — open security groups, missing encryption, public S3 buckets — in the same pipeline that runs your application tests.

These tools do not require running infrastructure. They read the source and flag violations against a built-in rule library, with optional custom rule support.

## Checkov

Checkov is a static analysis tool from Bridgecrew (now Prisma Cloud). Large built-in rule library for Terraform, Helm, Kubernetes, Dockerfiles, GitHub Actions, and more. Custom rules in Python or YAML.

```bash
pip install checkov
# or
brew install checkov
```

```bash
# Scan a Terraform directory
checkov -d ./infra/

# Scan a specific file
checkov -f main.tf

# Scan Kubernetes manifests
checkov -d ./k8s/ --framework kubernetes

# Scan a Helm chart
checkov -d ./charts/myapp/ --framework helm

# Output as JSON
checkov -d ./infra/ -o json

# Skip specific checks
checkov -d ./infra/ --skip-check CKV_AWS_20,CKV_AWS_57
```

Output shows passed/failed checks per resource with the check ID, description, and file:line reference.

### Custom policies (YAML)

```yaml
metadata:
  name: "Ensure S3 bucket has MFA delete enabled"
  id: "CKV2_AWS_CUSTOM_1"
  category: "ENCRYPTION"
scope:
  provider: terraform
definition:
  cond_type: attribute
  resource_types: ["aws_s3_bucket"]
  attribute: mfa_delete
  operator: equals
  value: "Enabled"
```

## Trivy (IaC mode)

Trivy is primarily a container image vulnerability scanner, but its `--scanners misconfig` mode covers IaC. One tool, multiple surfaces — useful when you are already using Trivy for image scanning and want consistent output.

```bash
brew install trivy
```

```bash
# Scan Terraform
trivy config ./infra/

# Scan Kubernetes manifests
trivy config ./k8s/

# Scan a Helm chart
trivy config ./charts/myapp/

# Include severity filter
trivy config --severity HIGH,CRITICAL ./infra/

# JSON output
trivy config -f json ./infra/
```

Trivy's IaC rules are sourced from [Trivy's built-in checks](https://github.com/aquasecurity/trivy-checks) — the same checks engine used by `tfsec` (Trivy absorbed `tfsec` in 2023).

## tfsec

`tfsec` was a standalone Terraform-focused scanner, now maintained as part of Trivy. The standalone CLI still works and is simpler if you only scan Terraform.

```bash
brew install tfsec

tfsec ./infra/
tfsec ./infra/ --severity HIGH
tfsec ./infra/ --format json
```

Most teams migrating from `tfsec` to Trivy get equivalent coverage with `trivy config`.

## Comparison

| | Checkov | Trivy config |
|---|---|---|
| Terraform | Yes | Yes |
| Kubernetes | Yes | Yes |
| Helm | Yes | Yes |
| Dockerfile | Yes | Yes |
| GitHub Actions | Yes | No |
| Custom rules | Python / YAML | Rego |
| Also scans | — | Container images, Git secrets, SBOMs |
| Maintained by | Prisma Cloud | Aqua Security |

For a team already using Trivy for image scanning, extending to IaC with `trivy config` keeps the toolchain simple. Checkov's advantage is the broader coverage (GitHub Actions, Bitbucket Pipelines) and more mature custom rule support.

## In CI

```yaml
# GitHub Actions — Trivy IaC scan
- name: Trivy IaC scan
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: config
    scan-ref: ./infra/
    severity: HIGH,CRITICAL
    exit-code: 1
```

```yaml
# GitHub Actions — Checkov
- name: Checkov scan
  uses: bridgecrewio/checkov-action@master
  with:
    directory: infra/
    framework: terraform
```

## Resources

- [Checkov documentation](https://www.checkov.io/1.Welcome/What%20is%20Checkov.html)
- [Trivy misconfig scanning](https://aquasecurity.github.io/trivy/latest/docs/scanner/misconfiguration/)
- [Trivy-checks (rule library)](https://github.com/aquasecurity/trivy-checks)
- [Checkov GitHub](https://github.com/bridgecrewio/checkov)
