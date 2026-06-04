---
title: "Nexus Repository"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["nexus", "artifacts", "registry", "maven", "docker", "npm"]
---

Sonatype Nexus Repository Manager is a universal artifact repository. It stores and serves build artifacts — Maven JARs, npm packages, Docker images, Helm charts, PyPI packages, raw binaries — from a single platform. It operates in three modes: hosted (your own artifacts), proxy (a local mirror of an upstream registry), and group (a virtual repository that aggregates hosted and proxy repos behind one URL).

## Why it exists

Two problems: you want a private registry for internal artifacts (container images, internal libraries), and you want to cache upstream registries to reduce build times, avoid rate limits, and insulate builds from upstream outages. Nexus solves both. Point your build tools at Nexus; Nexus fetches from upstream on first request and caches, or serves from your hosted repos.

## Repository types

```
# Maven proxy — caches Maven Central
https://nexus.example.com/repository/maven-central/

# Maven hosted — your internal JARs
https://nexus.example.com/repository/maven-releases/
https://nexus.example.com/repository/maven-snapshots/

# Docker hosted — your container images
https://nexus.example.com/repository/docker-hosted/

# npm proxy — caches registry.npmjs.org
https://nexus.example.com/repository/npm-proxy/
```

## Docker integration

Nexus can expose a hosted Docker registry on a dedicated port. Configure the Docker daemon to trust the registry, then push and pull normally:

```bash
docker login nexus.example.com:8082
docker tag myimage:latest nexus.example.com:8082/myimage:latest
docker push nexus.example.com:8082/myimage:latest
```

## Maven integration

Point Maven at Nexus by configuring `settings.xml` to use the Nexus group repository as a mirror:

```xml
<mirrors>
  <mirror>
    <id>nexus</id>
    <mirrorOf>*</mirrorOf>
    <url>https://nexus.example.com/repository/maven-public/</url>
  </mirror>
</mirrors>
```

All dependency resolution goes through Nexus. Cached. Air-gapped builds are possible by pre-populating the cache.

## Resources

- [Nexus Repository documentation](https://help.sonatype.com/repomanager3)
- [Sonatype Nexus OSS](https://www.sonatype.com/products/sonatype-nexus-oss)
