---
title: "Shared Tooling Images — One Image, Three Contexts"
date: 2026-06-02
draft: false
showReadingTime: false
tags: ["docker", "cicd", "tooling", "devops", "containers"]
---

The problem with per-context tooling: CI uses one version of a linter, a developer's machine has another, a colleague has a third. Someone upgrades locally, the pipeline fails. Someone pins the pipeline, local runs drift. The maintenance surface is the number of places you install tools multiplied by the number of people on the team.

The fix is one Docker image that travels across all three contexts:

1. **CI/CD** — the pipeline pulls the image, runs the same tools
2. **Local development** — developers run the image instead of installing tools natively
3. **Colleagues** — same image, same versions, no setup docs to go stale

When you need to upgrade a tool, you change one Dockerfile and cut a new tag. Everyone gets it on next pull. No coordination required.

---

## Why Docker?

There are other ways to solve this — dotfiles, Nix, OS package managers, VMs, cloud-init. All valid in different contexts.

The reason Docker makes sense here is that we are already working in a Kubernetes ecosystem where containers are the starting point. Most CI systems support Docker and OCI-compatible images natively. So the question becomes: is it worth introducing a different tool management approach alongside containers, or is it less costly to stay consistent?

Personally, I lean toward staying consistent. Your mileage may vary depending on your stack.

---

## What Goes in the Image

The principle: include anything that needs to be consistent across contexts. Linters, formatters, build tools, CLI utilities.

*Not the runtime — that is the application's own image.*

What specifically goes in depends on the target platform. A Kubernetes-only image looks different from one that also includes a cloud provider CLI. Adding tools increases the maintenance burden, so keep each image focused. That is also why there are multiple images — see [The Repos](#the-repos) below.

Typical candidates:

- `kubectl`, `helm`, `kustomize`
- Linters and formatters for the languages in use
- `jq`, `yq`, `curl` and similar utilities
- Cloud provider CLI where needed (`aws`, `openstack`)

---

## Versioning

Follow SemVer — image tag equals version. Merge to main triggers a release. No need to complicate it beyond trunk-based development.

Before merging, build and publish an image from the branch so the change can be tested and verified before it lands on mainline. The branch image is short-lived and not promoted to `latest` until the merge.

---

## Usage Patterns

A shell alias or Makefile target wraps the `docker run` so nobody has to remember the full invocation:

```bash
alias toolbox="docker run -it --rm -v $(pwd):/work -w /work image:latest"
```

Then `toolbox helm lint .` or `toolbox kubectl apply -f .` works the same locally as it does in CI.

**Interactive sessions** are where this pattern pays off beyond CI. Drop into a persistent terminal with the right context already loaded — kubeconfig mounted in, cloud credentials available, working directory set:

```bash
docker run -it --rm \
  -v $(pwd):/work \
  -v ~/.kube:/root/.kube:ro \
  -w /work \
  image:latest bash
```

You get a shell that looks the same for everyone on the team, regardless of what is installed on their machine.

For interactive use it is worth including a help script that runs on entry — either via `ENTRYPOINT` or by sourcing it from `.bashrc` inside the image. It should print what tools are available, their versions, and any common usage examples. Keeps the image self-documenting: a new colleague drops in and immediately knows what they have to work with without reading a README.

```bash
# example /usr/local/bin/toolbox-help
echo "=== Toolbox ==="
echo "kubectl   $(kubectl version --client -o json | jq -r '.clientVersion.gitVersion')"
echo "helm      $(helm version --short)"
echo "aws       $(aws --version 2>&1)"
echo ""
echo "Run 'toolbox-help' at any time to see this again."
```

In CI the step just references the image directly — no installation step, no version pinning in the pipeline config beyond the image tag.

---

## The Repos

Three images, each a superset of the previous:

| Repo                    | Contents                                                      |
|-------------------------|---------------------------------------------------------------|
| `tooling-k8s`           | kubectl, helm, kustomize, jq, yq — generic Kubernetes tooling |
| `tooling-k8s-aws`       | `tooling-k8s` + AWS CLI                                       |
| `tooling-k8s-openstack` | `tooling-k8s` + OpenStack CLI                                 |

To be built and published to the [GitHub org](https://github.com/Backend-Engineering-Strategy-Tools).

---
