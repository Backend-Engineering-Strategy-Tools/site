---
title: "Code Quality & Architecture Analysis"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["sonarqube", "structure101", "code-quality", "static-analysis", "architecture", "java"]
---

Static analysis catches bugs and code smells before they reach production. Architecture analysis catches structural decay before the codebase becomes unmaintainable. SonarQube does the former; Structure101 does the latter.

## SonarQube

A code quality and security platform. SonarQube runs static analysis on your codebase and reports bugs, code smells, security hotspots, and test coverage in a web dashboard. It supports 30+ languages; the Java and Kotlin analysis is particularly deep. Integrates into CI pipelines via the SonarScanner — a quality gate can fail the build if new code introduces issues above a configured threshold.

```bash
# Run analysis (from project root, after configuring sonar-project.properties)
sonar-scanner \
  -Dsonar.projectKey=my-project \
  -Dsonar.sources=src/main \
  -Dsonar.tests=src/test \
  -Dsonar.host.url=https://sonarqube.example.com \
  -Dsonar.token=$SONAR_TOKEN
```

**Quality gates** define the conditions a project must meet — for example: no new critical bugs, test coverage on new code ≥ 80%, no new security hotspots unreviewed. A gate failure blocks the PR merge or CI pipeline. The built-in "Sonar Way" gate is a sensible default; most teams customise it over time.

SonarQube Community Edition is free and covers the core analysis features. Enterprise Edition adds branch analysis, portfolio views, and security reports.

## Structure101

An architecture analysis tool for Java projects. Structure101 visualises the dependency structure of a codebase as a layered graph and identifies violations — circular dependencies between packages, classes depending on layers they shouldn't reach, packages with too many inbound dependencies. It is particularly useful for large, long-lived Java codebases where architectural boundaries have eroded over time.

The key report is the **tangle** metric: a tangle is a group of packages with circular dependencies, and the tangle percentage measures how much of the codebase is affected. A clean architecture has zero tangles. Structure101 shows exactly which dependencies create each tangle, making it possible to systematically break them.

It integrates with build systems (Maven, Gradle) to enforce architecture rules in CI — build fails if the tangle percentage exceeds a threshold, or if a dependency violates a defined layering rule.

## Resources

- [SonarQube documentation](https://docs.sonarsource.com/sonarqube/)
- [SonarQube Community Edition](https://www.sonarsource.com/open-source-editions/sonarqube-community-edition/)
- [Structure101 documentation](https://structure101.com/documents/)
