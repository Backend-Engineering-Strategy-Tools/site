---
title: "AWS CDK"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

AWS CDK (Cloud Development Kit) lets you define infrastructure using real programming languages — Java, TypeScript, Python — rather than a DSL. You write code, CDK synthesizes it into a CloudFormation template, and CloudFormation deploys it to AWS.

The appeal is obvious if your team lives in Java: familiar language, familiar tooling, loops and abstractions, unit tests with JUnit. No HCL to learn.

In practice it is slower and more cumbersome than it looks, and the CloudFormation layer underneath causes real problems.

## How it works

1. Write Java (imperative)
2. `mvn package` — compile and run unit tests
3. `cdk synth` — generate the CloudFormation template
4. `cdk diff` — compare deployed stack with current state (optional)
5. `cdk deploy` — deploy stack to AWS via CloudFormation
6. CloudFormation makes the API calls to AWS

The key thing to understand: CDK does not talk to AWS directly. It generates CloudFormation, and CloudFormation does the work. Everything downstream of `cdk synth` is CloudFormation behaviour, not CDK behaviour.

## The CloudFormation problem

CloudFormation does not track changes made outside of stacks. Someone logs into the console and modifies a security group — CloudFormation does not know, your CDK code does not know, and `cdk diff` will not show it. That is drift, and it accumulates silently until a deployment overrides something that was manually changed in production, or a `cdk destroy` removes something that was depended on.

CloudFormation does have a drift detection feature, but it is not part of the normal workflow — you trigger it manually from the console, it shows you the diff, and then expects you to go fix it yourself.

Compared to [Terraform](../terraform/), which maintains its own state file and surfaces drift explicitly in `terraform plan`, this is a meaningful operational weakness.

## Cross-stack dependencies

Splitting infrastructure into smaller stacks is the right instinct — smaller blast radius, faster deploys, clearer ownership. The problem is how CloudFormation handles values shared between stacks.

When Stack A exports a value (a VPC ID, a security group ARN) and Stack B imports it, CloudFormation creates a hard dependency. You cannot modify or delete that export while any other stack is consuming it. CloudFormation will block the update and leave you stuck — Stack A cannot deploy because the export is in use, and Stack B may be in a broken state because it depends on something that no longer exists as expected. Getting out requires carefully coordinating the removal of the import before you can change the export.

**The fix: use SSM Parameter Store instead of CloudFormation exports.**

Stack A writes its outputs to SSM:

```java
StringParameter.Builder.create(this, "VpcIdParam")
    .parameterName("/infra/vpc/id")
    .stringValue(vpc.getVpcId())
    .build();
```

Stack B reads from SSM at deploy time:

```java
String vpcId = StringParameter.valueForStringParameter(this, "/infra/vpc/id");
```

No CloudFormation export, no hard dependency, no blocked deployments. Stacks can be updated and deployed independently. SSM also gives you a clean place to browse shared infrastructure values and reference them from outside CDK (application config, scripts, other tools).

## Testing

Testing in CDK is limited to validating the synthesized CloudFormation template — you are not testing infrastructure behaviour, you are testing that your code generates the JSON you expect:

- **Unit tests** — JUnit assertions against the synthesized template (e.g. "does this stack contain an S3 bucket with versioning enabled")
- **Integration tests** — deploy to an isolated environment and validate via AWS SDK
- No native plan/apply preview; you must deploy to see what actually happens

## Pros

- Familiar Java constructs — loops, conditionals, reusable classes
- Full IDE support, refactoring, type safety
- Unit testing with JUnit
- Good for teams already invested in Java who want infrastructure close to application code

## Cons

- Generates CloudFormation — debugging complex stacks means reading generated JSON/YAML
- More boilerplate than HCL for straightforward infrastructure
- Drift detection relies on CloudFormation, which has no visibility into out-of-band changes
- Importing existing infrastructure can be awkward
- Smaller community example base compared to Terraform, especially in Java vs TypeScript/Python
- Deployments are slower than Terraform's direct API approach

## vs Terraform

For repeatable, standardised infrastructure with a clear plan/apply workflow and reliable drift detection, [Terraform](../terraform/) is the stronger choice. CDK makes sense when infrastructure is deeply coupled to application code and the team is committed to a single language across both.

## Resources

- [AWS CDK documentation](https://docs.aws.amazon.com/cdk/v2/guide/home.html)
- [AWS CDK API reference](https://docs.aws.amazon.com/cdk/api/v2/)
- [CDK Patterns](https://cdkpatterns.com/) — community example library
- [AWS CDK GitHub](https://github.com/aws/aws-cdk)
