---
title: "Dagger"
date: 2026-06-02
draft: false
showReadingTime: false
layout: single
tags: ["dagger", "cicd", "containers", "go", "pipelines"]
---

Your build script works on your laptop. It breaks in CI because a tool version differs. It breaks for a colleague because they're on a different OS. You're writing `apt-get install` steps in YAML and maintaining a separate script for local builds.

Dagger solves this the same way Docker solved "works on my machine" for applications: run everything in containers. Every pipeline step executes inside a defined container image — identically on your laptop, in GitHub Actions, or inside a Kubernetes pod. The Dagger Engine is a containerised daemon your pipeline calls into. Where it runs is an operational detail; what it does is defined once in code.

The other thing Dagger gives you that YAML-based CI systems don't: your pipeline is real code. Write it in Go (or TypeScript or Python), build a library of reusable functions, share it across projects, and test it the same way you'd test any other code.

## Module

A Dagger module is a Go package that exposes pipeline functions. Initialise one in your repo:

```bash
dagger init --sdk go --name my-pipeline
dagger develop
```

`dagger init` creates the scaffolding. `dagger develop` generates the Go bindings and drops you into a module ready to edit. A minimal function:

```go
package main

import (
    "context"
    "dagger/my-pipeline/internal/dagger"
)

type MyPipeline struct{}

func (m *MyPipeline) Build(ctx context.Context, src *dagger.Directory) *dagger.Container {
    return dag.Container().
        From("golang:1.22").
        WithDirectory("/src", src).
        WithWorkdir("/src").
        WithExec([]string{"go", "build", "./..."})
}
```

Call it from anywhere — local terminal, CI step, Argo workflow:

```bash
dagger call build --src .
```

## Library pattern

Because a module is just Go code, you build it like any other Go library: shared types, helper functions, unit tests. The pattern that works well in practice is a single internal module that codifies your organisation's conventions — base images, registry credentials, standard lint and test steps — and each project imports it.

A fix to the shared module propagates everywhere. You're not updating 40 YAML files.

Testing pipeline logic with `go test` works normally. A test that calls `dagger call` exercises the real container execution, not a mock. This is the thing YAML pipelines can't give you: a fast feedback loop on the pipeline logic itself before it hits CI.

## Multi-arch builds

Dagger has first-class support for multi-architecture container builds. Pass the platform as an argument:

```go
func (m *MyPipeline) BuildMultiArch(ctx context.Context, src *dagger.Directory) []*dagger.Container {
    platforms := []dagger.Platform{"linux/amd64", "linux/arm64"}
    containers := make([]*dagger.Container, len(platforms))
    for i, platform := range platforms {
        containers[i] = dag.Container(dagger.ContainerOpts{Platform: platform}).
            From("golang:1.22").
            WithDirectory("/src", src).
            WithWorkdir("/src").
            WithExec([]string{"go", "build", "./..."})
    }
    return containers
}
```

Same function, multiple targets, no extra tooling.

## Running in Kubernetes with Argo Workflows

Dagger Engine runs as a container. In Kubernetes, you run it as a sidecar or dedicated pod and point `dagger call` at it via the `_EXPERIMENTAL_DAGGER_RUNNER_HOST` environment variable. Each Argo Workflows step calls `dagger call <function>` — Argo handles DAG orchestration, retries, and observability; Dagger handles the build execution inside containers.

The split is clean: Argo owns workflow-level concerns, Dagger owns build reproducibility.

## Key commands

| Command | What it does |
|---|---|
| `dagger init --sdk go` | Initialise a new module with the Go SDK |
| `dagger develop` | Generate bindings, enter the development loop |
| `dagger functions` | List available functions in the current module |
| `dagger call <function> [args]` | Invoke a pipeline function |
| `dagger run <command>` | Run an arbitrary command with Dagger Engine available |

## Resources

- [Dagger documentation](https://docs.dagger.io/)
- [Go SDK reference](https://docs.dagger.io/api/sdk/go)
- [Daggerverse — community modules](https://daggerverse.dev/)
