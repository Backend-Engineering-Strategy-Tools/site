---
title: "Terraform"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

Terraform is HashiCorp's infrastructure-as-code tool: you declare what infrastructure you want in HCL (HashiCorp Configuration Language), and Terraform figures out how to create, update, or destroy resources to match that declaration. It works across providers — AWS, GCP, Azure, Kubernetes, GitHub, and hundreds more — through a plugin architecture.

## Core concepts

**Providers** are plugins that translate Terraform resources into API calls. Declared in `required_providers`:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}
```

**Resources** are the things you're managing — an EC2 instance, an S3 bucket, a DNS record:

```hcl
resource "aws_s3_bucket" "assets" {
  bucket = "my-app-assets"
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

**Data sources** read existing infrastructure without managing it — useful for referencing shared resources:

```hcl
data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = ["main"]
  }
}
```

## State

Terraform tracks what it has created in a **state file** (`terraform.tfstate`). This is the source of truth for what exists — Terraform computes diffs against state, not live infrastructure.

In teams, state must be stored remotely and locked during operations:

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "terraform-locks"
  }
}
```

Never commit state files to version control — they contain secrets and will diverge between team members.

## The plan/apply cycle

```bash
terraform init      # download providers, initialise backend
terraform plan      # show what will change — read this carefully
terraform apply     # create/update/destroy resources
terraform destroy   # tear everything down
```

`terraform plan` is the key step: it shows exactly what Terraform intends to do before touching anything. Review the plan — a `+` is create, `~` is update in-place, `-/+` is replace (destroy and recreate), `-` is destroy.

## Variables and outputs

Variables make configurations reusable:

```hcl
variable "environment" {
  type    = string
  default = "staging"
}

resource "aws_instance" "app" {
  ami           = "ami-0abc123"
  instance_type = var.environment == "prod" ? "t3.medium" : "t3.micro"
  tags = {
    Environment = var.environment
  }
}
```

Pass values via `terraform.tfvars`, environment variables (`TF_VAR_environment`), or the `-var` flag.

Outputs expose values after apply — useful for passing information between modules:

```hcl
output "bucket_name" {
  value = aws_s3_bucket.assets.bucket
}
```

## Modules

Modules are reusable, composable units of Terraform configuration — a directory of `.tf` files called as a block:

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "main"
  cidr = "10.0.0.0/16"
  azs  = ["eu-west-1a", "eu-west-1b"]
}
```

Encapsulate common patterns (a standard VPC setup, an ECS service, a Lambda with IAM role) in a module rather than repeating the same resources across configurations.

## Multiple environments

Workspaces exist but are limited — shared state, easy to confuse, no real isolation. The two patterns that actually work in practice:

**Folder per environment** — `envs/dev/`, `envs/staging/`, `envs/prod/` each have their own backend config and `tfvars`. Explicit, auditable, easy to reason about. The downside is duplication across env directories, mitigated by shared modules.

**Terragrunt** — a thin wrapper around Terraform that eliminates the duplication. Environments inherit from a root config, each only overrides what differs. One place to bump a module version and it propagates everywhere.

### Terragrunt

Terragrunt solves the main friction of the folder-per-environment pattern: repetition. Backend config, provider version, module source — these are the same across every environment. Terragrunt lets you define them once at the root and inherit downward.

A typical layout:

```
infra/
  terragrunt.hcl          # root config — backend, provider defaults
  dev/
    terragrunt.hcl        # env-level overrides
    vpc/
      terragrunt.hcl      # module call
    eks/
      terragrunt.hcl
  prod/
    terragrunt.hcl
    vpc/
      terragrunt.hcl
    eks/
      terragrunt.hcl
```

The root `terragrunt.hcl` defines the remote state pattern once:

```hcl
remote_state {
  backend = "s3"
  config = {
    bucket = "my-terraform-state"
    key    = "${path_relative_to_include()}/terraform.tfstate"
    region = "eu-west-1"
  }
}
```

Each module's `terragrunt.hcl` just declares its source and inputs:

```hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "git::https://github.com/myorg/terraform-modules.git//vpc?ref=v1.4.0"
}

inputs = {
  cidr = "10.1.0.0/16"
  environment = "dev"
}
```

Key commands:

```bash
terragrunt plan              # plan a single module
terragrunt apply             # apply a single module
terragrunt run-all plan      # plan all modules in a directory tree
terragrunt run-all apply     # apply all, respects dependency order
```

`run-all` handles dependency ordering automatically — if `eks` depends on `vpc`, Terragrunt applies `vpc` first.

## Testing and validation

Terraform has multiple layers of validation, from syntax checking to full integration tests against real infrastructure.

**Syntax and input validation**

```bash
terraform validate    # checks syntax, module references, variable constraints
terraform plan        # dry run — shows exactly what will change before touching anything
```

`validate` catches configuration errors early. `plan` is the key safety step — a `+` is create, `~` is update in-place, `-/+` is replace, `-` is destroy. Read it before every apply.

**Native unit tests (v1.6+)**

Tests live in `.tftest.hcl` files alongside the configuration. `run` blocks execute a plan or apply in isolation; `assert` blocks check the result:

```hcl
run "vpc_has_correct_cidr" {
  command = plan

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR does not match expected value"
  }
}
```

Run with `terraform test`. Good for validating modules before promotion.

**Integration testing**

For end-to-end validation against real AWS resources, [Terratest](https://terratest.gruntwork.io/) is the most widely used framework — Go tests that deploy infrastructure, run assertions via the AWS SDK, then tear it all down.

**Policy and compliance**

OPA/Rego, Conftest, or HashiCorp Sentinel can enforce policies at plan time — before anything is deployed. Useful for ensuring security groups are not wide open, IAM roles follow least privilege, tags are present on all resources.

## Resources

- [Terraform documentation](https://developer.hashicorp.com/terraform/docs)
- [Terraform Registry](https://registry.terraform.io/) — providers and modules
- [terraform-aws-modules](https://github.com/terraform-aws-modules) — well-maintained AWS module library
- [Terragrunt documentation](https://terragrunt.gruntwork.io/docs/)
