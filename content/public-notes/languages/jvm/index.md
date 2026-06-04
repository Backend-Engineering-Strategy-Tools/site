---
title: "JVM Languages"
date: 2026-06-03
draft: false
showReadingTime: false
layout: single
tags: ["jvm", "java", "kotlin", "groovy", "scala"]
---

JVM-hosted languages beyond Java. Each trades something to gain something, and each found a niche where the trade made sense.

Java was enough. It still is. The honest reason to know Groovy, Scala, and Kotlin is not that they are better — it is that the ecosystem puts them in front of you whether you choose them or not. Build tools, CI pipelines, and frameworks make that decision for you.

A practical tell: if the Java code you are reading starts to feel syntactically off — closures where you did not expect them, type inference that seems too aggressive, operators that should not be there — you are probably looking at Groovy, Scala, or Kotlin. Worth knowing enough to recognise each and get things done.

Also worth noting: Java itself has been catching up fast. Virtual threads, records, sealed classes, pattern matching, a faster release cadence — the gap between "Java" and "a more modern JVM language" has narrowed considerably. The case for leaving Java for something else on the JVM is weaker now than it was five years ago.

---

## Groovy

Dynamic, optionally typed JVM language with a syntax that is a superset of Java. Groovy code is often valid Java. The dynamic parts — closures, metaprogramming, GStrings — are what made it popular as a scripting and DSL language.

**Where you find it today:**
- **Gradle build scripts**: the Groovy DSL is the original Gradle scripting language (now being replaced by Kotlin DSL)
- **Jenkins pipelines**: Groovy is the language of Jenkinsfile declarative and scripted pipelines
- **Spock framework**: expressive BDD-style testing for JVM projects

Groovy's peak was the early Gradle/Jenkins era. Kotlin has taken over most of the "better Java scripting" use cases. Still found widely in CI/CD tooling — if you work with Jenkins or older Gradle builds, you will write Groovy.

Groovy shows up in Gradle builds and Jenkins pipelines. Know enough to read and modify it; not a reason to seek it out.

---

## Scala

Statically typed functional + OOP hybrid on the JVM. Strong type system, pattern matching, immutable data by default. Compiles to JVM bytecode and interops with Java libraries.

**Where you find it today:**
- **Apache Spark**: the dominant big data / data engineering platform is written in Scala and has a native Scala API
- **Akka**: actor model concurrency framework
- **Play Framework**: web framework, less common now
- **SBT**: build tool, build definition is Scala code

Scala has a reputation for complexity and a steep learning curve. The community split between Scala 2 and Scala 3 (Dotty) added friction. If you are working with Spark, you will encounter Scala. If you are not, the reasons to choose it over Kotlin or Java are narrower than they used to be. Another case where Java catching up makes the trade less obvious.

---

## Kotlin

JetBrains' answer to Java's verbosity. Statically typed, concise, null-safe by design. Full Java interop — Kotlin and Java can call each other in the same project. Official Android development language since 2017.

**Where you find it today:**
- Android development (the default)
- Spring Boot (first-class support since Spring 5)
- Gradle Kotlin DSL (replacing Groovy as the recommended build script language)
- Ktor — Kotlin-native web framework from JetBrains

Kotlin is what you reach for when you want Java but less of it. Coroutines handle async cleanly. The Kotlin DSL in Gradle gives type safety that the Groovy DSL could not.

Kotlin is the cleanest of the JVM alternatives — but again, Java has been closing the gap. Worth knowing if the project is already Kotlin; not a compelling reason to switch from Java.

---

## Jython

Python running on the JVM. Jython implements the Python language but executes on the JVM, meaning Python code can import and use Java classes directly.

Worth knowing it exists. In practice: Jython implements Python 2 (Python 3 support was never completed), which limits its relevance post-2020. Main use case was embedding Python scripting in Java applications. A few enterprise tools and test frameworks still use it.

If you need Python-JVM interop today, consider alternatives: GraalVM's polyglot API, or just making an HTTP boundary between a Python service and the JVM service.

---
