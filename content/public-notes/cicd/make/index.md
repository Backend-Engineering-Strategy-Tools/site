---
title: "Make — Task Runner Pattern"
date: 2026-06-03
draft: false
showReadingTime: false
---

Make predates most of the tooling in this notes collection by decades. Originally built to manage C compilation — track which source files changed, recompile only what's needed. The dependency graph and incremental execution model are genuinely elegant.

In modern use, Make is rarely used for what it was designed for. It is used as a **task runner**: a consistent interface that wraps whatever the project actually needs to do.

```makefile
.PHONY: build test lint deploy

build:
	docker build -t myapp .

test:
	docker run --rm myapp pytest

lint:
	docker run --rm myapp ruff check .

deploy:
	helm upgrade --install myapp ./chart
```

`make build`, `make test`, `make lint` — same interface regardless of what's underneath. New team member, CI pipeline, colleague's machine: one place to look.

---

## Why it still works

- Installed everywhere. No setup, no version to pin.
- Self-documenting entry point — `cat Makefile` tells you how to work with the project.
- Trivially wraps Docker, shell scripts, language-specific tools, cloud CLIs.
- Low overhead — it is just shell execution with a thin layer on top.

The fact that it is old is not a weakness. It is stable, understood, and available.

---

## The `.PHONY` problem

Make's native model assumes targets are files. `make build` checks if a file named `build` exists and skips the recipe if it does. `.PHONY` declares that a target is not a file, forcing it to always run.

Forgetting `.PHONY` is a classic Make footgun. Always declare task targets phony.

```makefile
.PHONY: build test lint clean
```

---

## Modern alternatives

**Just** (`Justfile`) — purpose-built task runner, not a build system. Cleaner syntax than Make, no file-dependency model to work around, better error messages. Cross-platform. Requires installation.

**Task** (`Taskfile.yml`) — YAML-based, similar goals to Just. More readable for people uncomfortable with Make syntax.

**Why still use Make then**: zero install cost, ubiquity in CI environments, and for many projects the `.PHONY` quirk is the only real friction. If the team already knows Make and the project isn't complex, switching to Just adds a dependency without solving a real problem.

If starting fresh on a project where the team is comfortable with the tooling choice, Just is the cleaner option.

It is there, it works. That is not faint praise — ubiquity and stability are real value. Every project gets a Makefile. New person joins, CI pipeline runs, colleague needs to build something: `make` is the answer and it requires no explanation.

---

## Pattern: shared interface over varied internals

The real value is not Make specifically — it is the pattern of having one consistent entry point regardless of what's underneath. Whether that is Make, Just, or a `scripts/` directory with a `run` script, the goal is the same: anyone (person or pipeline) can run the project without knowing its internals.

See also [Shared Tooling Images](/thinking/shared-tooling-images/) — the same principle applied to the tools themselves.

---

## Where this pattern applies

The signal that logic is leaking into the wrong place: when a tool's config format starts looking like a scripting language. That is the point to extract it into a script and wrap in Make.

**Build systems**
Gradle compiles, tests, and packages. Deployment logic, Docker builds, release steps → scripts. `make build` calls Gradle. `make docker` calls a script. `make deploy` calls Helm. See [Build Systems](/public-notes/cicd/build-systems/) for the full pattern.

**Infrastructure**
- **Terraform**: `terraform apply` does the infra. Environment selection, var file injection, state backend config, plan review → scripts. `make plan`, `make apply`.
- **Helm**: Helm packages and deploys. Cluster selection, secret fetching, values overrides → scripts. `make deploy`.
- **Ansible**: Ansible provisions. Inventory management, vault decryption, pre-flight checks → scripts. `make provision`.

**Testing**
Test runners run tests. Environment setup, test data seeding, coverage reporting → scripts. `make test` is the entry point regardless of whether it is pytest, jest, or go test underneath.

**Package managers**
A common npm/yarn trap: stuffing 20 scripts into `package.json` until it becomes a second build system. Keep `package.json` for dependency management. Orchestration belongs in Make.

**Static site / Hugo**
Hugo builds the site. PDF fetching, Docker wrapping, deploy steps → Makefile. The pattern this site already uses.
