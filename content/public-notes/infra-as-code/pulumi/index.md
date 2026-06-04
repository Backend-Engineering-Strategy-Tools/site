---
title: "Pulumi"
date: 2026-06-03
draft: false
showReadingTime: false
layout: single
tags: ["pulumi", "iac", "typescript", "go", "multi-cloud"]
---

Pulumi takes the same approach as [AWS CDK](../cdk/) — use a real programming language to define infrastructure — but without the CloudFormation layer underneath. Pulumi talks directly to cloud APIs, maintains its own state, and supports multiple clouds from a single codebase.

Languages: TypeScript, Python, Go, Java, C#, and YAML. Same language across all supported clouds.

---

## How it works

Write infrastructure as code in your language of choice. Pulumi runs the program, builds a desired-state graph, diffs against current state, and makes the API calls to converge.

```typescript
import * as aws from "@pulumi/aws";

const bucket = new aws.s3.Bucket("assets", {
    versioning: { enabled: true },
    tags: { Environment: "prod" },
});

export const bucketName = bucket.bucket;
```

```bash
pulumi preview   # show planned changes
pulumi up        # apply
pulumi destroy   # tear down
```

---

## State

Pulumi manages state like Terraform — a backend stores what resources exist and their current configuration. Options:

- **Pulumi Cloud** — hosted, free tier available, adds secrets management and team features
- **S3 / GCS / Azure Blob** — self-managed, same pattern as Terraform's remote backend

---

## vs Terraform

The core tradeoff: Pulumi gives you a real programming language (real loops, real functions, real tests) at the cost of a smaller ecosystem and less community tooling than Terraform. HCL is a constraint but also a simplicity — Terraform configurations are declarative and readable without needing to understand the language runtime.

Pulumi is the better choice when infrastructure logic is genuinely complex enough to benefit from a real language. For straightforward cloud resources, Terraform's declarative HCL is often simpler to read and maintain.

---

## vs AWS CDK

Both use real languages. The difference: CDK generates CloudFormation and inherits all of CloudFormation's limitations (see the [CDK page](../cdk/)). Pulumi talks directly to cloud APIs, which means better drift visibility, faster deploys, and support outside AWS.

---

## Testing

Because infrastructure is code, it tests like code:

- Unit tests with Jest (TypeScript), pytest (Python), or Go test — test the resource graph without deploying
- Integration tests that deploy to an isolated stack and assert against live infrastructure

---

## OpenTofu / Terraform note

After HashiCorp changed Terraform's licence to BSL in 2023, the community forked it as [OpenTofu](https://opentofu.org/). If the licence change matters to your organisation, OpenTofu is a drop-in replacement. Pulumi was not affected.

Only explored in POC and lab contexts, not production. The honest take: Pulumi feels like the Gradle of IaC. The real-language argument is compelling in theory — proper loops, functions, tests, abstractions — but in practice it is easy to get wrong, and HCL's constraint is also its strength. A Terraform configuration is readable by anyone; a Pulumi TypeScript codebase requires understanding the language runtime and the person who wrote it.

The cases where Pulumi wins: complex infrastructure logic that genuinely benefits from a real language, or teams already deep in a single language who want infrastructure to live alongside application code. For standard cloud infrastructure, [Terraform](../terraform/) is the lower-friction choice.
