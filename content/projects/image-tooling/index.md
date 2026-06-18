---
title: "Image Tooling"
date: 2026-06-18
draft: false
showReadingTime: false
layout: single
tags: ["docker", "dagger", "cicd", "kubernetes", "tooling"]
---

Versioned, multi-arch Docker images for Kubernetes workflows — built with [Dagger](/public-notes/cicd/dagger/), published to Docker Hub, triggered by a version tag.

The motivation is in [Shared Tooling Images](/thinking/shared-tooling-images/): one image, consistent versions, three contexts — CI, local, colleagues.

---

## Images

| GitHub repo | Docker Hub | Contents |
|-------------|-----------|---------|
| [`image-tooling`](https://github.com/Backend-Engineering-Strategy-Tools/image-tooling) | `senare/tooling-k8s` | kubectl, helm, kustomize, argocd CLI, k9s, jq, yq |
| `image-tooling` | `senare/tooling-k8s-aws` | `tooling-k8s` + AWS CLI |
| `image-tooling` | `senare/tooling-k8s-openstack` | `tooling-k8s` + OpenStack CLI |
| [`image-buildx`](https://github.com/Backend-Engineering-Strategy-Tools/image-buildx) | `senare/buildx` | CI builder — Docker buildx, AWS CLI, Dagger CLI |
| [`image-pandoc`](https://github.com/Backend-Engineering-Strategy-Tools/image-pandoc) | `senare/pandoc` | PDF generation — pandoc + TeX Live |

All images publish as multi-arch manifests: `linux/amd64` + `linux/arm64`.

---

## Quick start

**Interactive shell with kubeconfig mounted:**

```bash
docker run -it --rm \
  -v ~/.kube:/mnt/kube:ro \
  -v $(pwd):/work \
  -w /work \
  docker.io/senare/tooling-k8s:latest
```

The image entry point symlinks `/mnt/kube` → `/root/.kube` on startup, so `kubectl` picks it up immediately.

**Shell alias for daily use:**

```bash
alias k8s='docker run -it --rm \
  -v ~/.kube:/mnt/kube:ro \
  -v $(pwd):/work -w /work \
  docker.io/senare/tooling-k8s:latest'

k8s helm lint .
k8s kubectl get pods -n argocd
```

**In CI (GitHub Actions):**

```yaml
- name: Lint chart
  run: docker run --rm -v ${{ github.workspace }}:/work -w /work docker.io/senare/tooling-k8s:latest helm lint .
```

Or reference the image directly as the job container — no install step needed.

---

## Setup (contributors / maintainers)

Credentials are set once as [GitHub org-level secrets](/public-notes/cicd/github/) and inherited by all `image-*` repos automatically.

| Secret | Where to get it |
|--------|----------------|
| `DOCKERHUB_TOKEN` | hub.docker.com → Account → Security → Access Tokens (Read, Write, Delete) |
| `DAGGER_CLOUD_TOKEN` | cloud.dagger.io → Organisation → Tokens |

Path: github.com/Backend-Engineering-Strategy-Tools → Settings → Secrets and variables → Actions → New organisation secret.

---

## Releasing

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

The GitHub Actions workflow triggers on `v*.*.*` tags, calls `dagger call publish-multi-arch`, and pushes both `senare/<image>:v1.0.0` and `senare/<image>:latest` to Docker Hub. Pipeline trace at [cloud.dagger.io](https://dagger.cloud/).

---

## Links

- [Backend-Engineering-Strategy-Tools org](https://github.com/Backend-Engineering-Strategy-Tools)
- [senare/ on Docker Hub](https://hub.docker.com/u/senare)
- [Dagger pipelines](/public-notes/cicd/dagger/)
