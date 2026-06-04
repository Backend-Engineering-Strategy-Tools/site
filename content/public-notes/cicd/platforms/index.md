---
title: "CI/CD Platforms"
date: 2024-01-01
draft: false
showReadingTime: false
layout: single
tags: ["cicd", "tekton", "jenkins", "harness", "bitbucket", "github-actions", "argo", "pipelines"]
---

There are many CI/CD platforms and the choice between them matters less than it appears. All of them are thin orchestration wrappers — trigger on a git event, run some steps, report the result. The build logic itself should live in [Make](/public-notes/cicd/make/) or [Dagger](/public-notes/cicd/dagger/), not inside the pipeline definition. See [One Command, Any Pipeline](/thinking/one-command-any-pipeline/).

## CruiseControl

The early pioneer, released in 2001. CruiseControl introduced continuous integration as a practice — polling a source repository, building on every change, sending email on failure. Configuration was XML, the dashboard was a web page, and it ran on a server you managed yourself. Most of the concepts in modern CI trace back here. Largely historical today but worth knowing as the origin point.

## Hudson

Hudson was Sun Microsystems' take on CI — a Java application with a plugin ecosystem that made it far more extensible than CruiseControl. It gained wide adoption in enterprise Java shops during the late 2000s. When Oracle acquired Sun, the project forked. The community fork became Jenkins; the Oracle-maintained branch kept the Hudson name and eventually faded. Hudson is effectively dead.

## Jenkins

The fork that won. Jenkins took Hudson's plugin architecture and ran with it — today it has over 1800 plugins covering almost every tool in the ecosystem. A Jenkinsfile defines the pipeline as Groovy DSL and lives in the repository alongside the code. Jenkins is the most widely deployed self-hosted CI server and the default answer in many enterprises. The flip side: it is heavyweight, the Groovy DSL has sharp edges, and complex pipelines are difficult to test outside of Jenkins itself.

## Jenkins X

Jenkins X is a cloud-native reimagining of Jenkins for Kubernetes. It imposes a strongly opinionated GitOps workflow — pull requests promote through environments, preview environments spin up automatically, everything is driven by Git events. Built on Tekton under the hood. If you want opinionated Kubernetes CI/CD without building the conventions yourself, Jenkins X is one answer. If you want more control over the pipeline structure, raw Tekton gives you the primitives without the opinions.

## Tekton

Kubernetes-native CI/CD where pipelines, tasks, and triggers are all Kubernetes CRDs — defined in YAML and applied to a cluster, running as pods. No separate CI server to maintain, no external SaaS dependency. CI runs in the same cluster as your workloads using the same RBAC, secrets, and storage primitives. The core primitives are `Task` (a sequence of container steps), `Pipeline` (an ordered set of tasks), `PipelineRun` (an execution), and `Trigger` (an event listener that creates runs). The pattern that works well: keep Tasks thin and have them call `make <target>` — Tekton handles orchestration, Make handles logic.

## GitHub Actions

GitHub's built-in CI/CD, available to any repository on GitHub. Zero infrastructure, zero setup — if your code is on GitHub, Actions is already there. Workflows are YAML files in `.github/workflows/`, triggered by git events, running on GitHub-managed runners. A large marketplace of pre-built actions covers most common tasks. The zero-friction default for open source projects and small teams. See the [GitHub Actions](/public-notes/cicd/github/) note for more detail.

## Argo Workflows

A Kubernetes-native workflow engine from the Argo project. Where Tekton models CI primitives (Tasks, Pipelines), Argo Workflows is a general-purpose DAG executor — it can run any containerised workload as a directed acyclic graph of steps, with fan-out, fan-in, conditionals, and retry logic. Widely used as the execution layer under other tools (including Dagger on Kubernetes). Pairs well with [ArgoCD](/public-notes/cicd/argo-cd/) for a fully Argo-based GitOps stack. See the [Argo](/public-notes/cicd/argo-project/) note for coverage of the full Argo ecosystem including Rollouts, Events, and Kargo.

## Bitbucket Pipelines

Bitbucket's built-in CI/CD, integrated directly with Atlassian's hosting. If your code is already in Bitbucket, Pipelines is the zero-infrastructure option — the same position GitHub Actions occupies for GitHub users. Workflows are YAML, steps run in Docker containers, and Atlassian handles the runner infrastructure. Tightly integrated with Jira for deployment tracking. The right choice when you're already in the Atlassian ecosystem and don't want to introduce a separate CI tool.

## Harness

A commercial platform with a broader scope than most CI/CD tools — it covers CI, CD, feature flags, cloud cost management, and security testing under one roof. Enterprise-focused, with AI-assisted pipeline generation and strong support for policy and governance across large engineering organisations. Harness is the answer when the organisation needs a managed platform with SLAs, support, and audit trails rather than self-hosted infrastructure. Pricing reflects that positioning.

## Resources

- [Tekton documentation](https://tekton.dev/docs/)
- [Jenkins documentation](https://www.jenkins.io/doc/)
- [Jenkins X documentation](https://jenkins-x.io/docs/)
- [Argo Workflows documentation](https://argoproj.github.io/argo-workflows/)
- [Bitbucket Pipelines documentation](https://support.atlassian.com/bitbucket-cloud/docs/bitbucket-pipelines/)
- [Harness documentation](https://developer.harness.io/)
