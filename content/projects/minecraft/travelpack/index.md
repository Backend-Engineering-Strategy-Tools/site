---
title: "TravelPack — Minecraft Fabric Mod"
date: 2026-06-24
draft: false
showReadingTime: false
layout: single
tags: ["minecraft", "java", "fabric", "gradle", "cicd", "gaming", "homelab"]
---

A Fabric mod for Minecraft 1.21.4, started with the kids. It also serves as the concrete Java artifact for exploring two different build models — GitHub-hosted CI and a DIY on-prem pipeline on the homelab cluster.

## What it adds

**Sleeping Bag** — a lightweight portable bedroll (stackable up to 16) that lets players skip the night without placing a permanent bed. Can be crafted up into a White Bed if you settle somewhere.

**Horse Bedroll Slot** — horses get a dedicated inventory slot for the sleeping bag, which appears draped across the horse's back. No more awkwardly storing it in a chest.

## Build toolchain

Source on GitHub → [Backend-Engineering-Strategy-Tools/travelpack](https://github.com/Backend-Engineering-Strategy-Tools/travelpack).

Gradle with [Fabric Loom](https://github.com/FabricMC/fabric-loom) 1.9. Targets Minecraft 1.21.4 / Java 21. Ships with multi-language support (en, de, es, fr, sv) and a Patchouli in-game guide.

```bash
./gradlew build        # Compile and package — output to build/libs/
./gradlew runClient    # Launch dev Minecraft client with mod loaded
./gradlew runServer    # Launch dev server
```

GitHub Actions CI is already wired — every push builds and the workflow is set up for Modrinth publishing once that's ready.

## Two pipeline models

The same mod, two different paths from source to running server — that contrast is the point.

**GitHub-hosted (cloud model):** GitHub Actions → build JAR → publish to Modrinth. Managed CI, low ops overhead, no infra to maintain. Already partially in place.

**On-prem DIY:** Dagger pipeline + ArgoWorkflow running on the cluster ([Gardener on Cleura](/projects/gardener/) is the context here). Same artifact, different path. The question is what you gain from owning the pipeline and what it costs you in complexity.

Running the mod on the Cleura-hosted Minecraft server closes the loop — something built locally, shipped through a pipeline, landing in an actual game session.

## Status

| | |
|---|---|
| Mod — sleeping bag, horse slot, recipes, i18n | done |
| GitHub Actions build | done |
| Modrinth publish | planned |
| Dagger pipeline on cluster | planned |
| ArgoWorkflow integration | planned |
| Deploy mod to Cleura-hosted server | planned |
