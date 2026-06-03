---
title: "Build Systems — Ant, Maven, Gradle, Bazel"
date: 2026-06-03
draft: false
showReadingTime: false
---

The Java ecosystem has cycled through several generations of build tooling. Each generation solved real problems with the previous one and introduced new ones of its own.

---

## Ant

XML-based, imperative. You describe exactly what to do and in what order — compile these files, copy to this directory, package this jar. No conventions, no opinions.

**Strengths**: total control, predictable, easy to understand what any given build does.

**Weaknesses**: verbose, no built-in dependency management (Ivy was a separate add-on), and every project reinvents the same targets from scratch. Large Ant builds become hard to maintain.

Still found in older enterprise Java projects. Worth knowing to read and modify, less worth starting from scratch.

Used it. It was what it was — at least you always knew exactly what the build was doing.

---

## Maven

Convention over configuration. If your project follows the standard layout (`src/main/java`, `src/test/java`, etc.) most of the build is declared, not scripted. Dependency management built in via the POM and central repository.

**Maven 1**: the original. Repository model and POM concept introduced. Plugin system was limited and the build lifecycle was rigid.

**Maven 2**: major redesign. The lifecycle phases (validate → compile → test → package → install → deploy) that most people know. Dependency resolution significantly improved. This is the version that won widespread adoption.

**Maven 3**: incremental improvements over Maven 2. Better performance, improved parallel builds, polyglot POM support. Most Maven projects today run on 3.x.

**Strengths**: standardised project layout means any Maven project is immediately navigable; dependency management and central repository model that the whole ecosystem built on.

**Weaknesses**: XML is verbose for expressing logic; the lifecycle is powerful but opaque when things go wrong; plugin configuration gets unwieldy; multi-module builds are better than Ant but still awkward at scale.

Not a fan. All three weaknesses compound each other: the XML is painful to write, the lifecycle hides what is actually executing and where, and parent POM inheritance chains in multi-module projects make it genuinely hard to answer "what does this build actually do?" You end up cargo-culting POM snippets from Stack Overflow and hoping the lifecycle does what you think it does.

---

## Gradle

Groovy (and later Kotlin) DSL instead of XML. Keeps Maven's dependency management and repository model, drops the rigid lifecycle in favour of a task graph. Incremental builds — only re-runs tasks whose inputs changed.

Became the default for Android builds and has significant adoption in JVM projects that outgrew Maven.

**Strengths**: expressive build scripts; incremental and cached builds make large projects faster; Kotlin DSL gives type safety and IDE support; flexible enough to model non-standard builds.

**Weaknesses**: the flexibility is also the trap — Gradle builds vary wildly and can be hard to read; the Groovy DSL is easy to write badly; build times on cold caches can be slow; debugging task dependencies is non-trivial.

**Gradle vs Maven**: Maven wins on standardisation and predictability; Gradle wins on performance and flexibility. For a standard Java/Kotlin service with no unusual requirements, Maven is often the lower-maintenance choice. For Android, large monorepos, or complex multi-language builds, Gradle.

Gradle solves the XML problem but introduces a different one: the flexibility makes it very easy to get wrong. Every team ends up with a slightly different Gradle build, and reading someone else's is often just as opaque as Maven's lifecycle — just for different reasons. The problem of "what is this build actually doing" doesn't go away, it just changes shape.

The discipline that keeps Gradle manageable: **don't stuff everything into the Gradle build**. Gradle should compile, test, and package — that's it. Deployment logic, environment setup, Docker builds, release steps — those belong in scripts or other tools that are good at those things. Then wrap the whole thing in a Makefile that gives a single consistent entry point. `make build` calls Gradle. `make docker` calls a shell script. `make deploy` calls Helm. Gradle stays focused and readable; the Makefile is the seam that holds it together.

---

## SBT

The Scala Build Tool. Reactive, incremental compilation at the core. Not just a build tool — the REPL and interactive session are part of the workflow.

Heavy dependency on Scala itself; the build definition is Scala code. Powerful but a significant learning curve for anyone not already in the Scala ecosystem.

*Notes to follow.*

---

## Bazel & Bazelisk

Originally Google's internal build system (Blaze), open-sourced as Bazel. Hermetic builds — each action declares its inputs and outputs explicitly, no implicit filesystem access. Correctness and reproducibility guaranteed by construction.

Language-agnostic: rules exist for Java, Go, Python, C++, and others. Built for monorepos at scale — incremental and distributed builds, remote caching, remote execution.

**Bazelisk**: version manager for Bazel. Pin the Bazel version in `.bazelversion`, run `bazelisk` instead of `bazel` — it downloads and uses the pinned version automatically. Essential for team consistency.

**Strengths**: genuinely reproducible builds; scales to very large codebases; remote caching makes CI fast once warm.

**Weaknesses**: steep learning curve; rules ecosystem outside Google's own languages is less mature; significant setup cost; overkill for anything smaller than a large monorepo.

*Opinions to follow.*

---

## Choosing

| | Small project | Standard service | Large monorepo | Polyglot |
|--|--|--|--|--|
| **Ant** | Possible | Legacy only | No | No |
| **Maven** | Fine | Good default | Struggles | No |
| **Gradle** | Fine | Good | Better | Partial |
| **Bazel** | Overkill | Overkill | Strong | Strong |

Both Maven and Gradle have the same core problem: you end up not really knowing what your build is doing. Ant at least was honest about it. If forced to choose, Gradle is the least bad option — the DSL flexibility is a trap but it is a trap you can avoid with discipline, whereas Maven's lifecycle opacity and XML are just the deal regardless. For anything in the JVM ecosystem today the choice is usually made for you by the project or the framework — if you get to choose, Gradle with a simple build file and keep it that way.
