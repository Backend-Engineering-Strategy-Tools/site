---
title: "IntelliJ IDEA"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["idea", "intellij", "jetbrains", "ide", "java", "kotlin"]
---

IntelliJ IDEA is JetBrains' Java and Kotlin IDE. It has the deepest language understanding of any Java IDE — code completion that reasons about types across the entire project, refactoring that updates all call sites, a debugger with expression evaluation, and a profiler integrated into the same window. The free Community Edition covers Java, Kotlin, Groovy, and Scala. The paid Ultimate Edition adds frameworks (Spring, Quarkus, Micronaut), database tools, HTTP client, and built-in support for web technologies.

## Key capabilities

**Refactoring** — rename a class and every reference in every file updates. Extract method, inline variable, move class to a different package, change method signature — all with full project-wide impact analysis before execution.

**Navigation** — `Cmd+Click` goes to declaration, `Cmd+B` shows all usages, `Cmd+E` opens recent files, `Cmd+Shift+F` searches across the entire project. In a large codebase, knowing where things are called from matters more than reading the code.

**Inspections** — real-time static analysis flags potential bugs, code style violations, and anti-patterns as you type, not at build time.

**Debugger** — set breakpoints, step through code, evaluate arbitrary expressions in the current scope, watch variables, set conditional breakpoints. Remote debugging attaches to a running JVM with a single click.

## Plugins

The plugin ecosystem extends IDEA significantly. Notable ones:
- **IdeaVim** — vim key bindings throughout the editor
- **Kubernetes** — YAML editing with schema validation and cluster connectivity
- **Database tools** (Ultimate) — query databases from within the IDE

## Remote development

IDEA supports JetBrains Gateway for remote development — the IDE UI runs locally but the indexing and execution happen on a remote machine or container. Useful for developing against large codebases on powerful remote hardware.

## Resources

- [IntelliJ IDEA documentation](https://www.jetbrains.com/help/idea/)
- [JetBrains IDE key bindings](https://www.jetbrains.com/help/idea/keyboard-shortcuts-and-mouse-reference.html)
