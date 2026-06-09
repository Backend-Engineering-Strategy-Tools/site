---
title: "Backstage"
draft: false
date: 2026-06-08
showReadingTime: false
layout: single
tags: ["backstage", "developer-portal", "idp", "platform-engineering", "cncf"]
---

Backstage is an open-source framework for building **Internal Developer Portals (IDPs)**. Created by Spotify, donated to the CNCF in 2022. The core idea: instead of every team maintaining their own scattered documentation, dashboards, and service scaffolding, you consolidate it into one place that the whole organisation uses.

You deploy your own instance. Backstage is not a SaaS — it is a framework you run and extend. The investment is real, but so is the payoff once adoption reaches critical mass.

## Core plugins

Backstage ships with a small core and a large plugin ecosystem. The four foundational pieces:

### Software Catalog

The catalog is a registry of everything your organisation owns: services, libraries, websites, pipelines, ML models, databases. Each entity is described by a `catalog-info.yaml` file committed alongside the code it describes.

```yaml
# catalog-info.yaml — lives in the repo root
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payments-service
  description: Handles payment processing
  tags:
    - java
    - payments
  annotations:
    github.com/project-slug: myorg/payments-service
    backstage.io/techdocs-ref: dir:.
spec:
  type: service
  lifecycle: production
  owner: payments-team
  system: commerce
```

Backstage imports entities from **Locations** — typically Git repositories. The catalog refreshes on a schedule and stays in sync with the `catalog-info.yaml` files across your repos.

### Scaffolder (Software Templates)

The Scaffolder lets platform teams publish templates for creating new projects. Developers pick a template, fill in a form, and Backstage creates the repo, applies the template, opens a PR — whatever the template defines.

Templates are defined in YAML and use `${{ parameters.name }}` substitution. Actions are either built-in (`publish:github`, `fetch:template`, `catalog:register`) or custom.

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: go-service
  title: Go Microservice
spec:
  owner: platform-team
  type: service
  parameters:
    - title: Service details
      properties:
        name:
          type: string
          title: Service name
  steps:
    - id: fetch
      name: Fetch template
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
    - id: publish
      name: Create repo
      action: publish:github
      input:
        repoUrl: github.com?repo=${{ parameters.name }}&owner=myorg
```

### TechDocs

TechDocs renders Markdown documentation from repos as browsable pages inside Backstage. It uses **MkDocs** under the hood. Annotate the entity with `backstage.io/techdocs-ref: dir:.` and place a `mkdocs.yml` in the repo root.

```yaml
# mkdocs.yml
site_name: Payments Service
nav:
  - Home: index.md
  - Architecture: architecture.md
docs_dir: docs
plugins:
  - techdocs-core
```

Docs are either built at read-time (dev mode) or pre-built and stored in object storage (S3/GCS) for production. Pre-built is the right default for production — it separates the build from the render and avoids build overhead at page load.

### Search

Full-text search across the catalog, TechDocs, and any plugin that contributes a search collator. Powered by Lunr (local) or Elasticsearch for production deployments.

## Entity model

| Kind        | Represents                                         |
|-------------|----------------------------------------------------|
| `Component` | A deployable unit: service, website, library       |
| `API`       | An interface exposed by a Component                |
| `Resource`  | Infrastructure a Component depends on (DB, queue)  |
| `System`    | A collection of related Components and Resources   |
| `Domain`    | A business domain grouping Systems                 |
| `Group`     | A team or organisational unit                      |
| `User`      | An individual                                      |
| `Template`  | A Scaffolder template                              |
| `Location`  | A pointer to where entities are defined            |

The relationships (`providesApis`, `consumesApis`, `dependsOn`, `partOf`) are what make the catalog navigable — you can trace dependencies across services and see who owns what.

## Architecture

```
Browser
  └─ Backstage frontend (React, @backstage/core-*)
       └─ Backstage backend (Node.js, Express)
            ├─ Catalog backend — entity processing pipeline
            ├─ Scaffolder backend — template execution
            ├─ TechDocs backend — doc building/serving
            ├─ Auth backend — OAuth providers
            └─ PostgreSQL — persistent state
```

The backend is a Node.js monolith you extend with plugins. Each plugin typically registers API routes and a database schema. The frontend is a React SPA — plugins register pages, sidebar entries, and entity tab content.

## Getting started

```bash
npx @backstage/create-app@latest
cd my-backstage-app
yarn dev          # starts both frontend (:3000) and backend (:7007)
```

This scaffolds a working app with the catalog, scaffolder, and TechDocs already wired up. SQLite is the default database for local dev; switch to PostgreSQL before running anything that matters.

### Helm chart (production)

```bash
helm repo add backstage https://backstage.github.io/charts
helm install backstage backstage/backstage -f values.yaml
```

The chart expects an `app-config.yaml` mounted as a ConfigMap and PostgreSQL credentials in a Secret.

## app-config.yaml

The main config file. Controls database, auth providers, integrations, and plugin configuration. Environment-specific overrides go in `app-config.production.yaml`.

```yaml
backend:
  baseUrl: https://backstage.example.com
  database:
    client: pg
    connection:
      host: ${POSTGRES_HOST}
      user: ${POSTGRES_USER}
      password: ${POSTGRES_PASSWORD}

integrations:
  github:
    - host: github.com
      token: ${GITHUB_TOKEN}

catalog:
  locations:
    - type: url
      target: https://github.com/myorg/catalog/blob/main/all.yaml

auth:
  providers:
    github:
      development:
        clientId: ${AUTH_GITHUB_CLIENT_ID}
        clientSecret: ${AUTH_GITHUB_CLIENT_SECRET}
```

## Plugin ecosystem

Backstage has 200+ community plugins. Common ones:

| Plugin | What it adds |
|---|---|
| `kubernetes` | Live cluster view scoped to an entity |
| `github-actions` | CI/CD run status on entity pages |
| `pagerduty` | On-call and incident status per service |
| `sonarqube` | Code quality metrics per component |
| `cost-insights` | Cloud cost breakdown by team |
| `lighthouse` | Web performance audits |
| `argo-cd` | ArgoCD sync status on entity pages |

Plugins are npm packages. Install, register in `packages/app/src/App.tsx` (frontend) and `packages/backend/src/index.ts` (backend).

## Adoption pattern

The catalog only becomes useful when it is comprehensive. The typical path:

1. Import existing services by pointing the catalog at repos that have `catalog-info.yaml`
2. Add a bulk-importer location (a `catalog-info.yaml` that lists other locations) to bootstrap coverage
3. Enforce `catalog-info.yaml` in new repos via the Scaffolder — templates create it automatically
4. Build TechDocs incrementally — services that already have `docs/` directories are easy wins
5. Add the Kubernetes plugin once catalog ownership is clean — it ties live cluster state to catalog entities

## Resources

- [Backstage.io](https://backstage.io/) — official docs
- [Backstage GitHub](https://github.com/backstage/backstage)
- [Backstage Helm chart](https://github.com/backstage/charts)
- [CNCF project page](https://www.cncf.io/projects/backstage/)
- [Plugin marketplace](https://backstage.io/plugins)
- [ADR-002: Backstage Software Catalog](https://github.com/backstage/backstage/blob/master/docs/architecture-decisions/adr002-default-catalog-file-format.md) — explains the entity model design
