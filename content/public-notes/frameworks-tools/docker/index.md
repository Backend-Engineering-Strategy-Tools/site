---
title: "Docker & OCI"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

Docker packages applications and their dependencies into portable, reproducible units called containers. Unlike virtual machines, containers share the host kernel — they're isolated processes, not emulated hardware. This makes them fast to start, light on resources, and consistent across environments: the same image runs on a developer's laptop, in CI, and in production.

Docker popularised containers, but the underlying standard is now open. The **OCI (Open Container Initiative)** defines three specifications:

- **Image spec** — the format of a container image: layers, config, manifest
- **Runtime spec** — how a container is run: namespaces, cgroups, lifecycle
- **Distribution spec** — how images are pushed and pulled from registries

Any tool that produces an OCI image can run on any OCI-compliant runtime. Docker is one implementation. It is still the most natural entry point and the `docker` CLI remains the most familiar interface, but it is worth knowing that the ecosystem is broader than Docker Inc.

## OCI images and containers

An **image** is a read-only, layered filesystem snapshot built from a Dockerfile — each layer is a diff on top of the previous one. A **container** is a running instance of an image — an isolated process with its own filesystem, network interface, and process space, sharing the host kernel.

```bash
docker build -t myapp:1.0 .        # build OCI image from Dockerfile
docker run -p 8080:8080 myapp:1.0  # start container
docker ps                          # list running containers
docker exec -it <id> bash          # shell into a running container
```

Images are stored in registries — Docker Hub, GitHub Container Registry, ECR, Nexus. All speak the OCI distribution spec, so images built with any tool push and pull the same way.

## Dockerfile

The Dockerfile defines how an image is built — each instruction adds a layer:

```dockerfile
FROM golang:1.22-alpine AS build
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o /app/server .

FROM alpine:3.19
COPY --from=build /app/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

**Multi-stage builds** keep the final image lean: the first stage compiles using the full toolchain, the second copies only the binary. No compiler, no source, no build cache in the image you ship.

Order matters for layer caching — put things that change rarely (dependency downloads) before things that change often (source code). A cache miss invalidates all subsequent layers.

## Volumes and bind mounts

Containers have ephemeral filesystems — anything written inside is lost when the container stops. Persist data with volumes:

```bash
docker volume create pgdata
docker run -v pgdata:/var/lib/postgresql/data postgres:16
```

For local development, bind mounts map a host directory into the container:

```bash
docker run -v $(pwd):/app -w /app node:20 npm test
```

## Networking

Containers on the same Docker network can reach each other by name. Docker Compose creates a default network automatically; named networks can be created explicitly:

```bash
docker network create backend
docker run --network backend --name db postgres:16
docker run --network backend myapp   # can reach 'db' by hostname
```

## Podman

Podman is a drop-in Docker replacement that runs without a daemon and without root. The CLI is intentionally compatible:

```bash
alias docker=podman   # usually just works
```

Rootless containers mean a compromised container process cannot escalate to host root. Daemonless means no long-running background service with broad system access. On RHEL and Fedora, Podman is the default. For CI environments and security-conscious setups it is the better choice.

Podman also supports **pods** — groups of containers sharing a network namespace, mirroring the Kubernetes pod model. Useful for local development that needs to mirror how things will run in the cluster.

## Buildah

Buildah builds OCI images without a Docker daemon. It can build from a Dockerfile or construct images programmatically using shell commands — useful in CI pipelines where running a privileged Docker daemon is undesirable:

```bash
buildah bud -t myapp:1.0 .          # build from Dockerfile
buildah push myapp:1.0 registry/myapp:1.0
```

Buildah and Podman share the same underlying storage, so images built with Buildah are immediately available to Podman.

## Docker Compose

Compose manages multi-container applications defined in `compose.yml`:

```yaml
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      DATABASE_URL: postgres://app:secret@db/appdb
    depends_on:
      - db

  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: secret

volumes:
  pgdata:
```

```bash
docker compose up -d      # start in background
docker compose logs -f    # stream logs
docker compose down       # stop and remove containers
```

Compose is useful for local development environments. It is a shame it exists as a separate abstraction — it taught people to think in multi-container terms without teaching them Kubernetes, and then left them with a gap to cross when they needed to go to production. That said, it is practical for what it does and is not going away.

For production orchestration, see [Kubernetes](../../cloud-infrastructure/kubernetes/).

## Skopeo

Skopeo works with OCI images directly — copy, inspect, and convert — without pulling them to local storage. Useful in pipelines and for auditing registries:

```bash
# Inspect an image without pulling it
skopeo inspect docker://registry.example.com/myapp:1.0

# Copy between registries without touching local disk
skopeo copy docker://source-registry/myapp:1.0 docker://dest-registry/myapp:1.0

# Copy to a local OCI layout
skopeo copy docker://myapp:1.0 oci:myapp-local:1.0
```

`skopeo inspect` is particularly useful for checking image metadata, digest, and labels in CI before deciding whether to promote an image.

## ORAS

ORAS (OCI Registry As Storage) pushes and pulls arbitrary artifacts to OCI registries — not just container images. Helm charts, SBOMs, attestations, Terraform modules, binary releases — anything can be stored in a registry that speaks OCI distribution spec:

```bash
# Push a file as an OCI artifact
oras push registry.example.com/myapp-sbom:1.0 sbom.json:application/spdx+json

# Pull it back
oras pull registry.example.com/myapp-sbom:1.0
```

This matters because it means a single registry can become the distribution mechanism for the entire software supply chain — image, SBOM, signature, attestation — all with the same access controls and audit trail.

## Useful practices

- Use specific image tags (`postgres:16.2`, not `postgres:latest`) — `latest` changes under you
- Reference images by digest in production (`myapp@sha256:abc123`) — tags are mutable, digests are not
- Run as a non-root user: `USER appuser` in the Dockerfile
- Add a `.dockerignore` to exclude `.git`, `node_modules`, build artefacts from the build context
- Keep images small — large images are slow to push, pull, and scan

## Resources

- [OCI specifications](https://opencontainers.org/)
- [Docker documentation](https://docs.docker.com/)
- [Podman documentation](https://podman.io/docs)
- [Buildah documentation](https://buildah.io/)
- [Skopeo GitHub](https://github.com/containers/skopeo)
- [ORAS documentation](https://oras.land/docs/)
