---
title: "GitHub Actions"
date: 2024-01-01
draft: false
showReadingTime: false
layout: single
tags: ["github-actions", "cicd", "pipelines", "containers"]
---

For a small project or proof of concept, the cost of building a CI environment often exceeds the cost of the project itself. Spinning up a Tekton cluster, installing Argo Workflows, or maintaining a Jenkins server is real infrastructure — with real setup time, real maintenance overhead, and real dependencies to keep running.

GitHub Actions is already there. If your code is on GitHub, you have CI. No extra infrastructure, no additional accounts, a marketplace of pre-built integrations for almost everything you need. For open source projects and small teams it is the pragmatic default: free, integrated, and good enough for the standard build → test → publish pipeline.

## Workflow anatomy

Workflows live in `.github/workflows/` as YAML files. A workflow has triggers, jobs, and steps:

```yaml
name: Build and publish

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build
        run: make build

      - name: Test
        run: make test

      - name: Push image
        if: github.ref == 'refs/heads/main'
        run: |
          echo "${{ secrets.DOCKER_HUB_TOKEN }}" | docker login -u ${{ secrets.DOCKER_HUB_USER }} --password-stdin
          docker push myorg/myimage:latest
```

`on:` defines what triggers the workflow. `runs-on:` selects the runner. `uses:` pulls a pre-built action from the marketplace. `run:` executes shell commands directly.

The `if:` condition on the push step is a common pattern: run tests on every pull request, but only publish on merge to `main`.

## Secrets

GitHub Secrets store credentials without putting them in the repository. Add them under **Settings → Secrets and variables → Actions**, then reference them in workflows as `${{ secrets.MY_SECRET }}`.

For pushing to external services — Docker Hub, a package registry, a cloud provider — this is the integration point. The workflow authenticates using the secret, the secret itself never appears in logs or code.

### Organisation secrets

Secrets can be set at the organisation level and inherited by all repositories — no per-repo configuration needed. Useful for shared CI credentials reused across many repos.

Path: github.com/`<org>` → Settings → Secrets and variables → Actions → **New organisation secret**

Set **Repository access** to "All repositories" or a selected subset once you know which repos need it.

A worked example — shared image publishing credentials:

```
DOCKERHUB_TOKEN     # hub.docker.com → Account → Security → Access Tokens
DAGGER_CLOUD_TOKEN  # cloud.dagger.io → Organisation → Tokens
```

Set once at org level; every `image-*` repo inherits them. Workflows reference them identically to repo secrets: `${{ secrets.DOCKERHUB_TOKEN }}`. See [Dagger](/public-notes/cicd/dagger/) for `DAGGER_CLOUD_TOKEN` context.

## Environments

Environments add a protection layer on top of secrets. Define named environments (e.g. `staging`, `production`) and configure:

- **Required reviewers** — a human must approve before the job runs
- **Environment secrets** — secrets scoped to that environment only, not available to other jobs
- **Wait timer** — a mandatory delay before deployment proceeds

A deployment job targets an environment by name:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy
        run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.PROD_API_KEY }}
```

The job pauses for approval before running. Useful for open source projects where the pipeline is public but deployment credentials are not.

## Marketplace actions

Most common tasks have a pre-built action. A few worth knowing:

| Action | What it does |
|---|---|
| `actions/checkout` | Clone the repository |
| `actions/setup-go` | Install a specific Go version |
| `docker/setup-buildx-action` | Enable multi-arch Docker builds |
| `docker/build-push-action` | Build and push a container image |
| `helm/kind-action` | Spin up a local Kubernetes cluster for tests |

Using marketplace actions trades control for speed. For a POC or small project that's the right trade. For anything critical, pin the action to a specific commit SHA rather than a tag — tags are mutable.

## Self-hosted runners

GitHub-hosted runners (`ubuntu-latest`, `windows-latest`) cover most cases. Self-hosted runners make sense when you need access to an internal network, specific hardware (a GPU, specialised build machine), or want to avoid per-minute billing at scale.

At that point you are closer to running a full CI platform, which is where tools like [Tekton](/public-notes/cicd/platforms/) or [Argo Workflows](https://argoproj.github.io/argo-workflows/) become relevant — they give you the same kind of pipeline orchestration but running entirely on your own infrastructure.

## Resources

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Marketplace](https://github.com/marketplace?type=actions)
- [Workflow syntax reference](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions)
